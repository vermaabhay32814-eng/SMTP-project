# MacroSnap

MacroSnap is a Streamlit app that helps users estimate calories and macros for meals from a photo or text description, then send a summary email.

## Features

- Upload a meal photo or describe a meal in text
- Ask Gemini to estimate calories and macros
- Chat-style nutrition assistant experience
- Generate a meal summary and send it via Gmail SMTP
- Simple onboarding flow for name and email

## Tech Stack

- Python
- Streamlit
- Google Gemini API (`google-genai`)
- Gmail SMTP for email delivery

## Project Structure

- `app.py` – main Streamlit app and chat UI
- `prompts.py` – AI system prompt and email summary prompt
- `requirements.txt` – Python dependencies
- `.streamlit/secrets.toml.example` – example secrets file

## Setup

1. Create and activate a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure secrets:

   Create a `.streamlit/secrets.toml` file in the project root using the example template:

   ```toml
   GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
   GMAIL_ADDRESS = "your-email@gmail.com"
   GMAIL_APP_PASSWORD = "YOUR_GMAIL_APP_PASSWORD"
   ```

   Notes:
   - `GEMINI_API_KEY` should be a valid Google AI / Gemini API key.
   - `GMAIL_APP_PASSWORD` should be a Gmail app password, not your normal account password.

4. Run the app:

   ```bash
   streamlit run app.py
   ```

## Usage

- Open the app in your browser.
- Enter your name and email on first launch.
- Ask about a meal by typing or uploading a photo.
- MacroSnap estimates calories and macros and helps summarize what you ate.
- Click the email button to send the summary to your inbox.

## Notes

This app relies on external services:
- Gemini for AI analysis
- Gmail SMTP for sending the final summary

## License

This project does not currently include a license file.

Live Demo Link -> https://smtp-project-57cgafx5gasgbde632g3pp.streamlit.app/
