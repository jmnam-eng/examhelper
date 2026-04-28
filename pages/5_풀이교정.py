import os
import base64
import streamlit as st
from dotenv import load_dotenv
from utils.styles import GLOBAL_CSS

load_dotenv()

st.set_page_config(
    page_title="풀이 교정",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
st.markdown(
    """
    <style>
    .main { max-width: 560px; margin: 0 auto; }
    .feedback-correct {
        background: #f3fff3;
        border-left: 4px solid #4caf50;
        border-radius: 8px;
        padding: 14px;
        margin: 8px 0;
    }
    .feedback-wrong {
        background: #fff3f3;
        border-left: 4px solid #f44336;
        border-radius: 8px;
        padding: 14px;
        margin: 8px 0;
    }
    .feedback-tip {
        background: #fff8e1;
        border-left: 4px solid #ffc107;
        border-radius: 8px;
        padding: 14px;
        margin: 8px 0;
    }
    .page-preview {
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        overflow: hidden;
        margin: 8px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def pdf_to_images_base64(uploaded_file) -> list[dict]:
    """PDF 각 페이지를 PNG 이미지로 변환 후 base64 반환"""
    import fitz
    data = uploaded_file.read()
    doc = fitz.open(stream=data, filetype="pdf")
    pages = []
    for i, page in enumerate(doc):
        mat = fitz.Matrix(2.0, 2.0)  # 2x 해상도
        pix = page.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("png")
        b64 = base64.standard_b64encode(img_bytes).decode("utf-8")
        pages.append({"page": i + 1, "b64": b64, "bytes": img_bytes})
    doc.close()
    return pages


def image_to_base64(uploaded_file) -> list[dict]:
    """이미지 파일을 base64로 변환"""
    data = uploaded_file.read()
    ext = uploaded_file.name.split(".")[-1].lower()
    media_type = "image/jpeg" if ext in ("jpg", "jpeg") else "image/png"
    b64 = base64.standard_b64encode(data).decode("utf-8")
    return [{"page": 1, "b64": b64, "bytes": data, "media_type": media_type}]


def analyze_solution(api_key, pages, subject, problem_text, analysis_mode):
    import google.generativeai as genai
    from PIL import Image
    import io

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    mode_prompts = {
        "전체 분석": "틀린 부분, 비효율적인 풀이, 개선 방법을 모두 분석해주세요.",
        "오류만": "풀이에서 틀린 부분과 오류만 찾아 지적해주세요.",
        "효율성": "풀이 과정이 효율적인지 분석하고, 더 빠르거나 간단한 방법을 제시해주세요.",
    }

    problem_section = f"\n\n**문제**: {problem_text}" if problem_text.strip() else ""
    prompt = f"""학생의 {subject} 풀이 과정이 담긴 이미지입니다.{problem_section}

다음 항목으로 분석해주세요: {mode_prompts[analysis_mode]}

**분석 형식**:
## 📝 OCR 인식 결과
(이미지에서 읽은 풀이 과정 텍스트)

## ✅ 올바른 부분
(잘 된 풀이 단계)

## ❌ 오류 및 잘못된 풀이
(각 오류마다: 어느 단계에서, 어떤 오류인지, 올바른 풀이는?)

## ⚡ 효율성 개선
(더 빠르거나 간단한 풀이 방법 제안)

## 📚 정확한 모범 풀이
(처음부터 끝까지 완전한 풀이 과정)

## 💡 핵심 개념 정리
(이 문제 유형에서 꼭 기억해야 할 개념)

친근하고 격려하는 말투로, 학생이 이해하기 쉽게 설명해주세요."""

    # 이미지 + 프롬프트 구성
    content = [prompt]
    for p in pages:
        img = Image.open(io.BytesIO(p["bytes"]))
        content.append(img)

    placeholder = st.empty()
    full_response = ""
    for chunk in model.generate_content(content, stream=True):
        if chunk.text:
            full_response += chunk.text
            placeholder.markdown(full_response + "▌")
    placeholder.markdown(full_response)

    return full_response


# ── 메인 ──────────────────────────────────────────────────────────────

st.markdown("## 🔍 풀이 과정 교정")
st.caption("필기한 풀이를 AI가 읽고 오류와 개선점을 알려드립니다")
st.markdown("---")

api_key = os.environ.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("GEMINI_API_KEY가 필요합니다. `.env` 파일에 키를 설정해주세요.")
    st.code("GEMINI_API_KEY=AIza...")
    st.stop()

# 파일 업로드
st.subheader("📎 풀이 파일 업로드")
st.caption("손으로 쓴 풀이를 사진/스캔하거나 PDF로 올려주세요")

uploaded = st.file_uploader(
    "PDF, JPG, PNG 파일 지원",
    type=["pdf", "jpg", "jpeg", "png"],
    help="여러 페이지 PDF도 가능합니다",
)

pages = []
if uploaded:
    with st.spinner("파일 처리 중..."):
        try:
            if uploaded.name.lower().endswith(".pdf"):
                pages = pdf_to_images_base64(uploaded)
            else:
                pages = image_to_base64(uploaded)
            st.success(f"✅ {len(pages)}페이지 로드 완료")
        except Exception as e:
            st.error(f"파일 처리 오류: {e}")

    if pages:
        with st.expander("📄 페이지 미리보기"):
            for p in pages[:3]:
                st.image(p["bytes"], caption=f"{p['page']}페이지", use_container_width=True)
            if len(pages) > 3:
                st.caption(f"... 외 {len(pages)-3}페이지")

st.markdown("---")
st.subheader("⚙️ 분석 설정")

col1, col2 = st.columns(2)
with col1:
    subject = st.text_input(
        "과목명",
        placeholder="예: 미적분학, 유기화학, 알고리즘...",
    )
with col2:
    analysis_mode = st.selectbox(
        "분석 모드",
        ["전체 분석", "오류만", "효율성"],
        help="전체 분석: 오류+효율성 모두 / 오류만: 틀린 부분만 / 효율성: 더 나은 풀이법",
    )

problem_text = st.text_area(
    "문제 내용 (선택)",
    placeholder="풀었던 문제를 여기에 입력하면 더 정확한 분석이 가능합니다.\n예: 이차방정식 x²-5x+6=0을 인수분해로 풀어라",
    height=100,
)

st.markdown("")

if pages:
    if st.button("🔍 풀이 분석 시작", type="primary", use_container_width=True):
        st.markdown("---")
        st.subheader("📊 분석 결과")
        with st.chat_message("assistant"):
            result = analyze_solution(api_key, pages, subject, problem_text, analysis_mode)
            st.session_state["last_correction"] = result
elif not uploaded:
    st.info("풀이 파일을 업로드하면 분석 버튼이 활성화됩니다.")

# 이전 결과 표시
if not pages and "last_correction" in st.session_state:
    st.markdown("---")
    st.subheader("📊 이전 분석 결과")
    st.markdown(st.session_state["last_correction"])

st.markdown("---")

# 사용 팁
with st.expander("💡 더 정확한 분석을 위한 팁"):
    st.markdown("""
- **선명하게 찍기**: 밝은 곳에서 정면으로 촬영하세요
- **전체 풀이 포함**: 식 전개 과정을 빠짐없이 적어주세요
- **문제도 함께**: 문제 내용을 위에 입력하면 정확도가 올라갑니다
- **한 문제씩**: 여러 문제보다 한 문제씩 올리는 게 더 상세한 분석이 됩니다
    """)

col1, col2 = st.columns(2)
with col1:
    if st.button("✏️ 문제 생성으로", use_container_width=True):
        st.switch_page("pages/4_문제생성.py")
with col2:
    if st.button("🏠 홈으로", use_container_width=True):
        st.switch_page("app.py")
