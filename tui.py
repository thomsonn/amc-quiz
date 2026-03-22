"""AMC Study Tool — Textual TUI."""

from __future__ import annotations

from dotenv import load_dotenv

load_dotenv()

import random
import threading

from openai import OpenAI
from textual import work
from textual.app import App
from textual.containers import Container, VerticalScroll
from textual.message import Message
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    LoadingIndicator,
    Static,
)

from art import get_art, get_results_art
from db import (
    count_review_questions,
    get_due_topics,
    get_or_create_topic,
    get_progress,
    get_review_questions,
    init_db,
    save_attempt,
    save_question,
    update_last_attempt_argued,
    update_question_after_attempt,
    update_topic_after_quiz,
)
from generate import CHAPTERS, adjudicate_argument, generate_mcqs, get_index, resolve_topic, retrieve_context
from quiz import is_uncertain, parse_answer, score_answer
from review import build_review_quiz


# ── QuestionBank ────────────────────────────────────────────────────────────


class QuestionBank:
    """Thread-safe container for progressively-loaded questions."""

    def __init__(self, initial: list[dict] | None = None, context: str | None = None):
        self._questions: list[dict] = list(initial or [])
        self._lock = threading.Lock()
        self._done = threading.Event()
        self.context: str | None = context

    def extend(self, qs: list[dict]):
        with self._lock:
            self._questions.extend(qs)

    def __len__(self):
        with self._lock:
            return len(self._questions)

    def __getitem__(self, idx):
        with self._lock:
            return self._questions[idx]

    def available(self) -> int:
        with self._lock:
            return len(self._questions)

    def mark_done(self):
        self._done.set()

    @property
    def is_done(self) -> bool:
        return self._done.is_set()


# ── HomeScreen ───────────────────────────────────────────────────────────────


class HomeScreen(Screen):
    BINDINGS = [("q", "quit", "Quit")]

    MENU_ITEMS = [
        ("study", "Study a Topic"),
        ("review", "Review Due Topics"),
        ("progress", "View Progress"),
        ("qa", "Q&A Mode"),
        ("quit", "Quit"),
    ]

    def compose(self):
        yield Header()
        with Container(id="menu-container"):
            yield Static("AMC Study Tool", id="app-title")
            yield ListView(
                *[ListItem(Label(label), name=action) for action, label in self.MENU_ITEMS],
                id="home-menu",
            )
            yield Static("", id="due-count")
        yield Footer()

    def on_screen_resume(self):
        self._update_due_count()

    def on_mount(self):
        self._update_due_count()
        self.query_one("#home-menu", ListView).focus()

    def _update_due_count(self):
        due = get_due_topics()
        label = self.query_one("#due-count", Static)
        if due:
            label.update(f"{len(due)} topic(s) due for review")
        else:
            label.update("")

    def on_list_view_selected(self, event: ListView.Selected):
        action = event.item.name
        actions = {
            "study": lambda: self.app.push_screen(StudyScreen()),
            "review": lambda: self.app.push_screen(ReviewScreen()),
            "progress": lambda: self.app.push_screen(ProgressScreen()),
            "qa": lambda: self.app.push_screen(QAScreen()),
            "quit": lambda: self.app.exit(),
        }
        if action in actions:
            actions[action]()

    def action_quit(self):
        self.app.exit()


# ── StudyScreen ──────────────────────────────────────────────────────────────


class StudyScreen(Screen):
    BINDINGS = [("escape", "go_back", "Back")]

    def __init__(self):
        super().__init__()
        self._filter_timer = None

    def compose(self):
        yield Header()
        with Container(id="study-container"):
            yield Static("Study a Topic", id="app-title")
            yield Input(
                placeholder='Type a topic (e.g. "chest pain") or filter chapters...',
                id="study-input",
            )
            yield ListView(id="chapter-list")
        yield Footer()

    def on_mount(self):
        self._rebuild_list("")
        self.query_one("#study-input", Input).focus()

    def _rebuild_list(self, filter_text: str):
        lv = self.query_one("#chapter-list", ListView)
        ft = filter_text.lower()
        items = []
        for num, (name, _, _) in CHAPTERS.items():
            if ft and ft not in name.lower() and ft not in num:
                continue
            items.append(ListItem(Label(f"{num:>3}. {name}"), name=num))
        lv.clear()
        lv.extend(items)

    def on_key(self, event):
        focused = self.focused
        if isinstance(focused, Input) and event.key == "down":
            lv = self.query_one("#chapter-list", ListView)
            if lv.children:
                event.stop()
                lv.focus()
                lv.index = 0
        elif isinstance(focused, (ListView, ListItem)) and event.key == "up":
            lv = self.query_one("#chapter-list", ListView)
            if lv.index == 0:
                event.stop()
                self.query_one("#study-input", Input).focus()

    def on_input_changed(self, event: Input.Changed):
        if event.input.id != "study-input":
            return
        if self._filter_timer is not None:
            self._filter_timer.stop()
        self._filter_timer = self.set_timer(0.15, lambda: self._rebuild_list(event.value))

    def on_input_submitted(self, event: Input.Submitted):
        if event.input.id != "study-input":
            return
        text = event.value.strip()
        if not text:
            return
        topic_name, chapter_num = resolve_topic(text)
        if not topic_name:
            self.notify("Chapter not found (valid: 1-129)", severity="error")
            return
        self.app.push_screen(QuizLoadingScreen(topic_name, chapter_num))

    def on_list_view_selected(self, event: ListView.Selected):
        chapter_num = event.item.name
        if chapter_num and chapter_num in CHAPTERS:
            name = CHAPTERS[chapter_num][0]
            self.app.push_screen(QuizLoadingScreen(name, chapter_num))

    def action_go_back(self):
        self.app.pop_screen()


# ── QuizLoadingScreen ────────────────────────────────────────────────────────


class QuizLoadingScreen(Screen):
    """Shown while generating/waiting for the next question.

    Two modes:
    - Initial: no *bank* — generates the first question, then switches to QuestionScreen.
    - Waiting: *bank* provided — just shows art until QuestionsReady arrives.
    """

    BINDINGS = [("escape", "go_back", "Cancel")]

    def __init__(
        self,
        topic_name: str,
        chapter_num: str | None = None,
        review_mode: bool = False,
        # waiting-mode params (between questions)
        bank: QuestionBank | None = None,
        next_idx: int = 0,
        total_score: float = 0.0,
    ):
        super().__init__()
        self.topic_name = topic_name
        self.chapter_num = chapter_num
        self.review_mode = review_mode
        self.bank = bank
        self.next_idx = next_idx
        self.total_score = total_score

    def compose(self):
        if self.bank is not None:
            label = "Generating next question"
        elif self.review_mode:
            label = "Preparing review"
        else:
            label = "Generating question"
        art_text = get_art(self.topic_name, self.chapter_num)
        yield Header()
        with Container(id="loading-container"):
            yield Static(art_text, id="loading-art")
            yield Static(f'{label} on "[b]{self.topic_name}[/b]"...', id="loading-text")
            yield LoadingIndicator()
        yield Footer()

    def on_mount(self):
        if self.bank is None:
            self._generate()
        elif self.next_idx < self.bank.available() or self.bank.is_done:
            # Questions arrived before we mounted — proceed immediately
            self._proceed()

    def on_questions_ready(self, event: QuestionsReady):
        """Handle background questions arriving (waiting mode)."""
        if self.bank is not None:
            self._proceed()

    def _proceed(self):
        if self.next_idx < self.bank.available():
            self.app.switch_screen(
                QuestionScreen(
                    self.topic_name,
                    self.bank,
                    self.next_idx,
                    self.total_score,
                    review_mode=self.review_mode,
                )
            )
        elif self.bank.is_done:
            self.app.switch_screen(
                QuizResultsScreen(self.topic_name, self.total_score, len(self.bank))
            )

    @work(thread=True)
    def _generate(self):
        try:
            index = self.app.index
            if index is None:
                self.app.call_from_thread(self._on_failure, "Index not loaded yet. Please wait.")
                return

            if self.review_mode:
                context = retrieve_context(index, self.topic_name, self.chapter_num)
                questions = self._build_review(index)
                if not questions:
                    self.app.call_from_thread(self._on_failure, "No questions generated. Try a different topic.")
                    return
                bank = QuestionBank(questions, context=context)
                bank.mark_done()
                self.app.call_from_thread(self._on_success, bank, None)
                return

            # Progressive: retrieve context once, generate 1 question fast
            context = retrieve_context(index, self.topic_name, self.chapter_num)
            if not context or not context.strip():
                self.app.call_from_thread(self._on_failure, "No relevant content found. Try a different topic.")
                return

            first = generate_mcqs(index, self.topic_name, chapter_num=self.chapter_num, n=1, context=context)
            if not first:
                self.app.call_from_thread(self._on_failure, "No questions generated. Try a different topic.")
                return

            bank = QuestionBank(first, context=context)
            self.app.call_from_thread(self._on_success, bank, context, first)
        except Exception as e:
            self.app.call_from_thread(self._on_failure, str(e))

    def _build_review(self, index) -> list[dict]:
        topic = get_or_create_topic(self.topic_name)
        due_qs = get_review_questions(topic["id"])
        old_qs, num_new = build_review_quiz(due_qs)

        new_qs = []
        if num_new > 0:
            new_qs = generate_mcqs(index, self.topic_name, chapter_num=self.chapter_num, n=num_new, existing_questions=old_qs)
            for q in new_qs:
                q["is_review"] = False

        combined = old_qs + new_qs
        random.shuffle(combined)
        return combined

    def _on_success(self, bank: QuestionBank, context: str | None, first: list[dict] | None = None):
        self.app.switch_screen(
            QuestionScreen(self.topic_name, bank, current_idx=0, total_score=0.0, review_mode=self.review_mode)
        )
        # Kick off background generation of remaining questions on the App
        if context is not None:
            self.app.generate_remaining(bank, self.topic_name, self.chapter_num, context, first or [])

    def _on_failure(self, message: str):
        self.notify(message, severity="error")
        self.app.pop_screen()

    def action_go_back(self):
        self.app.pop_screen()


# ── QuestionScreen ───────────────────────────────────────────────────────────


class QuestionsReady(Message):
    """Posted by App when background question generation completes."""
    pass


class QuestionScreen(Screen):
    BINDINGS = [("escape", "go_home", "Quit Quiz")]

    show_feedback: reactive[bool] = reactive(False)
    selected_option: reactive[int] = reactive(-1)

    OPTION_LETTERS = ["A", "B", "C", "D"]

    def __init__(
        self,
        topic_name: str,
        bank: QuestionBank,
        current_idx: int,
        total_score: float,
        review_mode: bool = False,
    ):
        super().__init__()
        self.topic_name = topic_name
        self.bank = bank
        self.current_idx = current_idx
        self.total_score = total_score
        self.review_mode = review_mode
        self.q = bank[current_idx]
        self.topic_row = get_or_create_topic(topic_name)
        self._score = 0.0
        self._arguing = False
        self._argue_used = False
        self._qid: int | None = None
        self._user_answer: str = ""

    def compose(self):
        total = 5 if not self.bank.is_done else len(self.bank)
        idx = self.current_idx + 1

        header_text = f"Question {idx}/{total}  —  {self.topic_name}"
        if self.review_mode:
            tag = "Review" if self.q.get("is_review") else "New"
            header_text += f"  ·  [dim]{tag}[/dim]"

        bar_width = 20
        filled = round(idx / total * bar_width)
        bar_text = "█" * filled + "░" * (bar_width - filled)

        yield Header()
        with Container(id="question-container"):
            yield Static(header_text, id="q-header")
            yield Static(bar_text, id="progress-bar")
            yield Static(self.q["stem"], id="q-stem")
            yield Static(f"[b]A)[/b] {self.q['option_a']}", classes="option", id="opt-0")
            yield Static(f"[b]B)[/b] {self.q['option_b']}", classes="option", id="opt-1")
            yield Static(f"[b]C)[/b] {self.q['option_c']}", classes="option", id="opt-2")
            yield Static(f"[b]D)[/b] {self.q['option_d']}", classes="option", id="opt-3")
            yield Input(placeholder="A-D or explain in your own words", id="answer-input")
            yield Static("", id="feedback")
            yield Static("", id="explanation")
            yield Static("", id="nav-hint")
        yield Footer()

    def on_mount(self):
        self.query_one("#answer-input", Input).focus()

    def watch_selected_option(self, old: int, new: int):
        for i in range(4):
            opt = self.query_one(f"#opt-{i}", Static)
            if i == new:
                opt.add_class("highlighted")
            else:
                opt.remove_class("highlighted")
        inp = self.query_one("#answer-input", Input)
        if new >= 0:
            inp.value = self.OPTION_LETTERS[new]

    def on_input_changed(self, event: Input.Changed):
        if event.input.id == "answer-input" and not self.show_feedback:
            # If user edits the text manually, clear the arrow highlight
            val = event.value.strip().upper()
            if val in self.OPTION_LETTERS:
                self.selected_option = self.OPTION_LETTERS.index(val)
            else:
                self.selected_option = -1

    def on_input_submitted(self, event: Input.Submitted):
        if event.input.id == "answer-input" and self._arguing:
            self._submit_argument(event.value)
        elif event.input.id == "answer-input" and not self.show_feedback:
            self._submit_answer(event.value)

    def _submit_answer(self, raw: str):
        raw = raw.strip()
        if not raw:
            return
        primary, secondary = parse_answer(raw)
        if not primary:
            self.notify("Could not find A/B/C/D in your answer. Try again.", severity="warning")
            return

        uncertain = is_uncertain(raw, secondary)
        self._score = score_answer(primary, secondary, uncertain, self.q["correct_answer"])
        correct_letter = self.q["correct_answer"].upper()

        # Build feedback text
        feedback_el = self.query_one("#feedback", Static)
        feedback_el.remove_class("correct", "incorrect", "partial")

        if primary == correct_letter:
            if uncertain:
                feedback_el.update(f"Correct! The answer is {correct_letter}. (but uncertain — half credit: {self._score})")
                feedback_el.add_class("partial")
            else:
                feedback_el.update(f"Correct! ({self._score})")
                feedback_el.add_class("correct")
        elif secondary and secondary == correct_letter:
            feedback_el.update(
                f"Your first answer {primary} was wrong — the answer is {correct_letter}. (quarter credit: {self._score})"
            )
            feedback_el.add_class("partial")
        else:
            feedback_el.update(f"Incorrect. The answer is {correct_letter}. ({self._score})")
            feedback_el.add_class("incorrect")

        # Explanation
        if self.q.get("explanation"):
            self.query_one("#explanation", Static).update(self.q["explanation"])

        # Save to DB
        if self.q.get("is_review"):
            qid = self.q["id"]
        else:
            qid = save_question(self.topic_row["id"], self.q)
        save_attempt(qid, raw, self._score)
        update_question_after_attempt(qid, self._score)
        self._qid = qid
        self._user_answer = raw

        # Disable input and remove focus so Enter key bubbles to on_key
        inp = self.query_one("#answer-input", Input)
        inp.disabled = True
        self.set_focus(None)
        self.show_feedback = True

        is_last = self.bank.is_done and self.current_idx >= len(self.bank) - 1
        argue_hint = "  |  [b]a[/b] to argue" if self._score < 1.0 and not self._argue_used else ""
        if is_last:
            hint = f"Press [b]Enter[/b] for results  |  [b]d[/b] to discuss{argue_hint}  |  [b]Escape[/b] to quit"
        else:
            hint = f"Press [b]Enter[/b] for next question  |  [b]d[/b] to discuss{argue_hint}  |  [b]Escape[/b] to quit"
        self.query_one("#nav-hint", Static).update(hint)

    def on_key(self, event):
        if not self.show_feedback:
            if event.key == "up":
                event.prevent_default()
                if self.selected_option <= 0:
                    self.selected_option = 3
                else:
                    self.selected_option -= 1
            elif event.key == "down":
                event.prevent_default()
                if self.selected_option >= 3:
                    self.selected_option = 0
                else:
                    self.selected_option += 1
            return
        if event.key == "enter":
            event.prevent_default()
            self._next()
        elif event.key == "d":
            event.prevent_default()
            self._discuss()
        elif event.key == "a" and self._score < 1.0 and not self._arguing and not self._argue_used:
            event.prevent_default()
            self._start_argue()

    def _next(self):
        new_total = self.total_score + self._score
        next_idx = self.current_idx + 1

        # All done and no more questions
        if self.bank.is_done and next_idx >= len(self.bank):
            self.app.switch_screen(
                QuizResultsScreen(self.topic_name, new_total, len(self.bank))
            )
            return

        # Next question available
        if next_idx < self.bank.available():
            self.app.switch_screen(
                QuestionScreen(
                    self.topic_name,
                    self.bank,
                    next_idx,
                    new_total,
                    review_mode=self.review_mode,
                )
            )
            return

        # Not ready yet — show loading screen while waiting
        self.app.switch_screen(
            QuizLoadingScreen(
                self.topic_name,
                bank=self.bank,
                next_idx=next_idx,
                total_score=new_total,
                review_mode=self.review_mode,
            )
        )

    def _start_argue(self):
        """Enter argue mode — re-enable input for the user to type their argument."""
        self._arguing = True
        inp = self.query_one("#answer-input", Input)
        inp.value = ""
        inp.placeholder = "Type your argument..."
        inp.disabled = False
        inp.focus()
        self.query_one("#nav-hint", Static).update("Type your argument and press [b]Enter[/b]  |  [b]Escape[/b] to cancel")

    def _submit_argument(self, text: str):
        text = text.strip()
        if not text:
            return
        inp = self.query_one("#answer-input", Input)
        inp.disabled = True
        self.set_focus(None)
        self.query_one("#nav-hint", Static).update("Evaluating your argument...")
        self._run_adjudication(text)

    @work(thread=True)
    def _run_adjudication(self, argument: str):
        try:
            context = self.bank.context or ""
            result = adjudicate_argument(
                question=self.q,
                student_answer=self._user_answer,
                argument=argument,
                context=context,
            )
            self.app.call_from_thread(self._on_adjudication_result, result, argument)
        except Exception as e:
            self.app.call_from_thread(self._on_adjudication_result, {
                "accepted": False,
                "explanation": f"Error: {e}",
            }, argument)

    def _on_adjudication_result(self, result: dict, argument: str):
        self._arguing = False
        self._argue_used = True
        feedback_el = self.query_one("#feedback", Static)
        explanation_el = self.query_one("#explanation", Static)
        accepted = bool(result.get("accepted"))
        original_score = self._score
        new_score = 1.0 if accepted else self._score

        if accepted:
            self._score = 1.0
            feedback_el.remove_class("incorrect", "partial")
            feedback_el.add_class("correct")
            feedback_el.update(f"Argument accepted! Score updated to {self._score}")
            if self._qid:
                update_last_attempt_argued(self._qid, self._score, argument)
                update_question_after_attempt(self._qid, self._score)
        else:
            feedback_el.update(f"Argument not accepted. ({self._score})")
            if self._qid:
                ruling = result.get("explanation", "")
                update_last_attempt_argued(self._qid, self._score, f"[rejected] {argument} — {ruling}")

        explanation_el.update(result.get("explanation", ""))

        # Restore nav hints
        is_last = self.bank.is_done and self.current_idx >= len(self.bank) - 1
        if is_last:
            hint = "Press [b]Enter[/b] for results  |  [b]d[/b] to discuss  |  [b]Escape[/b] to quit"
        else:
            hint = "Press [b]Enter[/b] for next question  |  [b]d[/b] to discuss  |  [b]Escape[/b] to quit"
        self.query_one("#nav-hint", Static).update(hint)

    def _discuss(self):
        context = (
            f"Question: {self.q['stem']}\n"
            f"A) {self.q['option_a']}\nB) {self.q['option_b']}\n"
            f"C) {self.q['option_c']}\nD) {self.q['option_d']}\n"
            f"Correct answer: {self.q['correct_answer']}\n"
            f"Explanation: {self.q.get('explanation', '')}"
        )
        self.app.push_screen(QAScreen(seed_context=context, seed_topic=self.topic_name))

    def action_go_home(self):
        if self._arguing:
            # Cancel argue mode instead of quitting
            self._arguing = False
            inp = self.query_one("#answer-input", Input)
            inp.disabled = True
            inp.placeholder = "A-D or explain in your own words"
            self.set_focus(None)
            # Restore nav hints
            is_last = self.bank.is_done and self.current_idx >= len(self.bank) - 1
            argue_hint = "  |  [b]a[/b] to argue" if self._score < 1.0 and not self._argue_used else ""
            if is_last:
                hint = f"Press [b]Enter[/b] for results  |  [b]d[/b] to discuss{argue_hint}  |  [b]Escape[/b] to quit"
            else:
                hint = f"Press [b]Enter[/b] for next question  |  [b]d[/b] to discuss{argue_hint}  |  [b]Escape[/b] to quit"
            self.query_one("#nav-hint", Static).update(hint)
            return
        self.app.switch_screen(HomeScreen())


# ── QuizResultsScreen ────────────────────────────────────────────────────────


class QuizResultsScreen(Screen):
    BINDINGS = [("enter", "go_home", "Return Home"), ("escape", "go_home", "Return Home")]

    def __init__(self, topic_name: str, total_score: float, total_questions: int):
        super().__init__()
        self.topic_name = topic_name
        self.total_score = total_score
        self.total_questions = total_questions

    def compose(self):
        pct = (self.total_score / self.total_questions) * 100 if self.total_questions else 0

        yield Header()
        with Container(id="results-container"):
            yield Static(get_results_art(pct), id="results-art")
            yield Static(f'Quiz Complete: "{self.topic_name}"', id="results-title")
            yield Static(
                f"{self.total_score:.1f}/{self.total_questions} ({pct:.0f}%)",
                id="score-line",
            )

            result = update_topic_after_quiz(self.topic_name, pct)
            if result:
                new_box, next_date = result
                yield Static(f"Box: now at [b]{new_box}[/b]", classes="result-detail")
                yield Static(f"Next review: [b]{next_date}[/b]", classes="result-detail")

            yield Static("Press [b]Enter[/b] to return home", id="return-hint")
        yield Footer()

    def action_go_home(self):
        self.app.switch_screen(HomeScreen())


# ── ReviewScreen ─────────────────────────────────────────────────────────────


class ReviewScreen(Screen):
    BINDINGS = [("escape", "go_back", "Back")]

    def __init__(self):
        super().__init__()
        all_due = get_due_topics()
        self.due_topics = []
        self._q_counts: list[int] = []
        for t in all_due:
            cnt = count_review_questions(t["id"])
            self.due_topics.append(t)
            self._q_counts.append(cnt)

    def compose(self):
        items = []
        for i, t in enumerate(self.due_topics):
            cnt = self._q_counts[i]
            q_label = f", {cnt} Qs due" if cnt else ""
            items.append(
                ListItem(
                    Label(f"{t['name']}  (Box {t['box']}{q_label})"),
                    id=f"due-{i}",
                    name=str(i),
                )
            )

        yield Header()
        with Container(id="review-container"):
            yield Static("Topics Due for Review", id="app-title")
            yield ListView(*items, id="review-list")
            if not self.due_topics:
                yield Static("No topics due for review. Come back later!", id="empty-message")
        yield Footer()

    def on_mount(self):
        if self.due_topics:
            self.query_one("#review-list", ListView).focus()
        else:
            self.query_one("#review-list", ListView).display = False

    def on_list_view_selected(self, event: ListView.Selected):
        idx = int(event.item.name)
        if 0 <= idx < len(self.due_topics):
            topic = self.due_topics[idx]
            self.app.push_screen(QuizLoadingScreen(topic["name"], review_mode=True))

    def action_go_back(self):
        self.app.pop_screen()


# ── ProgressScreen ───────────────────────────────────────────────────────────


class ProgressScreen(Screen):
    BINDINGS = [("escape", "go_back", "Back")]

    def compose(self):
        yield Header()
        with Container(id="progress-container"):
            yield Static("Study Progress", id="app-title")
            yield DataTable(id="progress-table")
            yield Static("", id="totals")
        yield Footer()

    def on_mount(self):
        table = self.query_one("#progress-table", DataTable)
        table.add_columns("Topic", "Box", "Score", "Next Review")
        table.cursor_type = "row"

        rows = get_progress()
        grand_score = 0.0
        grand_total = 0
        for r in rows:
            att = r["total_attempts"] or 0
            sc = r["total_score"] or 0.0
            grand_score += sc
            grand_total += att
            pct = f"{sc:.1f}/{att} ({sc / att * 100:.0f}%)" if att > 0 else "—"
            table.add_row(r["name"], str(r["box"]), pct, r["next_review_date"])

        totals = self.query_one("#totals", Static)
        if grand_total > 0:
            totals.update(
                f"Total: {grand_score:.1f}/{grand_total} ({grand_score / grand_total * 100:.0f}%)"
            )
        elif not rows:
            totals.update("No study history yet. Start with Study a Topic!")

    def action_go_back(self):
        self.app.pop_screen()


# ── QAScreen ─────────────────────────────────────────────────────────────────


class QAScreen(Screen):
    BINDINGS = [("escape", "go_back", "Back")]

    def __init__(self, seed_context: str | None = None, seed_topic: str | None = None):
        super().__init__()
        self.seed_context = seed_context
        self.seed_topic = seed_topic
        self.query_engine = None

    def compose(self):
        yield Header()
        with Container(id="qa-container"):
            if self.seed_topic:
                yield Static(f"Discuss: {self.seed_topic}", id="qa-title")
            else:
                yield Static("Q&A — Ask about Murtagh's", id="qa-title")
            yield Static("Loading index...", id="index-placeholder")
            yield VerticalScroll(id="chat-log")
            yield Input(placeholder="Ask a question...", id="qa-input")
        yield Footer()

    def on_mount(self):
        chat_log = self.query_one("#chat-log")
        qa_input = self.query_one("#qa-input", Input)

        if self.app.index is not None:
            self._on_index_ready()
        else:
            chat_log.display = False
            qa_input.disabled = True

        if self.seed_context:
            chat_log.mount(Static(f"[dim]{self.seed_context}[/dim]", classes="a-msg"))

    def watch_index_ready(self, ready: bool):
        if ready:
            self._on_index_ready()

    def _on_index_ready(self):
        placeholder = self.query_one("#index-placeholder", Static)
        placeholder.display = False
        chat_log = self.query_one("#chat-log")
        chat_log.display = True
        qa_input = self.query_one("#qa-input", Input)
        qa_input.disabled = False
        qa_input.focus()
        self.query_engine = self.app.index.as_query_engine(similarity_top_k=5)

    def on_input_submitted(self, event: Input.Submitted):
        if event.input.id != "qa-input":
            return
        question = event.value.strip()
        if not question:
            return
        event.input.value = ""
        chat_log = self.query_one("#chat-log")
        chat_log.mount(Static(f"[b]Q:[/b] {question}", classes="q-msg"))
        event.input.disabled = True
        self._run_query(question)

    @work(thread=True)
    def _run_query(self, question: str):
        try:
            if self.query_engine is None:
                self.app.call_from_thread(self._on_query_failure, "Index not ready")
                return
            response = self.query_engine.query(question)
            self.app.call_from_thread(self._on_query_success, str(response))
        except Exception as e:
            self.app.call_from_thread(self._on_query_failure, str(e))

    def _on_query_success(self, answer: str):
        chat_log = self.query_one("#chat-log")
        chat_log.mount(Static(f"[b]A:[/b] {answer}", classes="a-msg"))
        qa_input = self.query_one("#qa-input", Input)
        qa_input.disabled = False
        qa_input.focus()
        chat_log.scroll_end()

    def _on_query_failure(self, message: str):
        self.notify(f"Query failed: {message}", severity="error")
        qa_input = self.query_one("#qa-input", Input)
        qa_input.disabled = False
        qa_input.focus()

    def action_go_back(self):
        self.app.pop_screen()


# ── App ──────────────────────────────────────────────────────────────────────


class AMCStudyApp(App):
    TITLE = "AMC Study Tool"
    CSS_PATH = "amc_study.tcss"

    index_ready: reactive[bool] = reactive(False)

    def __init__(self):
        super().__init__()
        self.index = None

    def on_mount(self):
        self.theme = "catppuccin-mocha"
        init_db()
        self.push_screen(HomeScreen())
        self._load_index()

    @work(thread=True)
    def _load_index(self):
        try:
            idx = get_index()
            self.app.call_from_thread(self._set_index, idx)
        except Exception as e:
            self.app.call_from_thread(
                self.notify, f"Failed to load index: {e}", severity="error"
            )

    def _set_index(self, idx):
        self.index = idx
        self.index_ready = True

    @work(thread=True)
    def generate_remaining(self, bank: QuestionBank, topic: str, chapter_num: str | None, context: str, existing_questions: list[dict] | None = None):
        """Generate remaining questions in background after first question is shown."""
        try:
            remaining = generate_mcqs(self.index, topic, chapter_num=chapter_num, n=4, context=context, existing_questions=existing_questions)
            if remaining:
                bank.extend(remaining)
            bank.mark_done()
            # Notify active QuestionScreen if it exists
            self.call_from_thread(self._notify_questions_ready)
        except Exception:
            bank.mark_done()
            self.call_from_thread(self._notify_questions_ready)

    def _notify_questions_ready(self):
        screen = self.screen
        if isinstance(screen, (QuestionScreen, QuizLoadingScreen)):
            screen.post_message(QuestionsReady())

    def watch_index_ready(self, ready: bool):
        if ready:
            self.notify("Index loaded", severity="information")
            # Propagate to any active QAScreen
            screen = self.screen
            if isinstance(screen, QAScreen):
                screen._on_index_ready()


if __name__ == "__main__":
    AMCStudyApp().run()
