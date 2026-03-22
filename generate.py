"""Retrieve textbook chunks and generate AMC-style MCQs."""

import json
import re

import chromadb
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
from openai import OpenAI

CHROMA_DIR = "chroma_db"

# (name, start_page, end_page)
CHAPTERS = {
    "1": ("The nature, scope and content of general practice", 57, 72),
    "2": ("Consulting skills", 73, 87),
    "3": ("Communication skills", 88, 102),
    "4": ("Counselling skills", 103, 130),
    "5": ("Health promotion and patient education", 131, 149),
    "6": ("Prevention in general practice", 150, 172),
    "7": ("Research and evidence-based medicine", 173, 191),
    "8": ("Inspection as a clinical skill", 192, 207),
    "9": ("A safe diagnostic model", 208, 230),
    "10": ("Depression", 231, 248),
    "11": ("Diabetes mellitus", 249, 291),
    "12": ("Drug and alcohol problems", 292, 331),
    "13": ("Anaemia", 332, 347),
    "14": ("Endocrine and metabolic disorders", 348, 378),
    "15": ("Spinal dysfunction", 379, 386),
    "16": ("Urinary tract infection", 387, 406),
    "17": ("Malignant disease", 407, 428),
    "18": ("Baffling viral and protozoal infections", 429, 462),
    "19": ("Baffling bacterial infections", 463, 491),
    "20": ("Infections of the central nervous system", 492, 506),
    "21": ("Connective tissue disease and the systemic vasculitides", 507, 530),
    "22": ("Neurological dilemmas", 531, 571),
    "23": ("Genetic conditions", 572, 618),
    "24": ("Abdominal pain", 619, 677),
    "25": ("Arthritis", 678, 731),
    "26": ("Anorectal disorders", 732, 753),
    "27": ("Thoracic back pain", 754, 784),
    "28": ("Low back pain", 785, 834),
    "29": ("Bruising and bleeding", 835, 858),
    "30": ("Chest pain", 859, 912),
    "31": ("Constipation", 913, 939),
    "32": ("Cough", 940, 975),
    "33": ("Deafness and hearing loss", 976, 999),
    "34": ("Diarrhoea", 1000, 1043),
    "35": ("Dizziness/vertigo", 1044, 1066),
    "36": ("Dyspepsia (indigestion)", 1067, 1096),
    "37": ("Dysphagia", 1097, 1107),
    "38": ("Dyspnoea", 1108, 1136),
    "39": ("The painful ear", 1137, 1170),
    "40": ("The red and tender eye", 1171, 1208),
    "41": ("Pain in the face", 1209, 1232),
    "42": ("Fever and chills", 1233, 1253),
    "43": ("Faints, fits and funny turns", 1254, 1288),
    "44": ("Haematemesis and melaena", 1289, 1295),
    "45": ("Headache", 1296, 1337),
    "46": ("Hoarseness", 1338, 1346),
    "47": ("Jaundice", 1347, 1386),
    "48": ("Nasal disorders", 1387, 1409),
    "49": ("Nausea and vomiting", 1410, 1426),
    "50": ("Neck lumps", 1427, 1439),
    "51": ("Neck pain", 1440, 1473),
    "52": ("Shoulder pain", 1474, 1502),
    "53": ("Pain in the arm and hand", 1503, 1541),
    "54": ("Hip, buttock and groin pain", 1542, 1571),
    "55": ("Pain in the leg", 1572, 1610),
    "56": ("The painful knee", 1611, 1657),
    "57": ("Pain in the foot and ankle", 1658, 1699),
    "58": ("Walking difficulty and leg swelling", 1700, 1715),
    "59": ("Palpitations", 1716, 1743),
    "60": ("Sleep disorders", 1744, 1766),
    "61": ("Sore mouth and tongue", 1767, 1792),
    "62": ("Sore throat", 1793, 1814),
    "63": ("Tiredness/fatigue", 1815, 1831),
    "64": ("The unconscious patient", 1832, 1851),
    "65": ("Urinary disorders", 1852, 1880),
    "66": ("Visual failure", 1881, 1911),
    "67": ("Weight change", 1912, 1935),
    "68": ("Depression and other mood disorders", 1936, 1945),
    "69": ("The disturbed patient", 1946, 1985),
    "70": ("Anxiety disorders", 1986, 2005),
    "71": ("Difficult behaviours", 2006, 2025),
    "72": ("Allergic disorders including hay fever", 2026, 2044),
    "73": ("Asthma", 2045, 2073),
    "74": ("Chronic obstructive pulmonary disease", 2074, 2091),
    "75": ("Cardiovascular disease", 2092, 2100),
    "76": ("Chronic heart failure", 2101, 2118),
    "77": ("Hypertension", 2119, 2154),
    "78": ("Dyslipidaemia", 2155, 2165),
    "79": ("Chronic kidney disease", 2166, 2184),
    "80": ("Obesity", 2185, 2197),
    "81": ("Osteoporosis", 2198, 2207),
    "82": ("Chronic pain", 2208, 2229),
    "83": ("An approach to the child", 2230, 2251),
    "84": ("Specific problems of children", 2252, 2288),
    "85": ("Surgical problems in children", 2289, 2314),
    "86": ("Common childhood infectious diseases (including skin eruptions)", 2315, 2350),
    "87": ("Behavioural and developmental issues and disorders in children", 2351, 2376),
    "88": ("Child abuse", 2377, 2395),
    "89": ("Emergencies in children", 2396, 2434),
    "90": ("Adolescent health", 2435, 2451),
    "91": ("Cervical cancer screening", 2452, 2471),
    "92": ("Family planning", 2472, 2491),
    "93": ("Breast disorders", 2492, 2534),
    "94": ("Abnormal uterine bleeding", 2535, 2551),
    "95": ("Lower abdominal and pelvic pain in women", 2552, 2579),
    "96": ("Premenstrual syndrome", 2580, 2587),
    "97": ("The menopause", 2588, 2606),
    "98": ("Vaginal discharge", 2607, 2627),
    "99": ("Vulvar disorders", 2628, 2646),
    "100": ("Basic antenatal care", 2647, 2667),
    "101": ("Postnatal care", 2668, 2687),
    "102": ("Men's health: an overview", 2688, 2696),
    "103": ("Scrotal pain", 2697, 2707),
    "104": ("Inguinoscrotal lumps", 2708, 2732),
    "105": ("Disorders of the penis", 2733, 2751),
    "106": ("Disorders of the prostate", 2752, 2773),
    "107": ("The subfertile couple", 2774, 2793),
    "108": ("Sexual health", 2794, 2815),
    "109": ("Sexually transmitted infections", 2816, 2844),
    "110": ("Intimate partner violence and sexual assault", 2845, 2858),
    "111": ("A diagnostic and management approach to skin problems", 2859, 2883),
    "112": ("Pruritus", 2884, 2911),
    "113": ("Common skin problems", 2912, 2970),
    "114": ("Acute skin eruptions", 2971, 3003),
    "115": ("Skin ulcers", 3004, 3026),
    "116": ("Common lumps and bumps", 3027, 3076),
    "117": ("Pigmented skin lesions", 3077, 3097),
    "118": ("Hair disorders", 3098, 3122),
    "119": ("Nail disorders", 3123, 3149),
    "120": ("Emergency care", 3150, 3201),
    "121": ("Stroke and transient ischaemic attacks", 3202, 3217),
    "122": ("Thrombosis and thromboembolism", 3218, 3232),
    "123": ("Common skin wounds and foreign bodies", 3233, 3267),
    "124": ("Common fractures and dislocations", 3268, 3325),
    "125": ("The elderly patient", 3326, 3361),
    "126": ("End of life/palliative care", 3362, 3383),
    "127": ("The health of Aboriginal and Torres Strait Islander peoples", 3384, 3404),
    "128": ("Refugee health", 3405, 3419),
    "129": ("Travellers' health and tropical medicine", 3420, 3785),
}


def resolve_topic(user_input: str) -> tuple[str, str | None]:
    """Resolve user input to (topic_name, chapter_number or None).

    Handles 'Chapter 6', 'ch6', '6', or free text like 'chest pain'.
    """
    text = user_input.strip()

    match = re.match(r"^(?:ch(?:apter)?\s*)?(\d+)$", text, re.IGNORECASE)
    if match:
        num = match.group(1)
        if num in CHAPTERS:
            return CHAPTERS[num][0], num
        print(f"  Chapter {num} not found (valid: 1-129).")
        return None, None

    return text, None


def get_index() -> VectorStoreIndex:
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_or_create_collection("murtagh")
    vector_store = ChromaVectorStore(chroma_collection=collection)
    return VectorStoreIndex.from_vector_store(vector_store)


def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    return client.get_or_create_collection("murtagh")


def retrieve_chunks_by_chapter(chapter_num: str, n: int = 20) -> str:
    """Retrieve chunks from a specific chapter by page range."""
    name, start_page, end_page = CHAPTERS[chapter_num]
    collection = get_collection()
    results = collection.get(
        where={"$and": [{"page": {"$gte": start_page}}, {"page": {"$lte": end_page}}]},
        include=["documents"],
        limit=n,
    )
    if not results["documents"]:
        return ""
    return "\n---\n".join(results["documents"])


def retrieve_chunks_by_topic(index: VectorStoreIndex, topic: str, n: int = 15) -> str:
    """Retrieve top-n relevant chunks for a free-text topic via semantic search."""
    retriever = index.as_retriever(similarity_top_k=n)
    nodes = retriever.retrieve(topic)
    return "\n---\n".join(node.get_content() for node in nodes)


MCQ_PROMPT = """You are an Australian Medical Council (AMC) exam question writer.

Using ONLY the following textbook excerpts, generate {n} multiple choice questions suitable for AMC MCQ exam preparation.

Each question must:
- Present a clinical vignette (patient age, sex, presenting complaint, relevant history/findings)
- Have exactly 4 options (A, B, C, D)
- Have exactly one correct answer
- Include a brief explanation of why the correct answer is right
- Be directly relevant to the topic: {topic}
- Prefer treatment and management questions (e.g. "What is the most appropriate management?", "Which treatment should be initiated?") over purely diagnostic questions. Some diagnostic questions are acceptable for variety, but the majority should test management decisions.

Return your response as JSON:
{{
  "questions": [
    {{
      "stem": "A 45-year-old male presents with...",
      "option_a": "...",
      "option_b": "...",
      "option_c": "...",
      "option_d": "...",
      "correct_answer": "A",
      "explanation": "..."
    }}
  ]
}}

TEXTBOOK EXCERPTS:
---
{context}
---"""


def retrieve_context(index: VectorStoreIndex, topic: str, chapter_num: str | None = None) -> str:
    """Retrieve textbook chunks for a topic. Returns prompt-ready text."""
    if chapter_num:
        return retrieve_chunks_by_chapter(chapter_num, n=20)
    else:
        return retrieve_chunks_by_topic(index, topic, n=15)


def generate_mcqs(
    index: VectorStoreIndex, topic: str, chapter_num: str | None = None, n: int = 5, context: str | None = None
) -> list[dict]:
    """Generate n AMC-style MCQs for a topic."""
    if context is None:
        context = retrieve_context(index, topic, chapter_num)

    if not context.strip():
        print("  No relevant content found. Try a different topic.")
        return []

    client = OpenAI()
    messages = [
        {"role": "system", "content": "You generate AMC exam questions in JSON format."},
        {"role": "user", "content": MCQ_PROMPT.format(n=n, topic=topic, context=context)},
    ]

    for attempt in range(2):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=messages,
        )
        try:
            data = json.loads(response.choices[0].message.content)
            return data["questions"]
        except (json.JSONDecodeError, KeyError):
            if attempt == 0:
                print("  Failed to parse generated questions. Retrying...")

    print("  Could not generate questions. Try a different topic.")
    return []
