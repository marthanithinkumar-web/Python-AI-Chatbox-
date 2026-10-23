"""Simple NLP pipeline: tokenization, stop-word filtering and intent matching."""
import re
from collections import Counter

STOP_WORDS = set("""a an the is are am was were to for of in on at and or i you me my we our it this that please can could tell about what when where how do does be with from your""".split())
SYNONYMS = {
    "test": "exam", "tests": "exam", "examinations": "exam", "paper": "exam",
    "tuition": "fees", "payment": "fees", "charges": "fees",
    "books": "library", "book": "library", "librarian": "library",
    "schedule": "timetable", "routine": "timetable", "class": "timetable",
    "presence": "attendance", "absent": "attendance", "present": "attendance",
    "subjects": "courses", "course": "courses", "branch": "courses",
    "phone": "contact", "email": "contact", "reach": "contact",
}
INTENTS = {
    "greeting": {"hello", "hi", "hey", "greetings", "morning", "evening"},
    "courses": {"course", "courses", "subject", "subjects", "branch", "semester", "syllabus"},
    "exam": {"exam", "date", "dates", "result", "results", "hall", "ticket"},
    "attendance": {"attendance", "percentage", "minimum", "shortage", "present", "absent"},
    "fees": {"fees", "payment", "charges", "scholarship", "refund"},
    "library": {"library", "book", "books", "borrow", "return", "reading"},
    "timetable": {"timetable", "schedule", "class", "classes", "period", "lab"},
    "contact": {"contact", "office", "phone", "email", "reach", "address"},
    "help": {"help", "options", "topics", "support", "menu"},
    "thanks": {"thanks", "thank", "appreciate", "great"},
    "about": {"who", "campusbot", "yourself", "purpose"},
}
RESPONSES = {
    "greeting": "Hello! I'm CampusBot. Ask me about courses, exams, attendance, fees, library, timetable, or contact details.",
    "courses": "Course and syllabus information varies by programme and semester. Check your department's official syllabus or academic portal for the current subject list.",
    "exam": "For confirmed exam dates, hall tickets, and results, check the official college examination portal or notice board. I don't invent dates.",
    "attendance": "Attendance requirements follow your college's current academic regulations. Check the student handbook or ask your class coordinator.",
    "fees": "For current fee amounts, payment deadlines, refunds, or scholarships, consult the official accounts office or scholarship notice. Never share payment credentials in chat.",
    "library": "For book availability, issue/return dates, and library hours, contact the college library or check its official catalogue.",
    "timetable": "Class and laboratory timetables can change. Refer to the latest department notice or official student portal.",
    "contact": "Please use the contact details published on your college's official website or contact your department office.",
    "help": "I can discuss courses, exams, attendance, fees, library, timetable, contact information, and this chatbot. Type history to view saved conversations or exit to stop.",
    "thanks": "You're welcome! Let me know if you have another college-related question.",
    "about": "I'm CampusBot, a student project demonstrating basic NLP with Python. I match words to intents and use local responses; I am not an official college service.",
}
FALLBACK = "I couldn't confidently match that question. Try courses, exams, attendance, fees, library, timetable, or contact. Type help to see options."


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.casefold())


def preprocess(text: str) -> list[str]:
    return [SYNONYMS.get(w, w) for w in tokenize(text) if w not in STOP_WORDS]


def classify_intent(text: str) -> str | None:
    words = preprocess(text)
    scores = {intent: sum(word in keywords for word in words)
              for intent, keywords in INTENTS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else None


def generate_response(text: str) -> str:
    return RESPONSES.get(classify_intent(text), FALLBACK)


def most_common_words(text: str, limit: int = 5) -> list[tuple[str, int]]:
    return Counter(preprocess(text)).most_common(limit)
