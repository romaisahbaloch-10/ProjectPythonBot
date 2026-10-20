
import streamlit as st
from openai import APIError
from ai_client import create_history, get_study_response
import json
import uuid
from pathlib import Path


# -----------------------------------
# 1. Page configuration
# -----------------------------------

st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="📚",
    layout="centered",
)

st.title("AI Study Assistant")
st.caption(
    "Your learning companion for explanations, summaries, "
    "and practice questions."
)

HISTORY_FILE = Path("chat_history.json")


def load_chats():
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_chats():
    with open(HISTORY_FILE, "w", encoding="utf-8") as file:
        json.dump(
            st.session_state.chats,
            file,
            ensure_ascii=False,
            indent=4,
        )


def create_new_chat():
    chat_id = str(uuid.uuid4())

    st.session_state.chats[chat_id] = {
        "title": "New chat",
        "messages": create_history(),
    }

    st.session_state.current_chat_id = chat_id
    save_chats()

# -----------------------------------
# 2. Initialize conversation state
# -----------------------------------

if "chats" not in st.session_state:
    st.session_state.chats = load_chats()

if "current_chat_id" not in st.session_state:
    if st.session_state.chats:
        st.session_state.current_chat_id = next(
            reversed(st.session_state.chats)
        )
    else:
        create_new_chat()


# -----------------------------------
# 3. Sidebar
# -----------------------------------

with st.sidebar:
    st.header("Study Assistant")
    st.write("What would you like to learn today?")

    st.divider()
 # Recent Chats
    st.subheader("Recent Chats")

    recent_chats = list(st.session_state.chats.items())[::-1]

    for chat_id, chat in recent_chats:
        button_label = chat["title"]

        if chat_id == st.session_state.current_chat_id:
            button_label = "📌 " + button_label

        if st.button(
            button_label,
            key=f"chat_{chat_id}",
            use_container_width=True,
        ):
            st.session_state.current_chat_id = chat_id
            st.rerun()

    st.subheader("Available features")
    st.write("- Explain concepts")
    st.write("- Summarize text")
    st.write("- Generate practice questions")

  
    if st.button("New conversation", use_container_width=True):
        create_new_chat()
        st.rerun()


# -----------------------------------
# 4. Display previous chat messages
# -----------------------------------


current_chat = st.session_state.chats[
    st.session_state.current_chat_id
]

messages = current_chat["messages"]

for message in messages:
    if message["role"] == "system":
        continue

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------------------------------
# 5. Accept a new question
# -----------------------------------

prompt = st.chat_input("Ask a study question...")

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)

    next_messages = messages + [
        {"role": "user", "content": prompt}
    ]

    try:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = get_study_response(next_messages)

            st.markdown(answer)

        # Save messages to the selected conversation
        current_chat["messages"] = next_messages + [
            {"role": "assistant", "content": answer}
        ]

        # Set the title using the first question
        if current_chat["title"] == "New chat":
            current_chat["title"] = prompt.strip().replace(
                "\n", " "
            )[:40]

        # Save chat history and refresh the app
        save_chats()
        st.rerun()

    except (APIError, ValueError) as error:
        st.error(
            "Could not get an answer. Check your API configuration "
            "and connection, then try again."
        )
        print(f"AI API error: {error}")


# if prompt:
#     # Display the user's question immediately.
#     with st.chat_message("user"):
#         st.markdown(prompt)

#     # Prepare conversation history for the API.
#    next_messages = messages + [
#     {"role": "user", "content": prompt}
# ]

#     try:
#         with st.chat_message("assistant"):
#             with st.spinner("Thinking..."):
#                 answer = get_study_response(next_messages)

#             st.markdown(answer)

#         # Save history only after a successful response.
#         st.session_state.messages = next_messages + [
#             {"role": "assistant", "content": answer}
#         ]

#     except (APIError, ValueError) as error:
#         st.error(
#             "Could not get an answer. Check your API configuration "
#             "and connection, then try again."
#         )
#         print(f"AI API error: {error}")
