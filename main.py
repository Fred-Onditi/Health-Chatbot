import json
from pathlib import Path

DATA_DIR = Path(__file__).parent

STOPWORDS = {
    "what", "is", "are", "the", "a", "an", "how", "do", "does",
    "can", "i", "my", "should", "to", "for", "of", "in", "on",
    "why", "when", "where", "will", "it", "and", "or", "have",
    "has", "be", "with", "about", "me", "you", "your",
}


def load_json(filename: str):
    """Load a JSON file from the same folder as this script."""
    with open(DATA_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)


def is_emergency(text: str, emergency_resources: dict) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in emergency_resources["emergency_keywords"])


def get_emergency_reply(emergency_resources: dict) -> str:
    lines = [emergency_resources["emergency_message"], ""]
    for hotline in emergency_resources["hotlines"][:4]:
        lines.append(f"- {hotline['service']} ({hotline['region']}): {hotline['number']}")
    return "\n".join(lines)


def find_answer(question: str, faq: list) -> str:
    """Find the FAQ entry with the most overlapping meaningful words."""
    question_words = set(question.lower().split()) - STOPWORDS

    best_match = None
    best_score = 0

    for item in faq:
        item_words = set(item["question"].lower().split()) - STOPWORDS
        score = len(question_words & item_words)
        if score > best_score:
            best_score = score
            best_match = item

    if best_match and best_score > 0:
        return f"[{best_match['category']}] {best_match['answer']}"

    return (
        "I don't have a specific answer for that. "
        "Try asking about sleep, nutrition, exercise, stress, or a symptom like headache."
    )


def find_symptom(question: str, symptom_info: list):
    lowered = question.lower()
    for item in symptom_info:
        if item["symptom"].lower() in lowered:
            return item
    return None


def format_symptom(item: dict) -> str:
    return (
        f"{item['symptom']}\n\n"
        f"Possible causes: {', '.join(item['possible_causes'])}\n\n"
        f"Self-care: {', '.join(item['self_care'])}\n\n"
        f"See a doctor if: {', '.join(item['see_doctor_if'])}\n\n"
        "This is general information only, not a diagnosis."
    )


def find_wellness_tips(question: str, wellness_tips: list):
    lowered = question.lower()
    for block in wellness_tips:
        topic = block["topic"].lower()
        if topic in lowered or any(word in lowered for word in topic.split()):
            return block
    return None


def format_wellness_tips(block: dict) -> str:
    tips = "\n".join(f"- {tip}" for tip in block["tips"])
    return f"Tips for {block['topic']}:\n{tips}"


def get_help_text() -> str:
    return (
        "You can ask:\n"
        "- Health questions (sleep, nutrition, exercise, stress)\n"
        "- About a symptom (headache, fever, cough, sore throat)\n"
        "- For wellness tips (sleep, nutrition, study & focus)\n"
        "- Type 'symptoms' to list available symptoms\n"
        "- Type 'topics' to list wellness topics\n"
        "- Type 'quit' to exit"
    )


def list_symptoms(symptom_info: list) -> str:
    names = ", ".join(item["symptom"] for item in symptom_info)
    return f"Available symptoms: {names}"


def list_topics(wellness_tips: list) -> str:
    names = ", ".join(block["topic"] for block in wellness_tips)
    return f"Available wellness topics: {names}"


def get_bot_reply(question: str, health_faq, symptom_info, wellness_tips, emergency_resources) -> str:
    if is_emergency(question, emergency_resources):
        return get_emergency_reply(emergency_resources)

    symptom = find_symptom(question, symptom_info)
    if symptom:
        return format_symptom(symptom)

    tips = find_wellness_tips(question, wellness_tips)
    if tips:
        return format_wellness_tips(tips)

    return find_answer(question, health_faq)


def main():
    health_faq = load_json("health_faq.json")
    symptom_info = load_json("symptom_info.json")
    wellness_tips = load_json("wellness_tips.json")
    emergency_resources = load_json("emergency_resources.json")

    print("Health Chatbot")
    print(emergency_resources["disclaimer"])
    print("\nType 'help' for examples or 'quit' to exit.\n")

    while True:
        question = input("You: ").strip()
        if question.lower() in ("quit", "exit"):
            print("Bot: Goodbye. Take care of your health.")
            break
        if not question:
            continue

        lowered = question.lower()

        if lowered == "help":
            print(f"Bot: {get_help_text()}\n")
            continue

        if lowered == "symptoms":
            print(f"Bot: {list_symptoms(symptom_info)}\n")
            continue

        if lowered == "topics":
            print(f"Bot: {list_topics(wellness_tips)}\n")
            continue

        answer = get_bot_reply(question, health_faq, symptom_info, wellness_tips, emergency_resources)
        print(f"Bot: {answer}\n")


if __name__ == "__main__":
    main()
