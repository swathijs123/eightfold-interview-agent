# Interview Practice Partner

AI-powered Streamlit app for running rapid-fire mock interviews with voice input, real-time transcription, strict interviewer behavior, and a qualitative + scored feedback report at the end.

## Features
- Role/level selector pre-interview lobby with coordinator chat for format questions.
- Voice-driven interview flow: AI reads each question aloud (gTTS) and records answers via `audio-recorder-streamlit`, transcribing them through Groq Whisper.
- Strict interviewer prompt that never evaluates answers mid-session and keeps cadence snappy.
- Automatic timeout/skip handling plus 20-question progress indicator.
- Post-session Markdown feedback report and 0–100 readiness score with justification.

## Prerequisites
- Python 3.10+ (tested with 3.13).
- Groq API key with access to `llama-3.3-70b-versatile` and `whisper-large-v3-turbo`.
- Microphone and speakers for voice recording/playback.

## Setup
1. Clone or download the repo and open a terminal inside `interview-agent`.
2. (Optional but recommended) create a virtual environment:
   ```bash
   py -3 -m venv .venv
   .\.venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install streamlit python-dotenv openai audio-recorder-streamlit gTTS
   ```
4. Create a `.env` file in the project root with:
   ```
   GROQ_API_KEY=sk_your_key_here
   ```

## Running the App
```bash
streamlit run app.py
```
Streamlit prints a local URL (default `http://localhost:8501`). Open it in the browser, configure the role/experience level, and click “START PRACTICE SESSION.” Grant microphone access when prompted.

### Controls
- `Skip` advances to a new question without scoring the answer.
- `Quit` ends the interview early and jumps to feedback.
- `🔁 Rerun App` (top-right) resets the Streamlit session.

## Backend Connectivity Test
To verify your Groq credentials independently of the UI:
```bash
python test_backend.py
```
The script loads `GROQ_API_KEY`, pings Groq using `llama3-8b-8192`, and prints any errors or a success message.

## Customization
- Update colors/components in `app.py` inside the “PREMIUM CSS” block.
- Adjust the strict interviewer rules or scoring prompts in Phase 2/3 to fit different interview styles.

## Troubleshooting
- **Audio errors**: ensure microphone permissions are granted and no other app is locking the device.
- **Groq errors**: confirm the API key is valid and your machine can reach `api.groq.com`.
- **Slow installs**: re-run `pip install` with `--default-timeout=120` if downloads timeout.



