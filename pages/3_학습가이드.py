import os
import streamlit as st
from dotenv import load_dotenv
from data.sample_exams import EXAMS
from utils.analyzer import build_result_df, calc_unit_stats, identify_weaknesses, calc_summary
from utils.styles import GLOBAL_CSS

load_dotenv()

st.set_page_config(
    page_title="학습 가이드",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
st.markdown("""
<style>
.guide-hero {
    background: linear-gradient(135deg, #4361EE 0%, #7B5EA7 100%);
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 16px;
}
.guide-hero-score { font-size: 2.2rem; font-weight: 900; color: #FFFFFF !important; }
.guide-hero-sub { color: rgba(255,255,255,0.9) !important; font-size: 0.95rem; margin-top: 4px; }
.weak-card {
    background: #FFF0F0;
    border-left: 5px solid #E63946;
    border-radius: 10px;
    padding: 14px 16px;
    margin: 8px 0;
}
.weak-card b { color: #1E2235 !important; }
.weak-card span { color: #C00020 !important; font-weight: 700; }
.strong-card {
    background: #F0FFF4;
    border-left: 5px solid #2DC653;
    border-radius: 10px;
    padding: 14px 16px;
    margin: 8px 0;
}
.strong-card b { color: #1E2235 !important; }
.strong-card span { color: #0A6622 !important; font-weight: 700; }
.tip-card {
    background: #F0F4FF;
    border: 1.5px solid #C5CAE9;
    border-radius: 12px;
    padding: 14px 16px;
    margin: 8px 0;
}
.tip-card b { color: #3451D1 !important; }
.tip-card-body { color: #1E2235 !important; margin-top: 4px; font-size: 0.95rem; }
</style>
""", unsafe_allow_html=True)


def show_rule_based_guide(df, unit_stats, weak_units, strong_units, summary):
    st.markdown("### 📌 학습 전략")
    score = summary["점수"]
    avg_time = summary["평균시간"]
    tips = []

    if score < 60:
        tips.append(("기초 다지기", "전 단원 기본 개념부터 다시 정리하세요. 교과서 개념 정리 → 기본 문제 풀기 순서로 진행하세요."))
    elif score < 80:
        tips.append(("오답 분석", "틀린 문항의 풀이 과정을 꼭 확인하고, 같은 유형의 문제를 3개 이상 더 풀어보세요."))
    else:
        tips.append(("심화 도전", "기본기는 탄탄합니다! 난이도 '상' 문제 위주로 연습해 완성도를 높이세요."))

    if avg_time > 120:
        tips.append(("시간 단축 훈련", f"평균 {avg_time}초로 다소 느립니다. 타이머를 맞추고 문제 풀기를 습관화하세요."))
    elif avg_time < 20:
        tips.append(("신중함 훈련", f"평균 {avg_time}초로 너무 빠릅니다. 문제를 꼼꼼히 읽는 습관이 필요합니다."))

    slow_q = df.loc[df["소요시간(초)"].idxmax()]
    if slow_q["정오답"] == "오답":
        tips.append(("시간 투자 효율화", f"{slow_q['문항']}({slow_q['단원']})에서 오래 걸렸지만 틀렸습니다. 해당 단원 집중 학습이 필요합니다."))

    for title, content in tips:
        st.markdown(
            f'<div class="tip-card"><b>💡 {title}</b>'
            f'<div class="tip-card-body">{content}</div></div>',
            unsafe_allow_html=True,
        )

    if weak_units:
        st.markdown("### 📅 주간 학습 계획 (예시)")
        days = ["월", "화", "수", "목", "금", "토", "일"]
        for i, unit in enumerate(weak_units[:3]):
            day1 = days[i * 2 % 7]
            day2 = days[(i * 2 + 1) % 7]
            st.markdown(f"- **{day1}/{day2}**: {unit} 집중 복습")
        st.markdown("- **일**: 전체 복습 + 약점 문제 재풀기")


def generate_ai_guide(api_key, exam, df, unit_stats, weak_units, strong_units, summary):
    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")

        wrong_questions = df[df["정오답"] == "오답"][["문항", "단원", "소요시간(초)"]].to_dict("records")
        unit_summary = unit_stats[["단원", "정답률(%)", "평균시간(초)"]].to_dict("records")

        prompt = f"""학생의 {exam['subject']} 시험 결과를 분석하고 맞춤 학습 가이드를 작성해주세요.

**시험 정보**: {exam.get('grade', '')} {exam['subject']}
**총점**: {summary['점수']}점 ({summary['정답수']}/{summary['총문항']} 정답)
**평균 문항 소요시간**: {summary['평균시간']}초

**단원별 결과**:
{chr(10).join([f"- {u['단원']}: 정답률 {u['정답률(%)']}%, 평균 {u['평균시간(초)']}초" for u in unit_summary])}

**약점 단원**: {', '.join(weak_units) if weak_units else '없음'}
**강점 단원**: {', '.join(strong_units) if strong_units else '없음'}

**틀린 문항 목록**:
{chr(10).join([f"- {q['문항']} ({q['단원']}, {q['소요시간(초)']}초 소요)" for q in wrong_questions])}

다음을 포함한 한국어 학습 가이드를 작성해주세요:
1. 전체 성취도 평가 (2-3문장)
2. 약점 단원별 구체적 학습 방법 (각 2-3가지 팁)
3. 강점을 활용한 학습 전략
4. 2주 학습 계획 (요일별)
5. 시험 시간 관리 피드백

마크다운 형식으로 작성하고, 학생이 이해하기 쉽게 친근한 말투를 사용해주세요."""

        with st.spinner("AI가 분석 중입니다..."):
            with st.chat_message("assistant"):
                placeholder = st.empty()
                full_response = ""
                for chunk in model.generate_content(prompt, stream=True):
                    if chunk.text:
                        full_response += chunk.text
                        placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)
                st.session_state["ai_guide"] = full_response

    except Exception as e:
        st.error(f"AI 가이드 생성 중 오류 발생: {e}")
        show_rule_based_guide(df, unit_stats, weak_units, strong_units, summary)


# ── 메인 ──────────────────────────────────────────────────────────────

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

df = build_result_df(questions, answers, times)
summary = calc_summary(df)
unit_stats = calc_unit_stats(df)
weak_units, strong_units = identify_weaknesses(unit_stats)

st.markdown("## 🎯 학습 가이드")
st.caption(exam_name)
st.markdown("---")

score = summary["점수"]
st.markdown(
    f'<div class="guide-hero">'
    f'<div class="guide-hero-score">총점 {score}점</div>'
    f'<div class="guide-hero-sub">정답 {summary["정답수"]}/{summary["총문항"]} · 평균 {summary["평균시간"]}초/문항</div>'
    f'</div>',
    unsafe_allow_html=True,
)

st.subheader("🔴 집중 보완 필요 단원")
if weak_units:
    for unit in weak_units:
        row = unit_stats[unit_stats["단원"] == unit].iloc[0]
        st.markdown(
            f'<div class="weak-card"><b>{unit}</b><br>'
            f'<span>정답률 {row["정답률(%)"]}%</span>'
            f'<span style="color:#5A6480;font-weight:500"> · 평균 {row["평균시간(초)"]}초/문항</span></div>',
            unsafe_allow_html=True,
        )
else:
    st.success("약점 단원이 없습니다! 균형 잡힌 실력이에요.")

st.subheader("🟢 잘하는 단원")
if strong_units:
    for unit in strong_units:
        row = unit_stats[unit_stats["단원"] == unit].iloc[0]
        st.markdown(
            f'<div class="strong-card"><b>{unit}</b><br>'
            f'<span>정답률 {row["정답률(%)"]}%</span>'
            f'<span style="color:#5A6480;font-weight:500"> · 평균 {row["평균시간(초)"]}초/문항</span></div>',
            unsafe_allow_html=True,
        )
else:
    st.info("아직 80% 이상인 단원이 없습니다. 더 열심히 해봐요!")

st.markdown("---")
st.subheader("🤖 AI 맞춤 학습 가이드")

api_key = os.environ.get("GEMINI_API_KEY", "")

if not api_key:
    st.warning(
        "GEMINI_API_KEY가 설정되지 않았습니다.  \n"
        "`.env` 파일에 `GEMINI_API_KEY=your-key`를 추가하면 AI 가이드를 받을 수 있습니다."
    )
    show_rule_based_guide(df, unit_stats, weak_units, strong_units, summary)
else:
    if st.button("✨ AI 학습 가이드 생성", type="primary", use_container_width=True):
        generate_ai_guide(api_key, exam, df, unit_stats, weak_units, strong_units, summary)
    elif "ai_guide" in st.session_state:
        st.markdown(st.session_state["ai_guide"])
    else:
        show_rule_based_guide(df, unit_stats, weak_units, strong_units, summary)

st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("📊 결과 분석으로", use_container_width=True):
        st.switch_page("pages/2_결과분석.py")
with col2:
    if st.button("🏠 홈으로", use_container_width=True):
        st.switch_page("app.py")
