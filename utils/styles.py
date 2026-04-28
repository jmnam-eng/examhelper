GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800;900&display=swap');

/* ── 기본 폰트 & 배경 ── */
html, body, [class*="css"], .stApp, .stApp * {
    font-family: 'Noto Sans KR', -apple-system, sans-serif !important;
}
.stApp {
    background-color: #EEF1FA !important;
}
.main .block-container {
    background-color: #FFFFFF;
    border-radius: 20px;
    padding: 2rem 2rem 3rem 2rem;
    max-width: 760px;
    box-shadow: 0 4px 24px rgba(60,80,180,0.08);
    margin-top: 1rem;
    margin-bottom: 2rem;
}

/* ── 모든 텍스트 강제 색상 ── */
p, span, div, h1, h2, h3, h4, h5, h6,
li, td, th, caption, small, strong, b, em,
.stMarkdown, .stMarkdown p,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] li {
    color: #1E2235 !important;
}

/* ── 제목 ── */
h1 { font-size: 2rem !important; font-weight: 900 !important; color: #1E2235 !important; }
h2 { font-size: 1.5rem !important; font-weight: 800 !important; color: #1E2235 !important; }
h3 { font-size: 1.2rem !important; font-weight: 700 !important; color: #1E2235 !important; }

/* ── 라디오 버튼 (선택지) ── */
.stRadio > label {
    color: #1E2235 !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
}
.stRadio div[role="radiogroup"] label,
.stRadio div[role="radiogroup"] p,
.stRadio div[role="radiogroup"] span {
    color: #1E2235 !important;
    font-size: 1rem !important;
    font-weight: 500 !important;
}
.stRadio div[role="radiogroup"] label:hover {
    background: #EEF1FA;
    border-radius: 8px;
}

/* ── 인풋 레이블 ── */
label, .stSelectbox label, .stTextInput label,
.stTextArea label, .stSlider label,
.stNumberInput label, .stFileUploader label,
.stColorPicker label {
    color: #1E2235 !important;
    font-weight: 700 !important;
    font-size: 0.92rem !important;
}

/* ── 입력 필드 ── */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input {
    background: #F5F7FF !important;
    color: #1E2235 !important;
    border: 2px solid #C5CAE9 !important;
    border-radius: 10px !important;
    font-size: 1rem !important;
}
.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: #4361EE !important;
    box-shadow: 0 0 0 3px rgba(67,97,238,0.12) !important;
}
.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #8892B0 !important;
}

/* ── 셀렉트박스 ── */
.stSelectbox div[data-baseweb="select"] > div {
    background: #F5F7FF !important;
    border: 2px solid #C5CAE9 !important;
    border-radius: 10px !important;
}
.stSelectbox div[data-baseweb="select"] span,
.stSelectbox div[data-baseweb="select"] div {
    color: #1E2235 !important;
    font-size: 1rem !important;
}

/* ── 버튼 ── */
.stButton > button {
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 0.55rem 1.2rem !important;
    transition: all 0.15s ease !important;
    min-height: 44px !important;
}
.stButton > button[kind="primary"] {
    background: #4361EE !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 2px 8px rgba(67,97,238,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    background: #3451D1 !important;
    box-shadow: 0 4px 16px rgba(67,97,238,0.4) !important;
}
.stButton > button[kind="secondary"] {
    background: #FFFFFF !important;
    color: #4361EE !important;
    border: 2px solid #4361EE !important;
}
.stButton > button[kind="secondary"]:hover {
    background: #EEF1FA !important;
}

/* ── 캡션 ── */
.stCaption, [data-testid="stCaptionContainer"] p,
[data-testid="stCaptionContainer"] span {
    color: #5A6480 !important;
    font-size: 0.88rem !important;
}

/* ── 알림 박스 ── */
.stSuccess > div {
    background: #E8F5E9 !important;
    border-left: 4px solid #2DC653 !important;
    border-radius: 10px !important;
}
.stSuccess p, .stSuccess span { color: #1B5E20 !important; }

.stWarning > div {
    background: #FFF8E1 !important;
    border-left: 4px solid #F4A261 !important;
    border-radius: 10px !important;
}
.stWarning p, .stWarning span { color: #5D3A00 !important; }

.stError > div {
    background: #FFEBEE !important;
    border-left: 4px solid #E63946 !important;
    border-radius: 10px !important;
}
.stError p, .stError span { color: #7B0000 !important; }

.stInfo > div {
    background: #E8EAF6 !important;
    border-left: 4px solid #4361EE !important;
    border-radius: 10px !important;
}
.stInfo p, .stInfo span { color: #1A237E !important; }

/* ── 탭 ── */
.stTabs [data-baseweb="tab-list"] {
    background: #F0F2FB !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    color: #5A6480 !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    border-radius: 10px !important;
    padding: 8px 16px !important;
}
.stTabs [aria-selected="true"] {
    background: #FFFFFF !important;
    color: #4361EE !important;
    box-shadow: 0 2px 8px rgba(67,97,238,0.12) !important;
}

/* ── 프로그레스바 ── */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #4361EE, #7B5EA7) !important;
    border-radius: 99px !important;
}
.stProgress > div > div {
    background: #E8EAF6 !important;
    border-radius: 99px !important;
}

/* ── 데이터프레임 ── */
.stDataFrame, .stDataFrame * {
    color: #1E2235 !important;
}
.stDataFrame table {
    border-radius: 10px !important;
    overflow: hidden !important;
}
.stDataFrame th {
    background: #EEF1FA !important;
    color: #1E2235 !important;
    font-weight: 700 !important;
}

/* ── 구분선 ── */
hr {
    border-color: #DDE2F0 !important;
    margin: 1.2rem 0 !important;
}

/* ── 슬라이더 ── */
.stSlider .stSlider div[data-testid="stTickBarMin"],
.stSlider .stSlider div[data-testid="stTickBarMax"] {
    color: #5A6480 !important;
}

/* ── 파일 업로더 ── */
[data-testid="stFileUploader"] section {
    background: #F5F7FF !important;
    border: 2px dashed #C5CAE9 !important;
    border-radius: 12px !important;
}
[data-testid="stFileUploader"] section span,
[data-testid="stFileUploader"] section p {
    color: #5A6480 !important;
}
[data-testid="stFileUploader"] section button {
    color: #4361EE !important;
    border-color: #4361EE !important;
}

/* ── expander ── */
[data-testid="stExpander"] summary {
    background: #F5F7FF !important;
    border-radius: 10px !important;
    padding: 0.6rem 1rem !important;
}
[data-testid="stExpander"] summary span,
[data-testid="stExpander"] summary p {
    color: #1E2235 !important;
    font-weight: 700 !important;
}

/* ── 사이드바 네비게이션 숨기기 ── */
[data-testid="stSidebarNav"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }

/* ── 스크롤바 ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #F0F2FB; }
::-webkit-scrollbar-thumb { background: #C5CAE9; border-radius: 3px; }
</style>
"""
