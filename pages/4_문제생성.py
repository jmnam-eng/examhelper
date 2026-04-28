import os
import json
import streamlit as st
from dotenv import load_dotenv
from utils.styles import GLOBAL_CSS

load_dotenv()

st.set_page_config(
    page_title="문제 생성",
    page_icon="✏️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
st.markdown(
    """
    <style>
    .main { max-width: 540px; margin: 0 auto; }
    .upload-area {
        border: 2px dashed #4f8ef7;
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        background: #f8f9ff;
        margin: 12px 0;
    }
    .preview-card {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
        border-left: 4px solid #4f8ef7;
        font-size: 0.9rem;
    }
    .gen-option {
        background: #fff;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def extract_text_from_pdf(uploaded_file) -> str:
    try:
        import fitz  # pymupdf
        data = uploaded_file.read()
        doc = fitz.open(stream=data, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except Exception as e:
        return f"[PDF 읽기 오류: {e}]"


def extract_text_from_txt(uploaded_file) -> str:
    try:
        return uploaded_file.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return f"[텍스트 읽기 오류: {e}]"


def generate_questions(api_key, material_text, subject, grade, num_q, difficulties):
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    diff_str = ", ".join([f"{d}:{c}문항" for d, c in difficulties.items() if c > 0])

    prompt = f"""다음 학습 자료를 바탕으로 {grade} {subject} 객관식 시험 문제 {num_q}개를 생성해주세요.

**난이도 구성**: {diff_str}

**학습 자료**:
{material_text[:6000]}

**출력 형식** (반드시 아래 JSON 배열 형식으로만 출력하세요. 설명 텍스트 없이 JSON만):
[
  {{
    "id": 1,
    "unit": "단원명",
    "text": "문제 내용",
    "choices": ["선택지1", "선택지2", "선택지3", "선택지4", "선택지5"],
    "answer": 0,
    "difficulty": "하",
    "explanation": "정답 해설"
  }}
]

규칙:
- answer는 정답 선택지의 0-based 인덱스
- difficulty는 "하", "중", "상" 중 하나
- choices는 반드시 5개
- 학습 자료 내용에 충실한 문제 출제
- 문제는 명확하고 오해 없는 표현 사용"""

    response = model.generate_content(prompt)
    raw = response.text.strip()

    # JSON 파싱 (코드블록 제거)
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


# ── 메인 ──────────────────────────────────────────────────────────────

st.markdown("## ✏️ 학습자료로 문제 생성")
st.caption("PDF 또는 텍스트 파일을 올리면 AI가 시험 문제를 만들어드립니다")
st.markdown("---")

api_key = os.environ.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("GEMINI_API_KEY가 필요합니다. `.env` 파일에 키를 설정해주세요.")
    st.code("GEMINI_API_KEY=AIza...")
    st.stop()

# 파일 업로드
st.subheader("📂 학습 자료 업로드")
uploaded = st.file_uploader(
    "PDF 또는 TXT 파일을 올려주세요",
    type=["pdf", "txt"],
    help="교과서, 노트 정리본, 요약집 등 모두 가능합니다",
)

material_text = ""
if uploaded:
    with st.spinner("파일 읽는 중..."):
        if uploaded.name.endswith(".pdf"):
            material_text = extract_text_from_pdf(uploaded)
        else:
            material_text = extract_text_from_txt(uploaded)

    if material_text and not material_text.startswith("["):
        char_count = len(material_text)
        st.success(f"✅ 파일 읽기 완료 · {char_count:,}자")
        with st.expander("내용 미리보기"):
            st.text(material_text[:800] + ("..." if len(material_text) > 800 else ""))
    else:
        st.error(material_text)
        material_text = ""

# 직접 입력 옵션
with st.expander("✍️ 텍스트 직접 입력"):
    manual_text = st.text_area(
        "학습 내용을 붙여넣으세요",
        height=200,
        placeholder="예: 이차방정식은 ax²+bx+c=0 형태이며...",
    )
    if manual_text:
        material_text = manual_text

st.markdown("---")

# 생성 옵션
if material_text:
    st.subheader("⚙️ 문제 생성 설정")

    col1, col2 = st.columns(2)
    with col1:
        subject = st.text_input(
            "과목명",
            placeholder="예: 미시경제학, 유기화학, 알고리즘...",
        )
    with col2:
        grade = st.selectbox("학년", ["1학년", "2학년", "3학년", "4학년", "대학원"])

    num_q = st.slider("문항 수", min_value=5, max_value=20, value=10, step=5)

    st.caption("난이도 구성")
    col_h, col_m, col_s = st.columns(3)
    with col_h:
        cnt_easy = st.number_input("하", min_value=0, max_value=num_q, value=max(1, num_q // 4))
    with col_m:
        cnt_mid = st.number_input("중", min_value=0, max_value=num_q, value=num_q // 2)
    with col_s:
        cnt_hard = st.number_input("상", min_value=0, max_value=num_q, value=num_q - max(1, num_q // 4) - num_q // 2)

    total_selected = cnt_easy + cnt_mid + cnt_hard
    if total_selected != num_q:
        st.warning(f"난이도 합계({total_selected})가 문항 수({num_q})와 다릅니다. 자동 조정됩니다.")

    st.markdown("")
    if not subject:
        st.info("과목명을 입력하면 문제 생성 버튼이 활성화됩니다.")
    if subject and st.button("🚀 문제 생성하기", type="primary", use_container_width=True):
        difficulties = {"하": int(cnt_easy), "중": int(cnt_mid), "상": int(cnt_hard)}

        with st.spinner("AI가 문제를 생성하고 있습니다... (10~20초)"):
            try:
                questions = generate_questions(
                    api_key, material_text, subject, grade, num_q, difficulties
                )
                st.session_state["generated_exam"] = {
                    "name": f"AI 생성 {subject} 시험 ({uploaded.name if uploaded else '직접입력'})",
                    "subject": subject,
                    "grade": grade,
                    "questions": questions,
                }
                st.session_state["generated_preview"] = True
                st.success(f"✅ {len(questions)}문항 생성 완료!")
            except Exception as e:
                st.error(f"생성 중 오류: {e}")

# 생성된 문제 미리보기
if st.session_state.get("generated_preview") and "generated_exam" in st.session_state:
    exam = st.session_state["generated_exam"]
    st.markdown("---")
    st.subheader("📋 생성된 문제 미리보기")

    for q in exam["questions"]:
        with st.expander(f"Q{q['id']}. {q['text'][:50]}... [{q['difficulty']}]"):
            st.markdown(f"**{q['text']}**")
            for i, choice in enumerate(q["choices"]):
                prefix = "✅ " if i == q["answer"] else f"{chr(9312+i)} "
                st.markdown(f"{prefix}{choice}")
            st.caption(f"단원: {q['unit']} | 해설: {q.get('explanation', '')}")

    st.markdown("")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 이 문제로 시험 보기", type="primary", use_container_width=True):
            # 생성된 문제를 시험용 세션에 등록
            from data.sample_exams import EXAMS
            exam_name = exam["name"]
            EXAMS[exam_name] = exam
            st.session_state["selected_exam"] = exam_name
            st.session_state["exam_started"] = False
            st.session_state["current_question"] = 0
            st.session_state["answers"] = {}
            st.session_state["times"] = {}
            st.session_state["question_start_time"] = None
            st.session_state["exam_complete"] = False
            st.switch_page("pages/1_시험풀기.py")
    with col2:
        if st.button("🏠 홈으로", use_container_width=True):
            st.switch_page("app.py")
