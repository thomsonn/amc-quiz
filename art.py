"""Cute Unicode block art for the AMC Study TUI.

Art mapped to Murtagh's General Practice, 7th edition chapter layout.
Style: kawaii/charming — simple bold shapes, little faces, sparkles.
Each piece is 20-24 chars wide × 8-10 lines tall.
"""

# ── Category Art ────────────────────────────────────────────────────────────

CATEGORY_ART = {
    "general": """\
[bright_cyan]      ┏━━━━━━┓
      ┃ ≋≋≋≋ ┃
      ┃ ≋≋≋≋ ┃✦
    ╭─┨ ≋≋≋≋ ┠─╮
    │ ┗━━━━━━┛ │
    │  ╰─ˆˆ─╯  │
    │  ·today· │
    ╰──────────╯[/bright_cyan]
   [dim]· general practice ·[/dim]""",

    "cardio": """\
[red]       ╭╮ ╭╮
      ╭╯╰─╯╰╮
      │ ♥  ♥ │
       ╲ ωˊ ╱
        ╲  ╱[/red]\
[bright_red]
    ┄╮╱╲╱╲╱╲╱╲╭┄
    ┄╯         ╰┄[/bright_red]
[dim]     · lub-dub ·[/dim]""",

    "respiratory": """\
[bright_cyan]        ╱▔╲
    ┈┈╱    ╲┈┈
   ╭─╱──────╲─╮
   │╱ ░░░░░░ ╲│
   │░░╭ˆωˆ╮░░░│
   │░░╰───╯░░░│
   ╰─╮░░░░░╭──╯
     ╰┬───┬╯
      │   │[/bright_cyan]
[dim]    · breathe ·[/dim]""",

    "neuro": """\
[bright_magenta]     ╭─━━━━─╮
    ╭╯⣀⡀⣀⡀⣀╰╮
    │⠋⠉⠋⠉⠋⠉⠋│
    │⣿⡇⣿⡇⣿⡇⣿│
    ╰╮⠉⠋⠉⠋⠉⠋╭╯
     ╰─╮˘ω˘╭─╯
       ┃    ┃
       ╰┄┄┄╯[/bright_magenta]
[dim]    · thinking ·[/dim]""",

    "msk": """\
[bright_white]       ╭─╮
      ╱ ◠ ╲
     ╱  ▿  ╲
    ─┤     ├─
     │╭───╮│
     ││ ✦ ││
     ╰┤   ├╯
    ─┬╯   ╰┬─
     │     │[/bright_white]
[dim]   · skeleton ·[/dim]""",

    "gi": """\
[bright_yellow]    ╭──────────╮
    │ ╭──────╮ │
    │ │ ·  · │ │
    │ ╰╮    ╭╯ │
    │  ╰╮  ╭╯  │
    │ ╭─╯╭─╯╮  │
    │ ╰╮ ╰╮ ╰╮ │
    ╰──╰──╰──╰─╯[/bright_yellow]
[dim]    · gurgles ·[/dim]""",

    "paeds": """\
[bright_green]      ╭────╮
      │・ω・│
      ╰─┬┬─╯
     ╭──┘╰──╮
     │ tiny! │
    ╭┴───────┴╮
    │ ◦  ✦  ◦ │
    ╰─╮─────╭─╯
      ╰─╥─╥─╯[/bright_green]""",

    "dermatology": """\
[bright_yellow]   ╭─────────────╮
   │ ◌  ◌     ◌  │
   │    ◌  ◌     │
   │ ◌     ╭───╮ │
   │   ◌  ╭╯✦°╰╮│
   │  ◌   │ °✦ ││
   │    ◌  ╰───╯ │
   ╰─────────────╯[/bright_yellow]
[dim]    · skin deep ·[/dim]""",

    "womens_health": """\
[bright_magenta]        ✧
      ╭─╨─╮
     ╭╯   ╰╮
     │ ♀ ˆˆ │
     ╰╮ ╰╯ ╭╯
    ╭─╰╮  ╭╯─╮
    │  ╰────╯  │
    ╰──────────╯[/bright_magenta]
[dim]  · women's health ·[/dim]""",

    "mens_health": """\
[bright_blue]        ✧
      ╭─╨─╮
     ╭╯   ╰╮
     │ ♂ ˆˆ │
     ╰╮ ╰╯ ╭╯
    ╭─╰╮  ╭╯─╮
    │  ╰────╯  │
    ╰──────────╯[/bright_blue]
[dim]  · men's health ·[/dim]""",

    "mental_health": """\
[bright_cyan]       ☁  ☁
     ╭──────╮
    ╭╯  ╭╮  ╰╮
    │  ╭╯╰╮  │
    │  │✦✦│  │
    │  ╰╮╭╯  │
    ╰╮  ╰╯  ╭╯
     ╰──☾───╯[/bright_cyan]
[dim]    · be kind ·[/dim]""",

    "ent_eyes": """\
[bright_green]    ╭──────────╮
    │ ◉      ◉ │
    │    ╱╲    │
    │   ╱  ╲   │
    │  ╰════╯  │
    │  ♪    ♪  │
    │   ╰──╯   │
    ╰──────────╯[/bright_green]""",

    "infectious": """\
[bright_red]    ╱╲  ✦  ╱╲
   ╱··╲   ╱··╲
  │·>_<·│·ˆoˆ·│
   ╲··╱   ╲··╱
    ╲╱  ✦  ╲╱
   ╱╲      ╱╲
  │·ˆ_ˆ·│·>.<·│
   ╲╱      ╲╱[/bright_red]
[dim]    · bugs! ·[/dim]""",

    "renal": """\
[bright_yellow]  ╭───╮     ╭───╮
  │╲░░│     │░░╱│
  │ ╲░│     │░╱ │
  │ ░╲│     │╱░ │
  │ ░░╲     ╱░░ │
  │ ░░ │   │ ░░ │
  ╰──┬─╯   ╰─┬──╯
     ╰───┬───╯[/bright_yellow]
[dim]    · filter ·[/dim]""",

    "endocrine": """\
[bright_magenta]     ╭━━━━━╮
     ┃ ╭─╮ ┃
     ┃ │✦│ ┃
     ┃ ╰┬╯ ┃
     ╰━━┿━━╯
      ╭─┴─╮
    ··│ ˘˘ │··
      ╰───╯[/bright_magenta]
[dim]    · glands ·[/dim]""",

    "haematology": """\
[red]       ╭───╮
     ╭╯     ╰╮
    ╭╯  ╭─╮  ╰╮
    │   │○│   │
    ╰╮  ╰─╯  ╭╯
     ╰╮     ╭╯
      ╰╮ ✦ ╭╯
       ╰───╯[/red]
[dim]    · blood ·[/dim]""",

    "emergency": """\
[bright_red]     ┏━━━┓
    ━┫ ✦ ┣━
     ┣━━━┫
    ━┫ ✦ ┣━
     ┗━━━┛
   ⚡ ⚡ ⚡ ⚡ ⚡
    !! STAT !![/bright_red]""",

    "oncology": """\
[bright_magenta]       ·  ✧  ·
      ╭──────╮
     ╭╯ ╭──╮ ╰╮
     │  │🔬│  │
     │  ╰──╯  │
     ╰╮  ✦✦ ╭╯
      ╰──────╯
     ✧ · ·· · ✧[/bright_magenta]""",

    "palliative": """\
[bright_white]    ·  · ✧ ·  ·
     ╭────────╮
     │ ╭╮  ☾  │
     │ ╰╯     │
     │   ✧    │
     │ gentle │
     ╰────────╯
    ·  ✧  ·  ✧  ·[/bright_white]""",

    "public_health": """\
[bright_green]   ╭─╮ ╭─╮ ╭─╮
   │·│ │·│ │·│
   ╰┬╯ ╰┬╯ ╰┬╯
    ╰───┬┴───╯
    ╭───┴───╮
    │  ✦✦✦  │
    │people!│
    ╰───────╯[/bright_green]""",
}

# ── Chapter → Category mapping ──────────────────────────────────────────────
# Murtagh's General Practice, 7th edition

CHAPTER_CATEGORIES: dict[str, str] = {
    # General practice & clinical skills (1-9)
    "1": "general", "2": "general", "3": "general", "4": "general",
    "5": "general", "6": "general", "7": "general", "8": "general",
    "9": "general",
    # Depression (10)
    "10": "mental_health",
    # Diabetes (11)
    "11": "endocrine",
    # Drug & alcohol (12)
    "12": "mental_health",
    # Anaemia (13)
    "13": "haematology",
    # Endocrine & metabolic (14)
    "14": "endocrine",
    # Spinal dysfunction (15)
    "15": "msk",
    # UTI (16)
    "16": "renal",
    # Malignant disease (17)
    "17": "oncology",
    # Viral & protozoal infections (18)
    "18": "infectious",
    # Bacterial infections (19)
    "19": "infectious",
    # CNS infections (20)
    "20": "infectious",
    # Connective tissue & vasculitides (21)
    "21": "msk",
    # Neurological dilemmas (22)
    "22": "neuro",
    # Genetic conditions (23)
    "23": "general",
    # Abdominal pain (24)
    "24": "gi",
    # Arthritis (25)
    "25": "msk",
    # Anorectal (26)
    "26": "gi",
    # Thoracic back pain (27)
    "27": "msk",
    # Low back pain (28)
    "28": "msk",
    # Bruising & bleeding (29)
    "29": "haematology",
    # Chest pain (30)
    "30": "cardio",
    # Constipation (31)
    "31": "gi",
    # Cough (32)
    "32": "respiratory",
    # Deafness (33)
    "33": "ent_eyes",
    # Diarrhoea (34)
    "34": "gi",
    # Dizziness/vertigo (35)
    "35": "neuro",
    # Dyspepsia (36)
    "36": "gi",
    # Dysphagia (37)
    "37": "gi",
    # Dyspnoea (38)
    "38": "respiratory",
    # Painful ear (39)
    "39": "ent_eyes",
    # Red/tender eye (40)
    "40": "ent_eyes",
    # Face pain (41)
    "41": "neuro",
    # Fever & chills (42)
    "42": "infectious",
    # Faints, fits, funny turns (43)
    "43": "neuro",
    # Haematemesis & melaena (44)
    "44": "gi",
    # Headache (45)
    "45": "neuro",
    # Hoarseness (46)
    "46": "ent_eyes",
    # Nasal disorders (48)
    "48": "ent_eyes",
    # Nausea & vomiting (49)
    "49": "gi",
    # Neck lumps (50)
    "50": "oncology",
    # Neck pain (51)
    "51": "msk",
    # Shoulder pain (52)
    "52": "msk",
    # Arm & hand pain (53)
    "53": "msk",
    # Hip, buttock, groin pain (54)
    "54": "msk",
    # Leg pain (55)
    "55": "msk",
    # Knee pain (56)
    "56": "msk",
    # Foot & ankle pain (57)
    "57": "msk",
    # Walking difficulty & leg swelling (58)
    "58": "msk",
    # Palpitations (59)
    "59": "cardio",
    # Sleep disorders (60)
    "60": "mental_health",
    # Sore mouth & tongue (61)
    "61": "ent_eyes",
    # Sore throat (62)
    "62": "ent_eyes",
    # Tiredness/fatigue (63)
    "63": "general",
    # Unconscious patient (64)
    "64": "emergency",
    # Urinary disorders (65)
    "65": "renal",
    # Visual failure (66)
    "66": "ent_eyes",
    # Weight change (67)
    "67": "endocrine",
    # Depression & mood disorders (68)
    "68": "mental_health",
    # Disturbed patient (69)
    "69": "mental_health",
    # Anxiety disorders (70)
    "70": "mental_health",
    # Difficult behaviours (71)
    "71": "mental_health",
    # Allergic disorders (72)
    "72": "respiratory",
    # Asthma (73)
    "73": "respiratory",
    # COPD (74)
    "74": "respiratory",
    # Cardiovascular disease (75)
    "75": "cardio",
    # Chronic heart failure (76)
    "76": "cardio",
    # Hypertension (77)
    "77": "cardio",
    # Dyslipidaemia (78)
    "78": "cardio",
    # Chronic kidney disease (79)
    "79": "renal",
    # Obesity (80)
    "80": "endocrine",
    # Osteoporosis (81)
    "81": "msk",
    # Chronic pain (82)
    "82": "msk",
    # Approach to the child (83)
    "83": "paeds",
    # Specific problems of children (84)
    "84": "paeds",
    # Surgical problems in children (85)
    "85": "paeds",
    # Childhood infectious diseases (86)
    "86": "paeds",
    # Behavioural/developmental in children (87)
    "87": "paeds",
    # Child abuse (88)
    "88": "paeds",
    # Emergencies in children (89)
    "89": "paeds",
    # Adolescent health (90)
    "90": "paeds",
    # Cervical cancer screening (91)
    "91": "womens_health",
    # Family planning (92)
    "92": "womens_health",
    # Breast disorders (93)
    "93": "womens_health",
    # Abnormal uterine bleeding (94)
    "94": "womens_health",
    # Lower abdominal/pelvic pain in women (95)
    "95": "womens_health",
    # Premenstrual syndrome (96)
    "96": "womens_health",
    # Menopause (97)
    "97": "womens_health",
    # Vaginal discharge (98)
    "98": "womens_health",
    # Vulvar disorders (99)
    "99": "womens_health",
    # Basic antenatal care (100)
    "100": "womens_health",
    # Postnatal care (101)
    "101": "womens_health",
    # Men's health overview (102)
    "102": "mens_health",
    # Scrotal pain (103)
    "103": "mens_health",
    # Inguinoscrotal lumps (104)
    "104": "mens_health",
    # Disorders of the penis (105)
    "105": "mens_health",
    # Disorders of the prostate (106)
    "106": "mens_health",
    # Subfertile couple (107)
    "107": "general",
    # Sexual health (108)
    "108": "general",
    # STIs (109)
    "109": "infectious",
    # Intimate partner violence (110)
    "110": "general",
    # Skin diagnostic approach (111)
    "111": "dermatology",
    # Pruritus (112)
    "112": "dermatology",
    # Common skin problems (113)
    "113": "dermatology",
    # Acute skin eruptions (114)
    "114": "dermatology",
    # Skin ulcers (115)
    "115": "dermatology",
    # Common lumps & bumps (116)
    "116": "dermatology",
    # Pigmented skin lesions (117)
    "117": "dermatology",
    # Hair disorders (118)
    "118": "dermatology",
    # Nail disorders (119)
    "119": "dermatology",
    # Emergency care (120)
    "120": "emergency",
    # Stroke & TIA (121)
    "121": "neuro",
    # Thrombosis & thromboembolism (122)
    "122": "haematology",
    # Skin wounds & foreign bodies (123)
    "123": "emergency",
    # Fractures & dislocations (124)
    "124": "emergency",
    # Elderly patient (125)
    "125": "palliative",
    # End of life/palliative care (126)
    "126": "palliative",
    # Aboriginal & Torres Strait Islander health (127)
    "127": "public_health",
    # Refugee health (128)
    "128": "public_health",
    # Travellers' health & tropical medicine (129)
    "129": "public_health",
}

# ── Results Art ─────────────────────────────────────────────────────────────

RESULTS_ART = {
    "high": """\
[bright_yellow]        ✦ ★ ✦
      ╭───────╮
      │ ◠   ◠ │
      │  ╰▽╯  │
      ├───────┤
      │✦✦✦✦✦✦✦│
      ╰───────╯[/bright_yellow]
[dim]    · brilliant ·[/dim]""",

    "mid": """\
[bright_cyan]      ╭───────╮
      │ ·   · │
      │  ╰─╯  │
      ├───────┤
      │ ✧ ✧ ✧ │
      ╰───────╯[/bright_cyan]
[dim]     · solid ·[/dim]""",

    "low": """\
[bright_white]      ╭───────╮
      │ ·   · │
      │  ───  │
      ├───────┤
      │  ╭─╮  │
      │  │✦│  │
      ╰──╰─╯──╯[/bright_white]
[dim]   · keep going ·[/dim]""",
}

# ── Fallback ────────────────────────────────────────────────────────────────

FALLBACK_ART = """\
[bright_cyan]      ╭──────╮
     ╭╯  ✦✦  ╰╮
     │  ╭──╮  │
     │  │♥ │  │
     │  ╰──╯  │
     ╰╮  ··  ╭╯
      ╰──────╯[/bright_cyan]"""


# ── Lookup functions ────────────────────────────────────────────────────────

def get_art(topic_name: str = "", chapter_num: str | None = None) -> str:
    """Return topic-appropriate art for loading screens."""
    if chapter_num and chapter_num in CHAPTER_CATEGORIES:
        category = CHAPTER_CATEGORIES[chapter_num]
        return CATEGORY_ART.get(category, FALLBACK_ART)
    # Try keyword matching on topic name for free-text topics
    topic_lower = topic_name.lower()
    keyword_map = {
        "cardio": ["heart", "chest pain", "cardio", "hypertension", "blood pressure", "palpitation", "angina"],
        "respiratory": ["lung", "breath", "cough", "asthma", "copd", "respiratory", "dyspnoea", "allerg"],
        "neuro": ["brain", "neuro", "headache", "seizure", "stroke", "dizz", "vertigo", "nerve", "face pain"],
        "msk": ["bone", "joint", "back pain", "knee", "shoulder", "hip", "arthritis", "fracture", "spinal",
                "neck pain", "arm", "hand", "leg pain", "foot", "ankle", "osteopor", "pain"],
        "gi": ["stomach", "bowel", "abdom", "liver", "diarrh", "constip", "nausea", "vomit", "dyspepsia",
               "dysphagia", "jaundice", "anorectal", "melaena"],
        "paeds": ["child", "paed", "infant", "baby", "adolesc", "neonat"],
        "dermatology": ["skin", "rash", "dermat", "eczema", "pruritus", "nail", "hair", "ulcer", "lesion"],
        "womens_health": ["pregnan", "menstrual", "ovari", "cervic", "breast", "menopause", "uterine",
                          "vaginal", "vulvar", "antenatal", "postnatal", "premenstrual"],
        "mens_health": ["prostate", "testicular", "scrotal", "penis", "erectile"],
        "mental_health": ["depress", "anxiety", "mental", "psych", "mood", "sleep", "insomnia", "behav"],
        "ent_eyes": ["ear", "eye", "nose", "throat", "deaf", "visual", "hoarse", "nasal"],
        "infectious": ["infect", "virus", "bacteri", "fever", "malaria", "hiv", "sti", "sexually transmit"],
        "renal": ["kidney", "renal", "urinary", "urin"],
        "endocrine": ["diabetes", "thyroid", "endocrin", "metabol", "obes", "weight"],
        "haematology": ["blood", "anaemia", "bleed", "bruis", "thromb", "coagul"],
        "emergency": ["emergency", "unconscious", "resuscit", "trauma"],
        "oncology": ["cancer", "malignan", "tumour", "tumor", "lump"],
        "palliative": ["palliative", "end of life", "elderly", "aged care", "dying"],
        "public_health": ["aboriginal", "refugee", "travel", "tropical", "indigenous"],
    }
    for category, keywords in keyword_map.items():
        if any(kw in topic_lower for kw in keywords):
            return CATEGORY_ART.get(category, FALLBACK_ART)
    return FALLBACK_ART


def get_results_art(pct: float) -> str:
    """Return score-appropriate art for results screen."""
    if pct >= 80:
        return RESULTS_ART["high"]
    elif pct >= 40:
        return RESULTS_ART["mid"]
    else:
        return RESULTS_ART["low"]