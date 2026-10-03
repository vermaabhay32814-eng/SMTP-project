import smtplib
from email.mime.text import MIMEText

import streamlit as st
from google import genai
from google.genai import types

from prompts import SYSTEM_PROMPT, WELCOME_MESSAGE_TEMPLATE, SUMMARY_REQUEST_PROMPT

# --- config ---
MODEL_NAME = "gemini-3.8-flash"

st.set_page_config(page_title="MacroSnap", page_icon="🥗", layout="centered")

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
GMAIL_ADDRESS = st.secrets["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD = st.secrets["GMAIL_APP_PASSWORD"]


# --- dark google-style CSS ---

st.markdown("""
<style>
    /* import a clean font */
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&family=Inter:wght@400;500;600&display=swap');

    /* base overrides */
    .stApp {
        font-family: 'Inter', 'Google Sans', sans-serif;
    }

    /* onboarding card — that centered box look */
    div[data-testid="stForm"] {
        background: #2d2d2d;
        border: 1px solid #3c4043;
        border-radius: 16px;
        padding: 2.5rem 2rem 2rem;
        max-width: 480px;
        margin: 2rem auto;
        box-shadow: 0 4px 24px rgba(0,0,0,0.4);
    }

    /* text inputs — subtle border, rounded */
    div[data-testid="stForm"] input {
        background: #1f1f1f !important;
        border: 1px solid #5f6368 !important;
        border-radius: 8px !important;
        color: #e8eaed !important;
        padding: 12px 14px !important;
        font-size: 15px !important;
        transition: border-color 0.2s ease;
    }
    div[data-testid="stForm"] input:focus {
        border-color: #8ab4f8 !important;
        box-shadow: 0 0 0 2px rgba(138,180,248,0.25) !important;
    }

    /* form labels */
    div[data-testid="stForm"] label {
        color: #bdc1c6 !important;
        font-size: 14px !important;
        font-weight: 500 !important;
    }

    /* submit button — google blue pill */
    div[data-testid="stForm"] button[kind="formSubmit"] {
        background: #8ab4f8 !important;
        color: #1f1f1f !important;
        border: none !important;
        border-radius: 24px !important;
        padding: 10px 32px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        letter-spacing: 0.3px;
        transition: background 0.2s ease, transform 0.1s ease;
        margin-top: 0.5rem;
    }
    div[data-testid="stForm"] button[kind="formSubmit"]:hover {
        background: #aecbfa !important;
        transform: translateY(-1px);
    }

    /* the whatsapp/email send button in chat */
    div[data-testid="stButton"] button {
        background: #303134 !important;
        color: #8ab4f8 !important;
        border: 1px solid #5f6368 !important;
        border-radius: 24px !important;
        font-weight: 500 !important;
        font-size: 13px !important;
        transition: all 0.2s ease;
    }
    div[data-testid="stButton"] button:hover {
        background: #3c4043 !important;
        border-color: #8ab4f8 !important;
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(138,180,248,0.2);
    }
    div[data-testid="stButton"] button:disabled {
        opacity: 0.4 !important;
        color: #5f6368 !important;
    }

    /* chat messages — rounder, cleaner */
    div[data-testid="stChatMessage"] {
        border-radius: 12px;
        border: 1px solid #3c4043;
        margin-bottom: 0.5rem;
    }

    /* title styling */
    h1 {
        font-family: 'Google Sans', 'Inter', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }

    /* caption text */
    .stCaption, div[data-testid="stCaptionContainer"] {
        color: #9aa0a6 !important;
        font-size: 13px !important;
    }

    /* chat input bar */
    div[data-testid="stChatInput"] textarea {
        background: #2d2d2d !important;
        border: 1px solid #5f6368 !important;
        border-radius: 24px !important;
        color: #e8eaed !important;
    }
    div[data-testid="stChatInput"] textarea:focus {
        border-color: #8ab4f8 !important;
    }

    /* success/error toasts */
    div[data-testid="stAlert"] {
        border-radius: 12px;
    }

    /* spinner text */
    .stSpinner > div {
        color: #8ab4f8 !important;
    }

    /* hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# --- cached clients so they survive streamlit reruns ---

@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)

gemini_client = get_gemini_client()


# --- helper functions ---

def render_message(msg):
    with st.chat_message(msg["role"]):
        if msg["kind"] == "text":
            st.write(msg["content"])
        elif msg["kind"] == "image":
            st.image(msg["content"])


def add_message(role, kind, content):
    st.session_state.messages.append({"role": role, "kind": kind, "content": content})
    render_message(st.session_state.messages[-1])


def ask_gemini(parts):
    try:
        response = st.session_state.chat.send_message(parts)
        return response.text
    except Exception as e:
        return f"Sorry, something went wrong: {e}"


def send_email(to_address, subject, body):
    """Fire off a plain-text email via Gmail SMTP. Returns (success, info)."""
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = to_address

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.send_message(msg)
        return True, "sent"
    except Exception as e:
        return False, str(e)


# =====================
# ONBOARDING
# =====================

if "onboarded" not in st.session_state:
    # little spacer so the card isn't jammed at the top
    st.markdown("<br>", unsafe_allow_html=True)

    st.title("🥗 MacroSnap")
    st.caption("Snap it. Track it. Email yourself the results.")

    with st.form("onboarding_form"):
        name = st.text_input("Your name")
        email = st.text_input(
            "Your email address",
            placeholder="you@example.com",
            help="MacroSnap will send your meal summary here.",
        )
        submitted = st.form_submit_button("Let's go 🚀")

        if submitted:
            if not name.strip() or not email.strip():
                st.warning("Please fill in both fields.")
            else:
                st.session_state.name = name.strip()
                st.session_state.email = email.strip()

                # spin up a gemini chat session with our system prompt
                st.session_state.chat = gemini_client.chats.create(
                    model=MODEL_NAME,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT
                    ),
                )
                st.session_state.messages = []
                st.session_state.onboarded = True
                st.rerun()

    st.stop()  # don't render anything below until onboarded


# =====================
# CHAT UI
# =====================

# header row — title on the left, send button on the right
header_col, btn_col = st.columns([5, 2], vertical_alignment="center")

with header_col:
    st.title("🥗 MacroSnap")

with btn_col:
    # don't let them send a summary if they haven't actually logged anything yet
    # (messages[0] is always the welcome msg, so we need more than that)
    send_disabled = len(st.session_state.messages) <= 2

    if st.button("📧 Send summary to Email", disabled=send_disabled, use_container_width=True):
        with st.spinner("Summarizing your meals..."):
            summary = ask_gemini([SUMMARY_REQUEST_PROMPT])

        ok, info = send_email(
            to_address=st.session_state.email,
            subject=f"MacroSnap Summary for {st.session_state.name}",
            body=summary,
        )
        if ok:
            st.success("Sent! Check your inbox 📬")
        else:
            st.error(f"Couldn't send: {info}")

st.caption(f"Logged in as {st.session_state.name} · summary goes to {st.session_state.email}")

# show welcome message on first load, replay history on reruns
if not st.session_state.messages:
    welcome = WELCOME_MESSAGE_TEMPLATE.format(name=st.session_state.name)
    add_message("assistant", "text", welcome)
else:
    for m in st.session_state.messages:
        render_message(m)

# the chat input — handles both text and photo uploads
user_input = st.chat_input(
    "Ask a question, or attach a photo of your meal",
    accept_file=True,
    file_type=["jpg", "jpeg", "png"],
)

if user_input:
    photo = user_input.files[0] if user_input.files else None
    text = user_input.text

    parts = []

    if photo is not None:
        photo_bytes = photo.getvalue()
        add_message("user", "image", photo_bytes)
        parts.append(types.Part.from_bytes(data=photo_bytes, mime_type=photo.type))

    if text:
        add_message("user", "text", text)
        parts.append(text)
    elif photo is not None:
        # they sent a photo with no caption, so we ask for them
        parts.append("What is this meal? Give me the calories and macros.")

    with st.spinner("Crunching the numbers..."):
        answer = ask_gemini(parts)

    add_message("assistant", "text", answer)
