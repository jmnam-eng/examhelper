import streamlit as st
from data.sample_exams import EXAMS
from utils.styles import GLOBAL_CSS

st.set_page_config(
    page_title="학습진단 플랫폼",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
st.markdown("""
<style>
.hero-wrap {
    background: linear-gradient(135deg, #4361EE 0%, #7B5EA7 100%);
    border-radius: 18px;
    padding: 28px 24px 22px 24px;
    margin-bottom: 24px;
}
.hero-title {
    font-size: 1.9rem;
    font-weight: 900;
    color: #FFFFFF !important;
    margin: 0;
    line-height: 1.2;
}
.hero-sub {
    color: rgba(255,255,255,0.88) !important;
    font-size: 1rem;
    margin-top: 6px;
    font-weight: 500;
}
.section-label {
    font-size: 0.78rem;
    font-weight: 800;
    color: #5A6480 !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin: 22px 0 8px 2px;
}
.exam-row {
    background: #F5F7FF;
    border: 1.5px solid #DDE2F0;
    border-radius: 14px;
    padding: 14px 16px;
    margin-bottom: 10px;
}
.exam-title {
    font-weight: 700;
    color: #1E2235 !important;
    font-size: 1rem;
}
.exam-meta {
    color: #5A6480 !important;
    font-size: 0.85rem;
    margin-top: 2px;
}
.ai-card {
    background: #F5F7FF;
    border: 1.5px solid #DDE2F0;
    border-radius: 14px;
    padding: 16px;
    height: 100%;
}
.ai-card-title {
    font-weight: 800;
    color: #1E2235 !important;
    font-size: 1rem;
    margin-bottom: 4px;
}
.ai-card-desc {
    color: #5A6480 !important;
    font-size: 0.85rem;
    line-height: 1.5;
}
</style>
""", unsafe_allow_html=True)

# 히어로
st.markdown("""
<div class="hero-wrap">
  <div class="hero-title">📚 학습진단 플랫폼</div>
  <div class="hero-sub">시험 풀기 · AI 문제 생성 · 풀이 교정</div>
</div>
""", unsafe_allow_html=True)

# ── 시험 풀기 ──
st.markdown('<div class="section-label">📝 예시 시험</div>', unsafe_allow_html=True)

for exam_name, exam_data in EXAMS.items():
    col1, col2 = st.columns([3, 1])
    with col1:
        grade_label = f"{exam_data['grade']} · " if exam_data.get("grade") else ""
        st.markdown(f"""
        <div class="exam-row">
            <div class="exam-title">{exam_name}</div>
            <div class="exam-meta">{grade_label}{exam_data['subject']} · {len(exam_data['questions'])}문항</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        if st.button("시작 ▶", key=f"exam_{exam_name}", use_container_width=True, type="primary"):
            st.session_state["selected_exam"] = exam_name
            st.session_state["exam_started"] = False
            st.session_state["current_question"] = 0
            st.session_state["answers"] = {}
            st.session_state["times"] = {}
            st.session_state["question_start_time"] = None
            st.session_state["exam_complete"] = False
            st.switch_page("pages/1_시험풀기.py")

# ── AI 기능 ──
st.markdown('<div class="section-label">🤖 AI 기능</div>', unsafe_allow_html=True)

col_a, col_b = st.columns(2)
with col_a:
    st.markdown("""
    <div class="ai-card">
        <div class="ai-card-title">✏️ 문제 생성</div>
        <div class="ai-card-desc">학습자료 업로드<br>→ AI가 맞춤 문제 출제</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("문제 생성하기", use_container_width=True, key="go_gen"):
        st.switch_page("pages/4_문제생성.py")

with col_b:
    st.markdown("""
    <div class="ai-card">
        <div class="ai-card-title">🔍 풀이 교정</div>
        <div class="ai-card-desc">손필기 PDF·사진<br>→ AI가 오류·개선점 분석</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if st.button("풀이 교정하기", use_container_width=True, key="go_cor"):
        st.switch_page("pages/5_풀이교정.py")

# ── 최근 결과 ──
if st.session_state.get("exam_complete"):
    st.markdown('<div class="section-label">📊 최근 결과</div>', unsafe_allow_html=True)
    exam_name = st.session_state.get("selected_exam", "")
    st.caption(f"완료: {exam_name}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 결과 분석", use_container_width=True):
            st.switch_page("pages/2_결과분석.py")
    with col2:
        if st.button("🎯 학습 가이드", use_container_width=True):
            st.switch_page("pages/3_학습가이드.py")
