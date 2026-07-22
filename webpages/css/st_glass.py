import streamlit as st


def liquid_glass():
    """전역 리퀴드 글라스 테마.

    컴포넌트 '종류'(data-testid / data-baseweb)를 셀렉터로 잡기 때문에
    같은 종류의 위젯(차트, 표, 폼, 버튼, 입력창 등)이 새로 추가되면
    별도 작업 없이 자동으로 같은 효과가 적용된다.

    index.py에서 require_login() 전에 한 번만 호출하면
    로그인 화면을 포함한 모든 페이지에 적용된다. (페이지별 호출 불필요)

    st.container()를 유리 카드로 만들고 싶으면 key를 "glass"로 시작하게 주면 된다:
        with st.container(key="glass_signup_card"):
            ...
    """
    st.markdown("""
    <style>
    /* ── 글라스 공통 토큰: 값을 여기서만 바꾸면 전체가 함께 바뀐다 ── */
    :root {
        --glass-bg: rgba(255, 255, 255, 0.06);
        --glass-bg-hover: rgba(255, 255, 255, 0.12);
        --glass-bg-active: rgba(255, 255, 255, 0.09);
        --glass-border: rgba(255, 255, 255, 0.14);
        --glass-border-strong: rgba(255, 255, 255, 0.28);
        --glass-blur: blur(24px) saturate(160%);
        --glass-blur-sm: blur(12px) saturate(140%);
        --glass-accent: rgba(59, 130, 246, 0.55);
        --glass-shadow:
            0 8px 32px rgba(0, 0, 0, 0.35),
            inset 0 1px 0 rgba(255, 255, 255, 0.25),
            inset 0 -1px 0 rgba(255, 255, 255, 0.05);
        --glass-shadow-sm:
            0 4px 16px rgba(0, 0, 0, 0.25),
            inset 0 1px 0 rgba(255, 255, 255, 0.25),
            inset 0 -1px 0 rgba(255, 255, 255, 0.05);
        --glass-highlight: linear-gradient(
            180deg,
            rgba(255, 255, 255, 0.10) 0%,
            rgba(255, 255, 255, 0.02) 40%,
            transparent 100%);
    }

    /* ── 배경: 은은한 컬러 글로우 (글라스 블러가 비칠 대상) ────── */
    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(1200px 600px at 15% -10%, rgba(37, 99, 235, 0.22), transparent 60%),
            radial-gradient(1000px 500px at 85% 10%, rgba(45, 212, 191, 0.16), transparent 60%),
            radial-gradient(800px 500px at 25% 55%, rgba(59, 130, 246, 0.13), transparent 65%),
            radial-gradient(800px 500px at 75% 65%, rgba(45, 212, 191, 0.11), transparent 65%),
            radial-gradient(900px 600px at 50% 110%, rgba(99, 102, 241, 0.14), transparent 60%),
            #0B1017;
    }

    /* ── 사이드바(측면탭): 얇은 유리 ─────────────────────────── */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: var(--glass-blur);
        -webkit-backdrop-filter: var(--glass-blur);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* ── 패널형 컴포넌트: 차트 / 표 / 폼 / 익스팬더 / 메트릭 ────
       새 종류를 유리 패널로 만들려면 아래 두 셀렉터 목록에만 추가하면 된다. */
    [data-testid="stPlotlyChart"],
    [data-testid="stVegaLiteChart"],
    [data-testid="stDataFrame"],  /* st.data_editor도 stDataFrame으로 렌더링됨 */
    [data-testid="stTable"],
    [data-testid="stForm"],
    [data-testid="stExpander"],
    [data-testid="stMetric"],
    [data-testid="stFileUploaderDropzone"],
    [data-testid="stChatMessage"],
    [class*="st-key-glass"] {
        position: relative;
        overflow: hidden;
        background: var(--glass-bg);
        backdrop-filter: var(--glass-blur);
        -webkit-backdrop-filter: var(--glass-blur);
        border: 1px solid var(--glass-border);
        border-radius: 20px;
        box-shadow: var(--glass-shadow);
    }

    /* 유리 표면 반사광 (위쪽이 밝은 스펙큘러 하이라이트) */
    [data-testid="stPlotlyChart"]::before,
    [data-testid="stVegaLiteChart"]::before,
    [data-testid="stDataFrame"]::before,
    [data-testid="stTable"]::before,
    [data-testid="stForm"]::before,
    [data-testid="stExpander"]::before,
    [data-testid="stMetric"]::before,
    [data-testid="stFileUploaderDropzone"]::before,
    [data-testid="stChatMessage"]::before,
    [class*="st-key-glass"]::before {
        content: "";
        position: absolute;
        inset: 0;
        background: var(--glass-highlight);
        pointer-events: none;
        z-index: 1;
    }

    /* 패널별 여백 미세 조정 */
    [data-testid="stPlotlyChart"],
    [data-testid="stVegaLiteChart"] { padding: 12px 10px 6px 6px; }
    [data-testid="stForm"]          { padding: 18px 18px 12px 18px; }
    [data-testid="stMetric"]        { padding: 18px 20px 16px 20px; }
    [data-testid="stChatMessage"]   { padding: 12px 16px; }
    [class*="st-key-glass"]         { padding: 16px 18px; }

    /* 익스팬더 내부의 기본 테두리/배경 제거 (유리 패널과 이중 테두리 방지) */
    [data-testid="stExpander"] details {
        border: none;
        background: transparent;
    }

    /* ── 알림 박스: st.info / st.success / st.warning / st.error ──
       종류별 색상이 의미를 가지므로 배경색은 Streamlit 기본(반투명 색 틴트)을
       그대로 두고, 블러·테두리·그림자만 얹어 '컬러 유리'로 만든다.
       테두리는 글자색(의미 색)을 25% 투명도로 따라간다. */
    [data-testid="stAlertContainer"] {
        backdrop-filter: var(--glass-blur);
        -webkit-backdrop-filter: var(--glass-blur);
        border: 1px solid rgba(255, 255, 255, 0.10);
        border: 1px solid color-mix(in srgb, currentColor 25%, transparent);
        border-radius: 16px;
        box-shadow: var(--glass-shadow-sm);
    }

    /* st.dialog 모달 표면 (배경이 어두워지므로 유리를 살짝 진하게) */
    [data-testid="stDialog"] [role="dialog"] {
        background: rgba(20, 26, 36, 0.75);
        backdrop-filter: var(--glass-blur);
        -webkit-backdrop-filter: var(--glass-blur);
        border: 1px solid var(--glass-border);
        border-radius: 20px;
        box-shadow: var(--glass-shadow);
    }

    /* ── 버튼: st.button / st.download_button / 폼 제출 / 팝오버 ── */
    [data-testid="stButton"] > button,
    [data-testid="stDownloadButton"] > button,
    [data-testid="stFormSubmitButton"] > button,
    [data-testid="stPopover"] > button {
        background: var(--glass-highlight), var(--glass-bg);
        backdrop-filter: var(--glass-blur-sm);
        -webkit-backdrop-filter: var(--glass-blur-sm);
        border: 1px solid var(--glass-border);
        border-radius: 14px;
        color: rgba(255, 255, 255, 0.9);
        box-shadow: var(--glass-shadow-sm);
        transition: background 0.2s ease, border-color 0.2s ease, transform 0.1s ease;
    }
    [data-testid="stButton"] > button:hover,
    [data-testid="stDownloadButton"] > button:hover,
    [data-testid="stFormSubmitButton"] > button:hover,
    [data-testid="stPopover"] > button:hover {
        background: var(--glass-highlight), var(--glass-bg-hover);
        border-color: var(--glass-border-strong);
        color: #fff;
    }
    [data-testid="stButton"] > button:active,
    [data-testid="stDownloadButton"] > button:active,
    [data-testid="stFormSubmitButton"] > button:active,
    [data-testid="stPopover"] > button:active {
        transform: scale(0.98);
        background: var(--glass-highlight), var(--glass-bg-active);
    }
    [data-testid="stButton"] > button:focus-visible,
    [data-testid="stDownloadButton"] > button:focus-visible,
    [data-testid="stFormSubmitButton"] > button:focus-visible,
    [data-testid="stPopover"] > button:focus-visible {
        outline: none;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.25), var(--glass-shadow-sm);
    }

    /* primary 계열 버튼(type="primary")은 파란 유리 틴트 */
    [data-testid="stButton"] > button[kind*="primary"],
    [data-testid="stFormSubmitButton"] > button[kind*="primary"] {
        background: var(--glass-highlight), rgba(37, 99, 235, 0.35);
        border-color: rgba(59, 130, 246, 0.45);
    }
    [data-testid="stButton"] > button[kind*="primary"]:hover,
    [data-testid="stFormSubmitButton"] > button[kind*="primary"]:hover {
        background: var(--glass-highlight), rgba(37, 99, 235, 0.50);
        border-color: rgba(59, 130, 246, 0.65);
    }

    /* ── 입력창: 텍스트/숫자/날짜/시간/셀렉트 등 ──
       한 줄 입력과 셀렉트는 BaseWeb(input/select)으로 렌더링되므로
       새 입력 위젯도 자동으로 유리가 된다.
       st.text_area는 BaseWeb이 아니라 stTextArea testid의 textarea로
       렌더링되므로(Streamlit 1.60 기준) 따로 잡는다. */
    .stApp [data-baseweb="input"],
    .stApp [data-testid="stTextArea"] textarea,
    .stApp [data-baseweb="select"] > div {
        background: var(--glass-bg);
        backdrop-filter: var(--glass-blur-sm);
        -webkit-backdrop-filter: var(--glass-blur-sm);
        border: 1px solid var(--glass-border);
        border-radius: 12px;
        box-shadow: var(--glass-shadow-sm);
        transition: border-color 0.2s ease, background 0.2s ease;
    }
    .stApp [data-baseweb="input"] input,
    .stApp [data-baseweb="select"] input {
        background: transparent;
        color: rgba(255, 255, 255, 0.92);
    }
    .stApp [data-testid="stTextArea"] textarea {
        color: rgba(255, 255, 255, 0.92);
    }
    .stApp [data-baseweb="input"]:focus-within,
    .stApp [data-testid="stTextArea"] textarea:focus,
    .stApp [data-baseweb="select"] > div:focus-within {
        outline: none;
        border-color: var(--glass-accent);
        background: var(--glass-bg-hover);
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.18), var(--glass-shadow-sm);
    }

    /* 채팅 입력창 (st.chat_input) */
    [data-testid="stChatInput"] {
        background: var(--glass-bg);
        backdrop-filter: var(--glass-blur-sm);
        -webkit-backdrop-filter: var(--glass-blur-sm);
        border: 1px solid var(--glass-border);
        border-radius: 14px;
        box-shadow: var(--glass-shadow-sm);
    }

    /* 셀렉트박스 드롭다운 목록 (body 포털에 뜨므로 .stApp 밖) */
    [data-baseweb="popover"] [role="listbox"] {
        background: rgba(20, 26, 36, 0.88);
        backdrop-filter: var(--glass-blur);
        -webkit-backdrop-filter: var(--glass-blur);
        border: 1px solid var(--glass-border);
        border-radius: 12px;
    }
    </style>
    """, unsafe_allow_html=True)
