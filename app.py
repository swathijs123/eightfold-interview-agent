import streamlit as st
from openai import OpenAI
import os
import json
from dotenv import load_dotenv
from audio_recorder_streamlit import audio_recorder
from gtts import gTTS
import base64
from io import BytesIO
import hashlib
import time

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Interview Practice Partner", 
    page_icon="", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)
load_dotenv()

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

# --- 2. PREMIUM CSS ---
st.markdown("""
    <style>
        /* GLOBAL RESET */
        .stApp { background-color: #0E1117; color: #E0E0E0; font-family: 'Inter', sans-serif; }
        
        /* OPTIMAL SPACING */
        .block-container { padding-top: 3rem; padding-bottom: 3rem; max-width: 1100px; }
        section[data-testid="stSidebar"] { display: none; }
        
        /* HEADER STYLING */
        .hero-title {
            font-size: 3rem;
            font-weight: 800;
            background: -webkit-linear-gradient(45deg, #00C853, #3498db);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
            text-align: center;
        }
        .hero-subtitle {
            font-size: 1.1rem;
            color: #888;
            margin-top: 10px;
            text-align: center;
            margin-bottom: 40px;
        }

        /* CARDS */
        .glass-card {
            background: rgba(30, 42, 56, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 25px;
            height: 100%;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        
        /* CHAT BUBBLES */
        .stChatMessage { padding: 1rem; border-radius: 10px; margin-bottom: 0.5rem; border: none; }
        .stChatMessage[data-testid="stChatMessageUser"] { background-color: #2b313e; }
        .stChatMessage[data-testid="stChatMessageAssistant"] { background-color: #1a1f26; }

        /* FEEDBACK REPORT HEADER */
        .report-header-card {
            background: linear-gradient(135deg, #1e2a38 0%, #161b22 100%);
            padding: 30px;
            border-radius: 15px;
            border: 1px solid #30363d;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
    </style>
""", unsafe_allow_html=True)

# --- QUICK RERUN CONTROL ---
with st.container():
    _, _, rerun_col = st.columns([6, 2, 1])
    with rerun_col:
        if st.button("🔁 Rerun App", key="rerun_top", use_container_width=True):
            try:
                st.experimental_rerun()
            except AttributeError:
                st.rerun()

# --- 3. AUDIO ENGINE ---
def play_ai_voice(text):
    try:
        tts = gTTS(text=text, lang='en')
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_base64 = base64.b64encode(audio_buffer.getvalue()).decode()
        audio_html = f"""<audio autoplay><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>"""
        st.markdown(audio_html, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Audio Error: {e}")

# --- 4. STATE MANAGEMENT ---
if "messages" not in st.session_state: st.session_state.messages = [] 
if "lobby_messages" not in st.session_state: st.session_state.lobby_messages = [] 
if "interview_active" not in st.session_state: st.session_state.interview_active = False
if "feedback_mode" not in st.session_state: st.session_state.feedback_mode = False
if "question_count" not in st.session_state: st.session_state.question_count = 0
if "last_audio_hash" not in st.session_state: st.session_state.last_audio_hash = None
if "final_report" not in st.session_state: st.session_state.final_report = ""
if "final_score" not in st.session_state: st.session_state.final_score = None
if "selected_role" not in st.session_state: st.session_state.selected_role = "Software Engineer"
if "selected_level" not in st.session_state: st.session_state.selected_level = "Junior"

# --- 5. MAIN APPLICATION ---

# ============================================================
# PHASE 1: THE LOBBY (Pleasant & Spacious)
# ============================================================
if not st.session_state.interview_active and not st.session_state.feedback_mode:
    
    st.markdown("""
        <div class="hero-container">
            <h1 class="hero-title">Interview Practice Partner</h1>
            <p class="hero-subtitle">AI-Powered Mock Interview System</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="large")
    
    # --- LEFT: SETUP ---
    with col1:
        st.markdown(
            """
            <div class="glass-card">
                <h3 style="color: #3498db; margin-bottom: 15px;">🛠️ Session Configuration</h3>
            """, unsafe_allow_html=True
        )
        
        st.session_state.selected_role = st.selectbox("Select Target Role", ["Software Engineer", "Sales Representative", "Retail Associate"])
        st.session_state.selected_level = st.selectbox("Experience Level", ["Junior", "Mid-Level", "Senior"])
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("⚠️ **Note:** Once started, the timer cannot be paused.")
        
        if st.button("🚀 START PRACTICE SESSION", type="primary", use_container_width=True):
            st.session_state.interview_active = True
            st.session_state.question_count = 1
            st.session_state.messages = []
            
            # Opener Logic
            role = st.session_state.selected_role
            if role == "Software Engineer": opener = "Q1: Introduce yourself and your tech stack."
            elif role == "Sales Representative": opener = "Q1: Pitch yourself in 30 seconds."
            else: opener = "Q1: Why do you want to work in retail?"
                
            st.session_state.messages.append({"role": "assistant", "content": opener})
            st.rerun()
            
        st.markdown("</div>", unsafe_allow_html=True)

    # --- RIGHT: INFO & COORDINATOR ---
    with col2:
        st.markdown(
            """
            <div class="glass-card">
                <h3 style="color: #00C853; margin-bottom: 15px;">ℹ️ Practice Guide</h3>
                <ul style="color: #B0B0B0; line-height: 1.8; margin-bottom: 20px;">
                    <li><b>Format:</b> 20 Rapid-Fire Questions</li>
                    <li><b>Input:</b> Voice Only (Click Mic)</li>
                    <li><b>Timer:</b> 20s buffer to start answering</li>
                </ul>
                <hr style="border-color: #333; margin-bottom: 20px;">
                <div style="font-weight: bold; margin-bottom: 10px;">👩‍💼 Coordinator Chat</div>
            """, unsafe_allow_html=True
        )
        
        # Chat area inside the card
        chat_container = st.container(height=150)
        with chat_container:
            if not st.session_state.lobby_messages:
                st.caption("Ask specific questions about the interview format here.")
            for msg in st.session_state.lobby_messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

        if user_query := st.chat_input("Ask coordinator..."):
            st.session_state.lobby_messages.append({"role": "user", "content": user_query})
            
            # --- STRICT COORDINATOR LOGIC ---
            coordinator_prompt = f"""
            You are the Practice Coordinator.
            User Query: "{user_query}"
            
            INSTRUCTIONS:
            1. If the query is about the interview, role ({st.session_state.selected_role}), or rules: Answer helpfuly.
            2. If the query is IRRELEVANT (weather, jokes, coding help, sports, general chat):
               Reply EXACTLY: "This inquiry is not relevant to the assessment. Please focus on the interview preparations."
            """
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": coordinator_prompt}] + st.session_state.lobby_messages
            )
            st.session_state.lobby_messages.append({"role": "assistant", "content": response.choices[0].message.content})
            st.rerun()
            
        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# PHASE 2: ACTIVE INTERVIEW
# ============================================================
elif st.session_state.interview_active:
    
    # Header
    c1, c2 = st.columns([3, 1])
    with c1: st.subheader(f"🎙️ {st.session_state.selected_role} Session")
    with c2: st.markdown(f"<h4 style='text-align: right; color: #3498db;'>Q{st.session_state.question_count} / 20</h4>", unsafe_allow_html=True)
    st.progress(min(st.session_state.question_count / 20, 1.0))

    # History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Voice Output
    last_msg = st.session_state.messages[-1]
    if last_msg["role"] == "assistant":
        msg_hash = hash(last_msg["content"])
        if "last_spoken_hash" not in st.session_state or st.session_state.last_spoken_hash != msg_hash:
            play_ai_voice(last_msg["content"])
            st.session_state.last_spoken_hash = msg_hash
            st.session_state.question_start_time = time.time()

    st.divider()

    # Input Zone
    col1, col2, col3 = st.columns([1, 2, 1])
    user_input = ""
    is_timeout = False
    
    with col2:
        # JS Focus Timer
        st.components.v1.html(
            f"""
            <div id="timer-box" style="color: #ff4b4b; text-align: center; font-family: sans-serif; font-weight: bold; font-size: 24px;">
                Start in: <span id="time">20</span>s
            </div>
            <script>
                var t=20; var e=document.getElementById('time');
                var timer=setInterval(function(){{ if(t<=0){{clearInterval(timer);e.innerHTML="LATE";}}else{{e.innerHTML=t;t--;}} }},1000);
                setInterval(function(){{ if(window.parent.document.activeElement && window.parent.document.activeElement.tagName==="IFRAME"){{ 
                    clearInterval(timer); document.getElementById('timer-box').innerHTML="<span style='color:#00C853'>🎙️ RECORDING...</span>"; 
                }} }},200);
            </script>
            """, height=50
        )
        
        audio_bytes = audio_recorder(text="", recording_color="#e74c3c", neutral_color="#00C853", icon_size="3x")
        
        c_a, c_b = st.columns(2)
        with c_a:
            if st.button("➡️ Skip", use_container_width=True): user_input = "SKIP"
        with c_b:
            if st.button("🔴 Quit", use_container_width=True): 
                st.session_state.interview_active = False
                st.session_state.feedback_mode = True
                st.rerun()

    # Processing Logic
    if audio_bytes:
        current_hash = hashlib.md5(audio_bytes).hexdigest()
        if current_hash != st.session_state.last_audio_hash:
            st.session_state.last_audio_hash = current_hash
            if (time.time() - st.session_state.question_start_time) > 200: is_timeout = True
            else:
                with st.spinner("Processing..."):
                    with open("temp.wav", "wb") as f: f.write(audio_bytes)
                    try: 
                        transcript = client.audio.transcriptions.create(model="whisper-large-v3-turbo", file=open("temp.wav", "rb"))
                        user_input = transcript.text
                    except: pass

    if user_input or is_timeout:
        if is_timeout:
            st.session_state.messages.append({"role": "user", "content": "(Timeout)"})
            system_instruction = "User Timed out. Reply: 'Time exceeded. Next question:' followed by question."
        elif user_input == "SKIP":
            st.session_state.messages.append({"role": "user", "content": "(Skipped)"})
            system_instruction = "User Skipped. Reply: 'Noted. Next question:' followed by NEW question."
        else:
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # --- STRICTEST PROMPT FOR BREVITY ---
            system_instruction = f"""
            You are a strict Interviewer for {st.session_state.selected_role}.
            Candidate just answered.
            
            STRICT RULES:
            1. DO NOT repeat, summarize, or rephrase the candidate's answer.
            2. DO NOT give evaluative feedback (no "Good answer", "Great point").
            3. Acknowledge with exactly ONE professional word/phrase (e.g., "Noted.", "Understood.", "Clear.", "Right.").
            4. Immediately ask the NEXT question.
            
            Example: "Noted. How do you handle API rate limiting?"
            Example: "Understood. Tell me about a conflict you had with a coworker."
            """

        with st.spinner("Thinking..."):
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": system_instruction}] + st.session_state.messages
            )
            ai_reply = completion.choices[0].message.content

        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
        st.session_state.question_count += 1
        
        if st.session_state.question_count > 20:
            st.session_state.interview_active = False
            st.session_state.feedback_mode = True
        
        st.rerun()

# ============================================================
# PHASE 3: FEEDBACK REPORT (Qualitative Only)
# ============================================================
elif st.session_state.feedback_mode:
    
    if not st.session_state.final_report:
        with st.spinner("Compiling Performance Review..."):
            grading_prompt = f"""
            Role: {st.session_state.selected_role}. Review transcript.
            
            GENERATE A QUALITATIVE FEEDBACK REPORT (Markdown).            DO NOT PROVIDE A HIRE/NO-HIRE DECISION.
            
            Structure:
            ### 1. Executive Summary
            [Brief overview of performance]
            
            ### 2. Key Strengths
            * [Strength 1]
            * [Strength 2]
            
            ### 3. Areas for Improvement
            * [Weakness 1]
            * [Weakness 2]
            
            ### 4. Suggested Learning Path
            [Recommendations]
            """
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.messages + [{"role": "user", "content": grading_prompt}]
            )
            st.session_state.final_report = completion.choices[0].message.content

    if not st.session_state.final_score:
        with st.spinner("Calculating overall score..."):
            score_prompt = f"""
            Role: {st.session_state.selected_role}. Review transcript.
            
            Return a JSON object with:
            - "score": integer 0-100 overall readiness score.
            - "justification": one sentence explaining the score.
            Consider clarity, depth, structure, and role alignment.
            Respond ONLY with valid JSON.
            """
            score_completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.messages + [{"role": "user", "content": score_prompt}]
            )
            score_raw = score_completion.choices[0].message.content.strip()
            try:
                st.session_state.final_score = json.loads(score_raw)
            except json.JSONDecodeError:
                st.session_state.final_score = {"score": None, "justification": score_raw}

    # HEADER
    st.markdown(f"""
    <div class='report-header-card'>
        <h2 style='margin:0; color: white;'>📋 Practice Session Feedback</h2>
        <p style='color: #888; margin: 10px 0 0 0;'>Evaluation for {st.session_state.selected_role}</p>
    </div>
    """, unsafe_allow_html=True)

    # SCORECARD
    score_value = st.session_state.final_score.get("score")
    score_label = f"{score_value}/100" if isinstance(score_value, int) else "N/A"
    with st.container(border=True):
        st.metric("Overall Score", score_label)
        st.caption(st.session_state.final_score.get("justification", ""))
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # CONTENT
    with st.container(border=True):
        st.markdown(st.session_state.final_report)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Start New Session", type="primary", use_container_width=True):
            st.session_state.clear()
            st.rerun()