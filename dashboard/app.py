import streamlit as st
import requests
import json
from datetime import datetime

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="EduGuard Dashboard",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ EduGuard — Teacher Dashboard")

tab1, tab2, tab3 = st.tabs(["🚨 Live Violations", "📝 Exam Submissions", "🧪 Live Demo"])

# TAB 1: Violations
with tab1:
    st.subheader("Recent Security Violations")
    if st.button("Refresh Violations"):
        try:
            res = requests.get(f"{API_URL}/dashboard/violations")
            violations = res.json()
            for v in violations:
                severity_color = "🔴" if v.get("severity") == "critical" else "🟠"
                with st.expander(f"{severity_color} {v.get('type', 'unknown')} — Student {v.get('student_id')} — {v.get('timestamp', '')[:19]}"):
                    st.code(v.get("input", ""), language="text")
                    st.write(f"Severity: {v.get('severity')}")
                    st.write(f"Endpoint: {v.get('endpoint')}")
        except Exception as e:
            st.error(f"Could not fetch violations: {e}")

# TAB 2: Exam Submissions
with tab2:
    st.subheader("Recent Exam Submissions")
    if st.button("Refresh Submissions"):
        try:
            res = requests.get(f"{API_URL}/dashboard/submissions")
            submissions = res.json()
            for s in submissions:
                grading = s.get("grading", {})
                security = s.get("security", {})
                score = grading.get("score", "N/A")
                flag = "⚠️ Plagiarism Suspected" if security.get("plagiarism_suspected") else "✅ Clean"
                with st.expander(f"Student {s.get('student_id')} | Score: {score}/100 | {flag}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Grading**")
                        st.json(grading)
                    with col2:
                        st.write("**Security**")
                        st.json(security)
        except Exception as e:
            st.error(f"Could not fetch submissions: {e}")

# TAB 3: Live Demo
with tab3:
    st.subheader("Live API Demo")

    demo_tab1, demo_tab2 = st.tabs(["Tutor Demo", "Exam Validator Demo"])

    with demo_tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Test Input")
            student_id = st.text_input("Student ID", value="STU_DEMO")
            subject = st.selectbox("Subject", ["Physics", "Math", "Biology", "Chemistry", "History"])
            grade = st.selectbox("Grade", ["8", "9", "10", "11", "12"])
            question = st.text_area("Student Question", height=100,
                value="Can you explain photosynthesis?")
            if st.button("Send to Tutor API"):
                with st.spinner("Running through guardrail pipeline..."):
                    res = requests.post(f"{API_URL}/tutor/ask", json={
                        "student_id": student_id,
                        "question": question,
                        "subject": subject,
                        "grade_level": grade
                    })
                    result = res.json()
                with col2:
                    st.markdown("### Pipeline Result")
                    status = result.get("status")
                    if status == "blocked":
                        st.error(f"🚫 BLOCKED at stage: {result.get('stage')}")
                        st.warning(f"Rule triggered: {result.get('reason')}")
                        st.info(f"Message to student: {result.get('message')}")
                    else:
                        st.success("✅ All guardrails passed")
                        st.write(f"Stages passed: {result.get('stages_passed')}")
                        st.markdown("**Tutor Response:**")
                        st.write(result.get("response"))

    with demo_tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Test Input")
            s_id = st.text_input("Student ID", value="STU_DEMO", key="exam_sid")
            e_id = st.text_input("Exam ID", value="EXAM_001")
            question_text = st.text_area("Question", height=80,
                value="Explain Newton's second law with an example.")
            rubric_text = st.text_area("Rubric", height=80,
                value="Definition(25pts) Formula(25pts) Example(25pts) Clarity(25pts)")
            answer_text = st.text_area("Student Answer", height=120,
                value="F=ma means force equals mass times acceleration.")
            if st.button("Validate Answer"):
                with st.spinner("Running validation pipeline..."):
                    res = requests.post(f"{API_URL}/exam/validate", json={
                        "student_id": s_id,
                        "exam_id": e_id,
                        "question": question_text,
                        "rubric": rubric_text,
                        "student_answer": answer_text,
                        "grade_level": "10"
                    })
                    result = res.json()
                with col2:
                    st.markdown("### Validation Result")
                    status = result.get("status")
                    if status == "blocked":
                        st.error(f"🚫 INJECTION DETECTED: {result.get('reason')}")
                    else:
                        grading = result.get("grading", {})
                        security = result.get("security", {})
                        st.success(f"✅ Score: {grading.get('score')}/100 — Grade: {grading.get('grade')}")
                        if security.get("plagiarism_suspected"):
                            st.warning(f"⚠️ Plagiarism suspected ({security.get('plagiarism_confidence')}% confidence)")
                        st.markdown("**Feedback:**")
                        st.write(grading.get("feedback"))
                        st.markdown("**Improvement:**")
                        st.write(grading.get("improvement_suggestion"))