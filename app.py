from pathlib import Path

import streamlit as st

from main import (
    get_bot_reply,
    get_help_text,
    list_symptoms,
    list_topics,
    load_json,
)

APP_DIR = Path(__file__).parent
EXAMPLE_QUESTIONS_PATH = APP_DIR / "example_questions.txt"


@st.cache_data
def load_data():
    return {
        "health_faq": load_json("health_faq.json"),
        "symptom_info": load_json("symptom_info.json"),
        "wellness_tips": load_json("wellness_tips.json"),
        "emergency_resources": load_json("emergency_resources.json"),
    }


@st.cache_data
def load_example_questions() -> tuple[str, ...]:
    with open(EXAMPLE_QUESTIONS_PATH, "r", encoding="utf-8") as file:
        return tuple(line.strip() for line in file if line.strip())

DOCTOR_WARNING = (
    "\n\n---\n"
    "⚠️ **Educational purposes only.** I am not a doctor and this is not "
    "medical advice, diagnosis, or treatment. If you are feeling unwell, "
    "please see a qualified healthcare professional. In an emergency, "
    "call your local emergency number 922 - SHA,"
     "1199 OR 1514 OR +254 700 395 395 - Kenya Red Cross"
    "+254 721 225 285 - St. John Ambulance") or "go to the nearest hospital."


DOCTOR_FOLLOW_UPS = (
    "\n\n**Questions a doctor would likely ask you:**\n"
    "- How long have you had these symptoms?\n"
    "- How severe are they (mild, moderate, severe)?\n"
    "- Do you have a fever, vomiting, or difficulty breathing?\n"
    "- Do you have any existing conditions or take any medication?\n"
)

RED_FLAGS = (
    "chest pain", "can't breathe", "cannot breathe", "difficulty breathing",
    "severe bleeding", "unconscious", "seizure", "stroke", "suicidal",
)


def add_doctor_style(question: str, reply: str) -> str:
    lowered = question.strip().lower()

    # Don't decorate the built-in commands
    if lowered in {"help", "symptoms", "topics"}:
        return reply

    if any(flag in lowered for flag in RED_FLAGS):
        reply = (
            "🚨 **This could be an emergency. Seek medical help immediately.**\n\n"
            + reply
        )
    else:
        reply += DOCTOR_FOLLOW_UPS

    return reply + DOCTOR_WARNING

def get_reply(question: str, data: dict) -> str:
    lowered = question.strip().lower()

    if lowered == "help":
        return get_help_text()

    if lowered == "symptoms":
        return list_symptoms(data["symptom_info"])

    if lowered == "topics":
        return list_topics(data["wellness_tips"])

    reply = get_bot_reply(
        question,
        data["health_faq"],
        data["symptom_info"],
        data["wellness_tips"],
        data["emergency_resources"],
    )
    return add_doctor_style(question, reply)

def welcome_message(disclaimer: str) -> dict:
    return {
        "role": "assistant",
        "content": (
            "Hello! I can answer general health questions, share wellness tips, "
            "and provide basic symptom information.\n\n"
            f"{disclaimer}"
        ),
    }


def init_session_state(disclaimer: str) -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = [welcome_message(disclaimer)]


def add_message(role: str, content: str) -> None:
    st.session_state.messages.append({"role": role, "content": content})


def render_chat_history() -> None:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def handle_question(question: str, data: dict) -> None:
    add_message("user", question)
    reply = get_reply(question, data)
    add_message("assistant", reply)


st.set_page_config(
    page_title="Health Chatbot",
    page_icon="🩺",
    layout="centered",
)

data = load_data()
disclaimer = data["emergency_resources"]["disclaimer"]
example_questions = load_example_questions()

init_session_state(disclaimer)

st.title(" Health Information Chatbot")
st.caption("School project — educational use only.")

with st.sidebar:
    st.header("About")
    st.info(disclaimer)

    st.header("Quick actions")
    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = [welcome_message(disclaimer)]
        st.rerun()

    st.header("Example questions")
    for question in example_questions:
        if st.button(question, use_container_width=True, key=f"example-{question}"):
            handle_question(question, data)
            st.rerun()

    with st.expander("Available symptoms"):
        st.write(list_symptoms(data["symptom_info"]))

    with st.expander("Wellness topics"):
        st.write(list_topics(data["wellness_tips"]))

render_chat_history()

if prompt := st.chat_input("Ask a health question..."):
    handle_question(prompt, data)
    st.rerun()
