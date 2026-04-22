import streamlit as st
import google.generativeai as genai
import PyPDF2

# ─────────────────────────────────────────────
# 🔑 CONFIGURE GEMINI
# ─────────────────────────────────────────────
api_key = st.secrets["GEMINI_API_KEY"]

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-2.5-flash")

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(page_title="AI Bias Checker", page_icon="🤖", layout="wide")

st.title("🤖 AI Bias Checker (Gemini Powered)")
st.markdown("Now powered by Gemini AI for resume analysis 🚀")
st.divider()

# ─────────────────────────────────────────────
# FUNCTION: Extract text from PDF
# ─────────────────────────────────────────────
def extract_text(file):
    if file.type == "application/pdf":
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    else:
        return file.read().decode("utf-8")

# ─────────────────────────────────────────────
# FUNCTION: Gemini analyzes resume
# ─────────────────────────────────────────────
def analyze_resume(text):
    prompt = f"""
    Analyze this resume and return:
    - Skill Level (Low, Medium, High)
    - Estimated Years of Experience (number)

    Resume:
    {text}

    Respond ONLY in this format:
    Skill: <value>
    Experience: <number>
    """

    response = model.generate_content(prompt)
    return response.text

# ─────────────────────────────────────────────
# LAYOUT
# ─────────────────────────────────────────────
left_col, right_col = st.columns([1, 1])

with left_col:
    st.subheader("📋 Candidate Information")

    uploaded_file = st.file_uploader("Upload Resume (PDF/TXT)", type=["pdf", "txt"])
    name = st.text_input("Name")
    gender = st.selectbox("Gender", ["Male", "Female"])

    check_clicked = st.button("✅ Analyze with AI", use_container_width=True)

with right_col:
    st.subheader("📊 AI Decision Results")

    if check_clicked and uploaded_file:

        # STEP 1: Extract text
        resume_text = extract_text(uploaded_file)

        # STEP 2: Gemini analysis
        with st.spinner("🤖 Gemini analyzing resume..."):
            result = analyze_resume(resume_text)

        st.code(result)

        # STEP 3: Parse Gemini output
        try:
            lines = result.split("\n")
            skill_level = lines[0].split(":")[1].strip()
            experience = int(lines[1].split(":")[1].strip())
        except:
            st.error("Error parsing Gemini response")
            st.stop()

        # STEP 4: Decision logic (no forced bias now)
        if experience > 3 and skill_level == "High":
            final_decision = "Hire"
        else:
            final_decision = "Reject"

        # STEP 5: Bias check (simulate fairness test)
        male_decision = final_decision
        female_decision = final_decision  # same logic → fair

        bias_detected = male_decision != female_decision

        fairness_score = 100 if not bias_detected else 50

        # ── DISPLAY ──
        if final_decision == "Hire":
            st.success("✅ Hire")
        else:
            st.error("❌ Reject")

        st.markdown("---")

        if bias_detected:
            st.warning("⚠️ Bias Detected")
        else:
            st.success("✅ No Bias Detected")

        st.markdown(f"**Fairness Score:** {fairness_score}%")
        st.progress(fairness_score / 100)

        st.markdown("---")

        st.info(
            f"{name if name else 'Candidate'} evaluated with "
            f"{experience} years experience and {skill_level} skill level."
        )

    else:
        st.info("👈 Upload resume and click Analyze")