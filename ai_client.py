import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# Load settings from the project folder.
load_dotenv(Path(__file__).resolve().parent / ".env")

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise RuntimeError("Add GROQ_API_KEY to your .env file.")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1",
)

MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

STUDY_INSTRUCTIONS = """
You are an AI Study Assistant for students.

Use simple language and short, clear explanations.
Use an example when it helps explain a concept.

For explanations:
- Define the concept.
- Explain its main idea.
- Give a simple example.

For summaries:
- Summarize the text supplied by the student.
- Preserve its main ideas.
- Ask for the text if none was supplied.

For practice questions:
- Generate the requested number of questions.
- If no number is specified, generate three.
- Put the answer key after the questions.

Use previous messages to understand follow-up questions.
Ask for clarification when necessary.
If uncertain, say so instead of inventing information.
"""


def create_history():
    """Start a conversation with the study instructions."""
    return [
        {"role": "system", "content": STUDY_INSTRUCTIONS}
    ]


def get_study_response(messages):
    """Send the conversation to Grok and return its answer."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=1500,
    )

    answer = response.choices[0].message.content

    if not answer or not answer.strip():
        raise ValueError("The model returned no text answer.")

    return answer