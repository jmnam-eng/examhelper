import io
import time
import numpy as np
import streamlit as st
from PIL import Image as PILImage
from streamlit_drawable_canvas import st_canvas
from data.sample_exams import EXAMS
from utils.styles import GLOBAL_CSS

st.set_page_config(
    page_title="시험 풀기",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
st.markdown("""
<style>
.top-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}
.exam-name {
    font-weight: 800;
    font-size: 1rem;
    color: #1E2235 !important;
}
.progress-txt {
    font-size: 0.88rem;
    color: #5A6480 !important;
    font-weight: 600;
}
.timer-pill {
    background: #FFF8E1;
    border: 2px solid #F4A261;
    border-radius: 20px;
    padding: 5px 14px;
    font-weight: 800;
    color: #7A4300 !important;
    font-size: 0.95rem;
    white-space: nowrap;
}
.unit-badge {
    display: inline-block;
    background: #EEF1FA;
    border: 1.5px solid #C5CAE9;
    color: #3451D1 !important;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.82rem;
    font-weight: 700;
    margin-bottom: 10px;
}
.question-box {
    background: #F0F4FF;
    border-left: 5px solid #4361EE;
    border-radius: 14px;
    padding: 18px 20px;
    margin: 10px 0 16px 0;
    font-size: 1.05rem;
    font-weight: 600;
    color: #1E2235 !important;
    line-height: 1.7;
}
.canvas-label {
    font-size: 0.85rem;
    font-weight: 800;
    color: #5A6480 !important;
    letter-spacing: 0.05em;
    margin-bottom: 6px;
}
.nav-label {
    font-size: 0.8rem;
    font-weight: 800;
    color: #5A6480 !important;
    letter-spacing: 0.05em;
    margin-bottom: 6px;
}
</style>
""", unsafe_allow_html=True)

# 세션 검사
if "selected_exam" not in st.session_state or not st.session_state["selected_exam"]:
    st.warning("먼저 홈에서 시험을 선택해주세요.")
    if st.button("🏠 홈으로"):
        st.switch_page("app.py")
    st.stop()

exam_name = st.session_state["selected_exam"]
exam = EXAMS[exam_name]
questions = exam["questions"]
total = len(questions)

for key, default in [
    ("current_question", 0), ("answers", {}),
    ("times", {}), ("drawings", {}), ("question_start_time", None)
]:
    if key not in st.session_state:
        st.session_state[key] = default

idx = st.session_state["current_question"]

# 완료
if idx >= total:
    st.session_state["exam_complete"] = True
    st.balloons()
    st.success("🎉 시험 완료!")
    st.markdown(f"**{exam_name}** · {total}문항 완료")
    n = len(st.session_state["drawings"])
    if n:
        st.info(f"✏️ {n}문항에 필기 저장됨 — 결과 분석 > 풀이 교정 탭에서 확인하세요")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 결과 분석", use_container_width=True, type="primary"):
            st.switch_page("pages/2_결과분석.py")
    with col2:
        if st.button("🏠 홈으로", use_container_width=True):
            st.switch_page("app.py")
    st.stop()

q = questions[idx]
if st.session_state["question_start_time"] is None:
    st.session_state["question_start_time"] = time.time()
elapsed = int(time.time() - st.session_state["question_start_time"])

# ── 상단 ──
col_info, col_timer = st.columns([3, 1])
with col_info:
    st.markdown(f'<div class="exam-name">{exam_name}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="progress-txt">문항 {idx+1} / {total}</div>', unsafe_allow_html=True)
with col_timer:
    st.markdown(f'<div class="timer-pill">⏱ {elapsed}초</div>', unsafe_allow_html=True)

st.progress(idx / total)

# ── 문항 ──
st.markdown(f'<div class="unit-badge">📖 {q["unit"]} &nbsp;·&nbsp; 난이도 {q["difficulty"]}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="question-box"><b>Q{q["id"]}.</b> {q["text"]}</div>', unsafe_allow_html=True)

# ── 선택지 ──
prev_answer = st.session_state["answers"].get(q["id"])
choice_labels = [f"{chr(9312+i)}  {c}" for i, c in enumerate(q["choices"])]
selected = st.radio(
    "답 선택",
    options=list(range(len(q["choices"]))),
    format_func=lambda i: choice_labels[i],
    index=prev_answer if prev_answer is not None else 0,
    key=f"radio_{q['id']}",
    label_visibility="collapsed",
)

# ── 필기 캔버스 ──
st.markdown("---")
st.markdown('<div class="canvas-label">✏️ 풀이 필기 노트</div>', unsafe_allow_html=True)

tool_col, color_col, width_col = st.columns([1, 1, 1])
with tool_col:
    mode = st.selectbox(
        "도구", ["freedraw", "line", "rect", "transform"],
        format_func=lambda x: {"freedraw":"✏️ 펜","line":"📏 선","rect":"⬜ 박스","transform":"✋ 이동"}[x],
        key=f"mode_{q['id']}", label_visibility="collapsed",
    )
with color_col:
    color = st.color_picker("색상", "#1E2235", key=f"color_{q['id']}", label_visibility="collapsed")
with width_col:
    width = st.slider("굵기", 1, 12, 3, key=f"width_{q['id']}", label_visibility="collapsed")

bg_img = None
if q["id"] in st.session_state["drawings"]:
    bg_img = PILImage.open(io.BytesIO(st.session_state["drawings"][q["id"]])).convert("RGBA")

canvas_result = st_canvas(
    fill_color="rgba(0,0,0,0)",
    stroke_width=width,
    stroke_color=color,
    background_color="#FFFFFF",
    background_image=bg_img,
    height=300,
    drawing_mode=mode,
    key=f"canvas_{q['id']}",
    display_toolbar=True,
)

# ── 저장 + 이동 ──
def save_and_go(new_idx):
    spent = int(time.time() - st.session_state["question_start_time"])
    st.session_state["times"][q["id"]] = st.session_state["times"].get(q["id"], 0) + spent
    st.session_state["answers"][q["id"]] = selected
    if canvas_result.image_data is not None:
        arr = canvas_result.image_data.astype(np.uint8)
        if arr[:, :, 3].max() > 0:
            img = PILImage.fromarray(arr)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            st.session_state["drawings"][q["id"]] = buf.getvalue()
    st.session_state["current_question"] = new_idx
    st.session_state["question_start_time"] = time.time()
    st.rerun()

st.markdown("")
col_prev, col_next = st.columns([1, 2])
with col_prev:
    if idx > 0:
        if st.button("◀ 이전", use_container_width=True):
            save_and_go(idx - 1)
with col_next:
    label = "다음 문항 ▶" if idx < total - 1 else "✅ 제출하기"
    btype = "secondary" if idx < total - 1 else "primary"
    if st.button(label, use_container_width=True, type=btype):
        save_and_go(idx + 1)

# ── 문항 바로가기 ──
st.markdown("---")
st.markdown('<div class="nav-label">문항 바로가기</div>', unsafe_allow_html=True)
cols = st.columns(min(total, 10))
for i, qi in enumerate(questions):
    answered = qi["id"] in st.session_state["answers"]
    has_draw = qi["id"] in st.session_state["drawings"]
    label = ("✓" if answered else str(i + 1)) + ("✏" if has_draw else "")
    with cols[i % min(total, 10)]:
        if st.button(label, key=f"nav_{i}", use_container_width=True,
                     type="primary" if i == idx else "secondary"):
            save_and_go(i)
