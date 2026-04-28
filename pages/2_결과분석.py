import io
import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image as PILImage
from dotenv import load_dotenv
from data.sample_exams import EXAMS
from utils.analyzer import build_result_df, calc_unit_stats, calc_summary, difficulty_stats
from utils.styles import GLOBAL_CSS

load_dotenv()

st.set_page_config(
    page_title="결과 분석",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
st.markdown(
    """
    <style>
    .metric-card {
        background: #eef2ff;
        border-radius: 14px;
        padding: 14px 10px;
        text-align: center;
        border: 1.5px solid #c5cae9;
    }
    .metric-num {
        font-size: 1.8rem;
        font-weight: 900;
        color: #3a6bd4;
        line-height: 1.2;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #445588;
        font-weight: 600;
        margin-top: 2px;
    }
    .correction-card {
        background: #f8f9ff;
        border-radius: 14px;
        padding: 16px;
        margin: 10px 0;
        border: 1.5px solid #dde8ff;
    }
    .q-label {
        font-weight: 700;
        color: #3a6bd4;
        font-size: 0.95rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if not st.session_state.get("exam_complete"):
    st.warning("완료된 시험이 없습니다. 먼저 시험을 풀어주세요.")
    if st.button("🏠 홈으로"):
        st.switch_page("app.py")
    st.stop()

exam_name = st.session_state["selected_exam"]
exam = EXAMS[exam_name]
questions = exam["questions"]
answers = st.session_state["answers"]
times = st.session_state["times"]
drawings = st.session_state.get("drawings", {})

df = build_result_df(questions, answers, times)
summary = calc_summary(df)
unit_stats = calc_unit_stats(df)
diff_stats = difficulty_stats(df)

st.markdown("## 📊 결과 분석")
st.caption(exam_name)
st.markdown("---")

tab1, tab2 = st.tabs(["📊 결과 분석", "🔍 풀이 교정"])

# ════════════════════════════════════════════
# TAB 1: 결과 분석
# ════════════════════════════════════════════
with tab1:
    score = summary["점수"]
    score_color = "#2e7d32" if score >= 80 else ("#f57c00" if score >= 60 else "#c62828")
    grade = "우수" if score >= 80 else ("보통" if score >= 60 else "미흡")

    col1, col2, col3, col4 = st.columns(4)
    for col, num, label in [
        (col1, f'<span style="color:{score_color}">{score}</span>', "점수"),
        (col2, f"{summary['정답수']}/{summary['총문항']}", "정답"),
        (col3, str(summary["평균시간"]), "평균(초)"),
        (col4, grade, "등급"),
    ]:
        with col:
            st.markdown(
                f'<div class="metric-card"><div class="metric-num">{num}</div>'
                f'<div class="metric-label">{label}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("")

    # 문항별 소요시간
    st.subheader("⏱ 문항별 소요 시간")
    fig_time = px.bar(
        df, x="문항", y="소요시간(초)",
        color="정오답",
        color_discrete_map={"정답": "#43a047", "오답": "#e53935"},
        text="소요시간(초)", height=280,
    )
    fig_time.update_layout(
        plot_bgcolor="#f8f9ff", paper_bgcolor="#f8f9ff",
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        font=dict(family="Noto Sans KR", color="#1a1a2e"),
        xaxis_title="", yaxis_title="초",
    )
    fig_time.update_traces(textposition="outside")
    st.plotly_chart(fig_time, use_container_width=True)

    # 단원별 정답률
    st.subheader("📚 단원별 정답률")
    fig_unit = px.bar(
        unit_stats, x="정답률(%)", y="단원", orientation="h",
        text="정답률(%)",
        color="정답률(%)",
        color_continuous_scale=["#e53935", "#ff9800", "#43a047"],
        range_color=[0, 100],
        height=max(200, len(unit_stats) * 52),
    )
    fig_unit.update_layout(
        plot_bgcolor="#f8f9ff", paper_bgcolor="#f8f9ff",
        margin=dict(l=0, r=0, t=10, b=0),
        coloraxis_showscale=False,
        font=dict(family="Noto Sans KR", color="#1a1a2e"),
        xaxis=dict(range=[0, 115]),
    )
    fig_unit.update_traces(texttemplate="%{text}%", textposition="outside")
    st.plotly_chart(fig_unit, use_container_width=True)

    # 난이도별 정답률
    st.subheader("🎯 난이도별 정답률")
    order = ["하", "중", "상"]
    diff_stats["난이도"] = pd.Categorical(diff_stats["난이도"], categories=order, ordered=True)
    diff_stats = diff_stats.sort_values("난이도")
    fig_diff = go.Figure(go.Bar(
        x=diff_stats["난이도"],
        y=diff_stats["정답률(%)"],
        text=diff_stats["정답률(%)"].astype(str) + "%",
        textposition="outside",
        marker_color=["#66bb6a", "#ffa726", "#ef5350"],
    ))
    fig_diff.update_layout(
        plot_bgcolor="#f8f9ff", paper_bgcolor="#f8f9ff",
        height=240, margin=dict(l=0, r=0, t=10, b=0),
        font=dict(family="Noto Sans KR", color="#1a1a2e"),
        yaxis=dict(range=[0, 115]),
    )
    st.plotly_chart(fig_diff, use_container_width=True)

    # 문항별 상세
    st.subheader("📋 문항별 상세")
    st.dataframe(
        df[["문항", "단원", "난이도", "소요시간(초)", "정오답", "내답", "정답"]],
        use_container_width=True, hide_index=True,
    )

    st.markdown("")
    if st.button("🎯 학습 가이드 보기", use_container_width=True, type="primary"):
        st.switch_page("pages/3_학습가이드.py")

# ════════════════════════════════════════════
# TAB 2: 풀이 교정
# ════════════════════════════════════════════
with tab2:
    api_key = os.environ.get("GEMINI_API_KEY", "")

    if not drawings:
        st.info("시험 중 필기한 내용이 없습니다.\n\n다음 시험에서 ✏️ 풀이 필기 노트에 풀이 과정을 작성하면 여기서 교정을 받을 수 있습니다.")
    else:
        st.markdown(f"**✏️ 필기가 저장된 문항: {len(drawings)}개**")
        st.caption("문항을 선택하면 AI가 풀이 과정을 분석합니다.")

        if not api_key:
            st.error("GEMINI_API_KEY가 필요합니다. `.env` 파일에 설정해주세요.")
        else:
            # 문항 선택
            q_ids_with_drawings = list(drawings.keys())
            q_map = {q["id"]: q for q in questions}

            selected_qid = st.selectbox(
                "교정할 문항 선택",
                options=q_ids_with_drawings,
                format_func=lambda qid: f"Q{qid}. {q_map[qid]['text'][:35]}..." if qid in q_map else f"Q{qid}",
            )

            if selected_qid:
                q_info = q_map.get(selected_qid)
                user_ans = answers.get(selected_qid)
                is_correct = user_ans == q_info["answer"] if user_ans is not None else False

                col_img, col_info = st.columns([2, 1])
                with col_img:
                    drawing_bytes = drawings[selected_qid]
                    st.image(drawing_bytes, caption=f"Q{selected_qid} 필기", use_container_width=True)
                with col_info:
                    st.markdown(
                        f'<div class="correction-card">'
                        f'<div class="q-label">Q{selected_qid}</div>'
                        f'<div style="font-size:0.85rem;color:#1a1a2e;margin-top:6px">{q_info["unit"]}</div>'
                        f'<div style="margin-top:8px;font-weight:700;color:{"#2e7d32" if is_correct else "#c62828"}">'
                        f'{"✅ 정답" if is_correct else "❌ 오답"}</div>'
                        f'<div style="font-size:0.82rem;color:#445588;margin-top:4px">'
                        f'소요: {times.get(selected_qid, 0)}초</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                problem_text = f"{q_info['text']}\n\n선택지: {', '.join(q_info['choices'])}\n정답: {q_info['choices'][q_info['answer']]}"

                if st.button("🔍 이 풀이 교정받기", type="primary", use_container_width=True, key="correct_btn"):
                    _run_correction(api_key, drawing_bytes, q_info["unit"], problem_text, selected_qid)
                elif f"correction_{selected_qid}" in st.session_state:
                    st.markdown("---")
                    st.markdown(st.session_state[f"correction_{selected_qid}"])

            # 전체 일괄 교정
            if len(drawings) > 1:
                st.markdown("---")
                if st.button("📋 틀린 문항 전체 교정", use_container_width=True, key="batch_btn"):
                    wrong_with_drawings = [
                        qid for qid in drawings
                        if answers.get(qid) != q_map[qid]["answer"]
                    ]
                    if wrong_with_drawings:
                        for qid in wrong_with_drawings:
                            q_info = q_map[qid]
                            problem_text = f"{q_info['text']}\n\n정답: {q_info['choices'][q_info['answer']]}"
                            st.markdown(f"#### Q{qid}. {q_info['text'][:40]}...")
                            _run_correction(api_key, drawings[qid], q_info["unit"], problem_text, qid)
                            st.markdown("---")
                    else:
                        st.success("필기된 문항은 모두 정답입니다!")

    st.markdown("")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎯 학습 가이드", use_container_width=True):
            st.switch_page("pages/3_학습가이드.py")
    with col2:
        if st.button("🏠 홈으로", use_container_width=True):
            st.switch_page("app.py")


def _run_correction(api_key, drawing_bytes, subject, problem_text, qid):
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    img = PILImage.open(io.BytesIO(drawing_bytes))

    prompt = f"""학생의 {subject} 풀이 필기 이미지입니다.

**문제**: {problem_text}

아래 형식으로 분석해주세요:

## 📝 필기 인식
(이미지에서 읽은 풀이 과정)

## ✅ 잘된 부분
(올바른 풀이 단계)

## ❌ 오류 / 개선점
(틀린 부분, 비효율적 부분 각각: 어느 단계에서 → 무엇이 잘못 → 올바른 방법)

## 📚 모범 풀이
(정확하고 효율적인 완전한 풀이)

## 💡 기억할 개념
(이 유형 문제에서 핵심 포인트)

학생이 이해하기 쉽게, 친근하고 격려하는 말투로 작성해주세요."""

    with st.spinner(f"Q{qid} 분석 중..."):
        with st.chat_message("assistant"):
            placeholder = st.empty()
            full = ""
            for chunk in model.generate_content([prompt, img], stream=True):
                if chunk.text:
                    full += chunk.text
                    placeholder.markdown(full + "▌")
            placeholder.markdown(full)
            st.session_state[f"correction_{qid}"] = full
