import os
import base64
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from modules.db import get_connection, init_db
from modules.posts import get_all_posts, get_post, create_post, delete_post
from modules.comments import get_comments, create_comment, delete_comment
from modules.suggestions import (
    create_suggestion, get_all_suggestions,
    mark_as_read, delete_suggestion, get_unread_count
)

load_dotenv()

# Streamlit Cloud 시크릿 → os.environ 동기화 (로컬 .env 없을 때 사용)
try:
    for _k, _v in st.secrets.items():
        if isinstance(_v, str):
            os.environ.setdefault(_k, _v)
except Exception:
    pass

ACCESS_CODE    = os.getenv('ACCESS_CODE', '').strip()
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin1234')

init_db()

BASE_DIR = os.path.dirname(__file__)

def _b64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return ""

LOGO_WHITE_B64 = _b64(os.path.join(BASE_DIR, "assets", "logo_white.png"))
LOGO_BLUE_B64  = _b64(os.path.join(BASE_DIR, "assets", "logo_blue.png"))

def get_stats():
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute('SELECT COUNT(*) AS cnt FROM posts')
    posts = cur.fetchone()['cnt']
    cur.execute('SELECT COUNT(*) AS cnt FROM comments')
    comments = cur.fetchone()['cnt']
    conn.close()
    return posts, comments

# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="남부 라운지 · HYUNDAI",
    page_icon="🅗",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap');

* {{ font-family: 'Noto Sans KR', -apple-system, sans-serif !important; }}

/* ── 전역 ── */
.stApp {{ background: #F0F2F7; }}
/* 헤더 배경을 배너와 동일한 다크 네이비로 통일 */
header[data-testid="stHeader"] {{
    background: linear-gradient(130deg, #002C5F 0%, #004080 55%, #005090 100%) !important;
    border-bottom: none !important;
    box-shadow: none !important;
}}
/* Deploy 버튼, 상태 위젯, 메인메뉴, footer 제거 */
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
.stDeployButton,
#MainMenu,
footer {{
    display: none !important;
    visibility: hidden !important;
}}

.block-container {{
    padding: 0 2.5rem 3rem 2.5rem !important;
    max-width: 100% !important;
}}

/* ══════════════════════════════════════
   사이드바
══════════════════════════════════════ */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #001f45 0%, #002C5F 40%, #003570 100%) !important;
    border-right: none !important;
    box-shadow: 3px 0 20px rgba(0,0,0,0.18) !important;
}}
section[data-testid="stSidebar"] > div {{
    padding: 1.5rem 1.2rem !important;
}}
section[data-testid="stSidebar"] .stButton > button {{
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: rgba(255,255,255,0.72) !important;
    border-radius: 10px !important;
    font-size: 0.87rem !important;
    font-weight: 400 !important;
    text-align: left !important;
    width: 100% !important;
    padding: 0.52rem 0.9rem !important;
    margin-bottom: 0.25rem !important;
    transition: all 0.18s ease !important;
    letter-spacing: 0.01em !important;
}}
section[data-testid="stSidebar"] .stButton > button:hover {{
    background: rgba(255,255,255,0.1) !important;
    color: white !important;
    border-color: rgba(255,255,255,0.22) !important;
}}
section[data-testid="stSidebar"] .stButton > button[kind="primary"] {{
    background: rgba(0,170,210,0.18) !important;
    border-color: rgba(0,170,210,0.5) !important;
    color: #4dd9f5 !important;
    font-weight: 600 !important;
}}
section[data-testid="stSidebar"] .stTextInput > div > div > input {{
    background: #ffffff !important;
    border-color: rgba(0,44,95,0.35) !important;
    color: #111827 !important;
    border-radius: 8px !important;
    font-size: 0.85rem !important;
}}
section[data-testid="stSidebar"] .stTextInput > div > div > input::placeholder {{
    color: #9ca3af !important;
}}
section[data-testid="stSidebar"] label {{
    color: rgba(255,255,255,0.5) !important;
    font-size: 0.78rem !important;
}}

/* ══════════════════════════════════════
   메인 배너
══════════════════════════════════════ */
.main-banner {{
    background: linear-gradient(130deg, #002C5F 0%, #004080 55%, #005090 100%);
    padding: 1.6rem 2.5rem;
    margin: 0 -2.5rem 2rem -2.5rem;
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 4px 20px rgba(0,44,95,0.2);
}}
.main-banner::before {{
    content: '';
    position: absolute;
    right: -80px; top: -80px;
    width: 280px; height: 280px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(0,170,210,0.12) 0%, transparent 70%);
    pointer-events: none;
}}
.main-banner::after {{
    content: '';
    position: absolute;
    left: 45%; bottom: -60px;
    width: 200px; height: 200px;
    border-radius: 50%;
    background: rgba(255,255,255,0.03);
    pointer-events: none;
}}
.banner-left {{ position: relative; z-index: 1; }}
.banner-title {{
    font-size: 1.5rem;
    font-weight: 700;
    color: white;
    margin: 0 0 0.2rem;
    letter-spacing: -0.3px;
}}
.banner-title em {{
    color: #00ccf0;
    font-style: normal;
}}
.banner-sub {{
    font-size: 0.78rem;
    color: rgba(255,255,255,0.48);
    letter-spacing: 0.4px;
    font-weight: 300;
}}
.banner-right {{ position: relative; z-index: 1; text-align: right; }}
.banner-right img {{ height: 20px; opacity: 0.88; display: block; margin-bottom: 0.5rem; margin-left: auto; }}
.banner-section-chip {{
    display: inline-block;
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.18);
    color: rgba(255,255,255,0.7);
    font-size: 0.72rem;
    padding: 0.2rem 0.7rem;
    border-radius: 20px;
    font-weight: 400;
}}

/* ══════════════════════════════════════
   공통 카드
══════════════════════════════════════ */
.card {{
    background: white;
    border-radius: 14px;
    border: 1px solid #E8EBF2;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    transition: all 0.18s ease;
    overflow: hidden;
}}
.card:hover {{
    box-shadow: 0 6px 22px rgba(0,44,95,0.1);
    border-color: #D0D8EF;
    transform: translateY(-1px);
}}

/* ══════════════════════════════════════
   게시글 카드
══════════════════════════════════════ */
.post-card {{
    background: white;
    border-radius: 14px;
    border: 1px solid #E8EBF2;
    box-shadow: 0 2px 8px rgba(0,0,0,0.045);
    padding: 1.1rem 1.4rem 1rem;
    margin-bottom: 0.6rem;
    position: relative;
    overflow: hidden;
    transition: all 0.18s ease;
}}
.post-card::before {{
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    background: linear-gradient(180deg, #002C5F, #00AAD2);
    border-radius: 14px 0 0 14px;
}}
.post-card:hover {{
    box-shadow: 0 6px 22px rgba(0,44,95,0.1);
    border-color: #c8d4ef;
    transform: translateY(-1px);
}}
.post-title {{
    font-size: 0.95rem;
    font-weight: 600;
    color: #1a1f36;
    margin: 0 0 0.5rem;
    line-height: 1.45;
}}
.post-meta {{
    font-size: 0.73rem;
    color: #9ca3af;
    display: flex;
    align-items: center;
    gap: 0.55rem;
    flex-wrap: wrap;
}}
.tag-nick {{
    color: #1a4fa0;
    font-weight: 600;
    background: #EEF3FF;
    padding: 0.12rem 0.55rem;
    border-radius: 20px;
    font-size: 0.71rem;
}}
.tag-cmt {{
    color: #059669;
    background: #ECFDF5;
    padding: 0.12rem 0.5rem;
    border-radius: 20px;
    font-size: 0.71rem;
    font-weight: 500;
}}
.tag-new {{
    color: #dc2626;
    background: #FEF2F2;
    padding: 0.12rem 0.5rem;
    border-radius: 20px;
    font-size: 0.68rem;
    font-weight: 700;
}}

/* ══════════════════════════════════════
   게시글 상세
══════════════════════════════════════ */
.detail-hd {{
    background: white;
    border-radius: 14px;
    border: 1px solid #E8EBF2;
    border-top: 3px solid #002C5F;
    padding: 1.5rem 1.6rem 1.2rem;
    margin-bottom: 0.8rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}}
.detail-title {{
    font-size: 1.2rem;
    font-weight: 700;
    color: #111827;
    margin: 0 0 0.7rem;
    line-height: 1.4;
}}
.detail-meta {{
    font-size: 0.77rem;
    color: #9ca3af;
    display: flex;
    gap: 0.7rem;
    align-items: center;
    flex-wrap: wrap;
}}
.detail-body {{
    background: white;
    border-radius: 14px;
    border: 1px solid #E8EBF2;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    font-size: 0.93rem;
    color: #374151;
    line-height: 1.8;
    white-space: pre-wrap;
    min-height: 80px;
}}

/* ══════════════════════════════════════
   댓글
══════════════════════════════════════ */
.comment-item {{
    background: #F8FAFF;
    border: 1px solid #EBF0FA;
    border-radius: 10px;
    padding: 0.85rem 1.1rem;
    margin-bottom: 0.45rem;
}}
.c-nick {{ color: #002C5F; font-weight: 600; font-size: 0.78rem; }}
.c-time {{ color: #c4cad8; font-size: 0.73rem; }}
.c-body {{ font-size: 0.88rem; color: #374151; line-height: 1.6; margin-top: 0.3rem; }}

/* ══════════════════════════════════════
   건의함
══════════════════════════════════════ */
.sg-notice {{
    background: linear-gradient(135deg, #FFFBEB, #FFF3CC);
    border: 1px solid #FDE68A;
    border-radius: 12px;
    padding: 0.9rem 1.2rem;
    margin-bottom: 1.3rem;
    font-size: 0.83rem;
    color: #854D0E;
    line-height: 1.5;
}}

/* ══════════════════════════════════════
   섹션 제목
══════════════════════════════════════ */
.sec-hd {{
    font-size: 1rem;
    font-weight: 700;
    color: #111827;
    margin: 0 0 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding-bottom: 0.6rem;
    border-bottom: 2px solid #EEF2FF;
}}
.sec-hd .accent {{ color: #002C5F; }}

/* ══════════════════════════════════════
   통계 카드 (사이드바용)
══════════════════════════════════════ */
.sb-stat {{
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 10px;
    padding: 0.65rem 0.9rem;
    margin-bottom: 0.35rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.8rem;
    color: rgba(255,255,255,0.6);
}}
.sb-stat .val {{
    font-size: 0.95rem;
    font-weight: 700;
    color: white;
}}

/* ══════════════════════════════════════
   사이드바 레이블
══════════════════════════════════════ */
.sb-label {{
    font-size: 0.68rem;
    color: rgba(255,255,255,0.35);
    letter-spacing: 0.8px;
    font-weight: 500;
    margin: 1rem 0 0.4rem;
    text-transform: uppercase;
}}
.sb-nick-chip {{
    background: rgba(0,170,210,0.15);
    border: 1px solid rgba(0,170,210,0.35);
    color: #4dd9f5;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 600;
    display: inline-block;
    margin-bottom: 0.5rem;
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}}
.sb-divider {{
    border: none;
    border-top: 1px solid rgba(255,255,255,0.1);
    margin: 0.9rem 0;
}}

/* ══════════════════════════════════════
   게이트 화면
══════════════════════════════════════ */
.gate-outer {{
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding-top: 4rem;
}}
.gate-card {{
    background: white;
    border-radius: 22px;
    padding: 2.5rem 2rem 2rem;
    box-shadow: 0 12px 50px rgba(0,44,95,0.12);
    border: 1px solid #E8EBF2;
    width: 100%;
    text-align: center;
}}

.gate-icon {{ font-size: 2.4rem; margin-bottom: 0.8rem; }}
.gate-title {{
    font-size: 1.25rem;
    font-weight: 700;
    color: #111827;
    margin-bottom: 0.4rem;
}}
.gate-sub {{
    font-size: 0.82rem;
    color: #9ca3af;
    margin-bottom: 1.8rem;
    line-height: 1.6;
}}

/* ══════════════════════════════════════
   빈 상태
══════════════════════════════════════ */
.empty-state {{
    text-align: center;
    padding: 3.5rem 1rem;
}}
.empty-state .ei {{ font-size: 2.5rem; margin-bottom: 0.5rem; }}
.empty-state p {{ font-size: 0.87rem; color: #9ca3af; line-height: 1.6; }}

/* ══════════════════════════════════════
   입력 / 버튼 공통
══════════════════════════════════════ */
.stTextInput > div > div > input {{
    background: #ffffff !important;
    border-radius: 10px !important;
    border-color: #E5E7EB !important;
    font-size: 0.9rem !important;
}}
.stTextInput > div > div > input:focus {{
    background: #ffffff !important;
    border-color: #002C5F !important;
    box-shadow: 0 0 0 3px rgba(0,44,95,0.08) !important;
}}
.stTextArea > div > div > textarea {{
    background: #ffffff !important;
    border-radius: 10px !important;
    border-color: #E5E7EB !important;
    font-size: 0.9rem !important;
}}
.stTextArea > div > div > textarea:focus {{
    background: #ffffff !important;
    border-color: #002C5F !important;
    box-shadow: 0 0 0 3px rgba(0,44,95,0.08) !important;
}}
.stButton > button {{
    border-radius: 10px !important;
    font-weight: 500 !important;
    font-size: 0.87rem !important;
    transition: all 0.18s ease !important;
    border: 1.5px solid transparent !important;
}}
.stButton > button[kind="primary"] {{
    background: #002C5F !important;
    color: white !important;
    border-color: #002C5F !important;
    box-shadow: 0 3px 12px rgba(0,44,95,0.22) !important;
}}
.stButton > button[kind="primary"]:hover {{
    background: #003d7a !important;
    box-shadow: 0 5px 18px rgba(0,44,95,0.3) !important;
    transform: translateY(-1px) !important;
}}
.stButton > button[kind="secondary"] {{
    background: white !important;
    color: #374151 !important;
    border-color: #E5E7EB !important;
}}
.stButton > button[kind="secondary"]:hover {{
    border-color: #002C5F !important;
    color: #002C5F !important;
    background: #F0F4FF !important;
}}
hr.sect {{ border: none; border-top: 1px solid #EEF0F6; margin: 1.2rem 0; }}
.stSuccess, .stWarning, .stError, .stInfo {{ border-radius: 10px !important; }}
</style>
""", unsafe_allow_html=True)


# ── 세션 상태 ─────────────────────────────────────────────────
def init_session():
    defaults = {
        'page': 'board',
        'selected_post_id': None,
        'admin_auth': False,
        'access_ok': not bool(ACCESS_CODE),
        'nickname': '',
        'write_mode': False,
        'change_nickname': False,
        'my_posts': set(),
        'my_comments': set(),
        'board_sort': 'latest',
        'sg_submitted': False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()


def nav(page, post_id=None):
    st.session_state.page = page
    st.session_state.selected_post_id = post_id
    st.session_state.write_mode = False


def is_my_post(pid):
    return pid in st.session_state.my_posts or st.session_state.admin_auth

def is_my_comment(cid):
    return cid in st.session_state.my_comments or st.session_state.admin_auth


# ══════════════════════════════════════════════════════════════
# 사이드바
# ══════════════════════════════════════════════════════════════
def render_sidebar():
    with st.sidebar:
        # 로고
        st.markdown(
            f'<div style="text-align:center;padding:0.5rem 0 1.2rem;">'
            f'<img src="data:image/png;base64,{LOGO_WHITE_B64}" style="height:22px;opacity:0.92;">'
            f'</div>',
            unsafe_allow_html=True
        )

        # 커뮤니티 이름
        st.markdown(
            '<div style="text-align:center;color:white;font-size:1.1rem;font-weight:700;'
            'letter-spacing:-0.2px;margin-bottom:0.2rem;">남부 라운지</div>'
            '<div style="text-align:center;color:rgba(255,255,255,0.38);font-size:0.72rem;'
            'margin-bottom:0.2rem;letter-spacing:0.4px;">HYUNDAI · 남부지역본부</div>',
            unsafe_allow_html=True
        )

        st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

        if not st.session_state.get('nickname'):
            return  # 닉네임 미설정 시 네비 생략

        # 네비게이션
        st.markdown('<div class="sb-label">메뉴</div>', unsafe_allow_html=True)
        page = st.session_state.page

        t1 = "primary" if page in ('board', 'detail') else "secondary"
        if st.button("📋  게시판", use_container_width=True, type=t1, key="sb_board"):
            nav('board'); st.rerun()

        t2 = "primary" if page == 'suggestion' else "secondary"
        if st.button("📬  건의함", use_container_width=True, type=t2, key="sb_sg"):
            nav('suggestion'); st.rerun()

        unread = get_unread_count()
        badge  = f" ({unread})" if unread > 0 else ""
        t3     = "primary" if page == 'admin' else "secondary"
        if st.button(f"🔒  관리자{badge}", use_container_width=True, type=t3, key="sb_admin"):
            nav('admin'); st.rerun()

        st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

        # 닉네임
        st.markdown('<div class="sb-label">내 닉네임</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="sb-nick-chip">{st.session_state.nickname}</div>',
            unsafe_allow_html=True
        )

        if st.session_state.change_nickname:
            new_nick = st.text_input("새 닉네임", value=st.session_state.nickname,
                                     max_chars=20, label_visibility="collapsed",
                                     placeholder="새 닉네임 입력")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("변경", use_container_width=True, type="primary", key="nick_ok"):
                    if new_nick.strip():
                        st.session_state.nickname = new_nick.strip()
                    st.session_state.change_nickname = False
                    st.rerun()
            with c2:
                if st.button("취소", use_container_width=True, key="nick_cancel"):
                    st.session_state.change_nickname = False
                    st.rerun()
        else:
            if st.button("닉네임 변경", use_container_width=True, key="nick_change"):
                st.session_state.change_nickname = True
                st.rerun()

        st.markdown('<hr class="sb-divider">', unsafe_allow_html=True)

        # 통계
        st.markdown('<div class="sb-label">커뮤니티 현황</div>', unsafe_allow_html=True)
        post_cnt, cmt_cnt = get_stats()

        st.markdown(f"""
        <div class="sb-stat"><span>전체 게시글</span><span class="val">{post_cnt}</span></div>
        <div class="sb-stat"><span>전체 댓글</span><span class="val">{cmt_cnt}</span></div>
        <div class="sb-stat"><span>미확인 건의</span><span class="val">{unread}</span></div>
        """, unsafe_allow_html=True)

        # 하단 안내
        st.markdown(
            '<div style="margin-top:2rem;font-size:0.68rem;color:rgba(255,255,255,0.2);'
            'text-align:center;line-height:1.6;">모든 게시물은 익명으로 처리됩니다<br>'
            '© 현대자동차 남부지역본부</div>',
            unsafe_allow_html=True
        )


# ══════════════════════════════════════════════════════════════
# 메인 배너
# ══════════════════════════════════════════════════════════════
PAGE_LABELS = {
    'board':      '게시판',
    'detail':     '게시판',
    'suggestion': '건의함',
    'admin':      '관리자',
}

def render_main_banner():
    section = PAGE_LABELS.get(st.session_state.page, '게시판')
    st.markdown(f"""
    <div class="main-banner">
        <div class="banner-left">
            <div class="banner-title"><em>남부</em> 라운지</div>
            <div class="banner-sub">HYUNDAI MOTOR COMPANY · 남부지역본부 익명 소통 공간</div>
        </div>
        <div class="banner-right">
            <img src="data:image/png;base64,{LOGO_WHITE_B64}" alt="HYUNDAI">
            <span class="banner-section-chip">{section}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# 입장 코드 화면
# ══════════════════════════════════════════════════════════════
def render_access_gate():
    render_main_banner()
    _, col, _ = st.columns([2.5, 1.5, 2.5])
    with col:
        st.markdown(f"""
        <div class="gate-card">
            <div class="gate-icon">🔐</div>
            <div class="gate-title">입장 코드 확인</div>
            <div class="gate-sub">현대자동차 남부지역본부<br>직원 전용 공간입니다<br>관리자로부터 받은 코드를 입력하세요</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        code = st.text_input("코드", type="password", placeholder="입장 코드 입력",
                             label_visibility="collapsed")
        if st.button("입장하기", use_container_width=True, type="primary"):
            if code == ACCESS_CODE:
                st.session_state.access_ok = True
                st.rerun()
            else:
                st.error("입장 코드가 올바르지 않습니다.")


# ══════════════════════════════════════════════════════════════
# 닉네임 설정 화면
# ══════════════════════════════════════════════════════════════
def render_nickname_setup():
    render_main_banner()
    _, col, _ = st.columns([2.5, 1.5, 2.5])
    with col:
        st.markdown(f"""
        <div class="gate-card">
            <div class="gate-icon">✏️</div>
            <div class="gate-title">닉네임 설정</div>
            <div class="gate-sub">커뮤니티에서 사용할 닉네임을 정해주세요<br>실제 신원과는 연결되지 않습니다</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        nickname = st.text_input("닉네임", placeholder="닉네임 입력 (최대 20자)",
                                 max_chars=20, label_visibility="collapsed")
        if st.button("남부 라운지 입장", use_container_width=True, type="primary"):
            if not nickname.strip():
                st.warning("닉네임을 입력해주세요.")
            else:
                st.session_state.nickname = nickname.strip()
                st.rerun()


# ══════════════════════════════════════════════════════════════
# 게시판
# ══════════════════════════════════════════════════════════════
def render_board():
    # 상단 도구
    c_title, c_sort1, c_sort2, c_write = st.columns([4, 1, 1, 1])
    with c_title:
        st.markdown('<div class="sec-hd"><span class="accent">📋</span> 게시판</div>',
                    unsafe_allow_html=True)
    with c_sort1:
        st.markdown("<br>", unsafe_allow_html=True)
        t = "primary" if st.session_state.board_sort == 'latest' else "secondary"
        if st.button("최신순", use_container_width=True, type=t, key="sort_latest"):
            st.session_state.board_sort = 'latest'
            st.rerun()
    with c_sort2:
        st.markdown("<br>", unsafe_allow_html=True)
        t = "primary" if st.session_state.board_sort == 'popular' else "secondary"
        if st.button("인기순 (댓글↑)", use_container_width=True, type=t, key="sort_popular"):
            st.session_state.board_sort = 'popular'
            st.rerun()
    with c_write:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✏️ 글쓰기", use_container_width=True, type="primary", key="write_btn"):
            st.session_state.write_mode = True
            st.rerun()

    if st.session_state.write_mode:
        st.markdown('<hr class="sect">', unsafe_allow_html=True)
        render_write()
        return

    posts = get_all_posts(st.session_state.board_sort)
    if not posts:
        st.markdown("""
        <div class="empty-state">
            <div class="ei">📝</div>
            <p>아직 게시글이 없습니다<br>첫 번째 글을 남겨보세요!</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # 게시글 목록
    for i, post in enumerate(posts):
        is_new = i < 3 and post['comment_count'] == 0  # 최신 3개 중 댓글 없는 것
        new_tag = '<span class="tag-new">NEW</span>' if i < 2 else ''
        c_post, c_btn = st.columns([9, 1])
        with c_post:
            st.markdown(f"""
            <div class="post-card">
                <div class="post-title">{post['title']} {new_tag}</div>
                <div class="post-meta">
                    <span class="tag-nick">{post['nickname']}</span>
                    <span>{post['created_at']}</span>
                    <span class="tag-cmt">💬 {post['comment_count']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with c_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("보기", key=f"v_{post['id']}", use_container_width=True):
                nav('detail', post['id'])
                st.rerun()


# ══════════════════════════════════════════════════════════════
# 글쓰기
# ══════════════════════════════════════════════════════════════
def render_write():
    st.markdown('<div class="sec-hd"><span class="accent">✏️</span> 새 게시글 작성</div>',
                unsafe_allow_html=True)
    st.caption(f"작성자 닉네임: {st.session_state.nickname}")

    title   = st.text_input("제목", placeholder="제목을 입력하세요", max_chars=100)
    content = st.text_area("내용", placeholder="자유롭게 작성해주세요",
                           height=240, max_chars=3000)
    c1, c2, _ = st.columns([1.5, 1.5, 4])
    with c1:
        if st.button("게시하기", use_container_width=True, type="primary"):
            if not title.strip():
                st.warning("제목을 입력해주세요.")
            elif not content.strip():
                st.warning("내용을 입력해주세요.")
            else:
                pid = create_post(title.strip(), content.strip(), st.session_state.nickname)
                st.session_state.my_posts.add(pid)
                st.session_state.write_mode = False
                st.success("게시글이 등록되었습니다.")
                st.rerun()
    with c2:
        if st.button("취소", use_container_width=True):
            st.session_state.write_mode = False
            st.rerun()


# ══════════════════════════════════════════════════════════════
# 게시글 상세
# ══════════════════════════════════════════════════════════════
def render_detail():
    post = get_post(st.session_state.selected_post_id)
    if not post:
        st.error("게시글을 찾을 수 없습니다.")
        nav('board'); st.rerun(); return

    c_back, _, c_del = st.columns([2, 6, 1.5])
    with c_back:
        if st.button("← 목록으로"):
            nav('board'); st.rerun()
    with c_del:
        if is_my_post(post['id']):
            if st.button("🗑️ 삭제", use_container_width=True):
                delete_post(post['id'])
                st.session_state.my_posts.discard(post['id'])
                nav('board'); st.rerun()

    st.markdown(f"""
    <div class="detail-hd">
        <div class="detail-title">{post['title']}</div>
        <div class="detail-meta">
            <span class="tag-nick">{post['nickname']}</span>
            <span>{post['created_at']}</span>
        </div>
    </div>
    <div class="detail-body">{post['content']}</div>
    """, unsafe_allow_html=True)

    # 댓글 목록
    comments = get_comments(post['id'])
    st.markdown(f'<div class="sec-hd"><span class="accent">💬</span> 댓글 {len(comments)}개</div>',
                unsafe_allow_html=True)

    if comments:
        for cm in comments:
            cc, cd = st.columns([9, 1])
            with cc:
                st.markdown(f"""
                <div class="comment-item">
                    <div style="display:flex;gap:0.6rem;align-items:center;margin-bottom:0.1rem;">
                        <span class="c-nick">{cm['nickname']}</span>
                        <span class="c-time">{cm['created_at']}</span>
                    </div>
                    <div class="c-body">{cm['content']}</div>
                </div>
                """, unsafe_allow_html=True)
            with cd:
                st.markdown("<br>", unsafe_allow_html=True)
                if is_my_comment(cm['id']):
                    if st.button("🗑️", key=f"dc_{cm['id']}", help="삭제"):
                        delete_comment(cm['id'])
                        st.session_state.my_comments.discard(cm['id'])
                        st.rerun()
    else:
        st.markdown("""
        <div class="empty-state" style="padding:1.5rem;">
            <p>아직 댓글이 없습니다. 첫 댓글을 남겨보세요!</p>
        </div>
        """, unsafe_allow_html=True)

    # 댓글 입력
    st.markdown(f"""
    <div style="font-size:0.88rem;font-weight:600;color:#1f2937;margin:1.2rem 0 0.4rem;">
        댓글 작성
        <span style="color:#9ca3af;font-weight:400;font-size:0.78rem;margin-left:0.3rem;">
            ({st.session_state.nickname})
        </span>
    </div>
    """, unsafe_allow_html=True)
    ctext = st.text_area("댓글", placeholder="댓글을 입력하세요",
                          height=90, max_chars=500, label_visibility="collapsed")
    c1, _, _ = st.columns([2, 4, 4])
    with c1:
        if st.button("댓글 등록", type="primary", use_container_width=True):
            if not ctext.strip():
                st.warning("내용을 입력해주세요.")
            else:
                cid = create_comment(post['id'], ctext.strip(), st.session_state.nickname)
                st.session_state.my_comments.add(cid)
                st.rerun()


# ══════════════════════════════════════════════════════════════
# 건의함
# ══════════════════════════════════════════════════════════════
def render_suggestion():
    if st.session_state.get('sg_submitted'):
        st.success("건의사항이 익명으로 접수되었습니다! 소중한 의견 감사합니다.")
        st.session_state.sg_submitted = False

    st.markdown('<div class="sec-hd"><span class="accent">📬</span> 건의함</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="sg-notice">
        💡 <strong>익명 건의함</strong> — 제출하신 건의사항은 닉네임 없이 관리자에게만 전달됩니다.
        불편사항, 개선 아이디어, 자유로운 의견을 편하게 남겨주세요.
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([3, 2])
    with c1:
        title   = st.text_input("제목", placeholder="건의 제목을 입력하세요", max_chars=100)
        content = st.text_area("내용", placeholder="건의 내용을 자유롭게 작성해주세요",
                               height=260, max_chars=3000)
        if st.button("건의 제출하기", type="primary", use_container_width=True):
            if not title.strip():
                st.warning("제목을 입력해주세요.")
            elif not content.strip():
                st.warning("내용을 입력해주세요.")
            else:
                create_suggestion(title.strip(), content.strip())
                st.session_state.sg_submitted = True
                st.rerun()
    with c2:
        st.markdown("""
        <div style="background:white;border-radius:14px;padding:1.5rem;
                    border:1px solid #E8EBF2;box-shadow:0 2px 8px rgba(0,0,0,0.05);
                    margin-top:1.8rem;">
            <div style="font-size:0.85rem;font-weight:700;color:#111827;margin-bottom:0.8rem;">
                건의함 이용 안내
            </div>
            <div style="font-size:0.8rem;color:#6b7280;line-height:1.8;">
                ✅ 완전 익명으로 처리됩니다<br>
                ✅ 닉네임도 저장되지 않습니다<br>
                ✅ 관리자만 내용을 확인합니다<br>
                ✅ 자유롭게 의견을 표현하세요<br><br>
                <span style="color:#9ca3af;font-size:0.75rem;">
                부적절한 내용은 관리자에 의해<br>삭제될 수 있습니다.
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# 관리자
# ══════════════════════════════════════════════════════════════
def render_admin():
    st.markdown('<div class="sec-hd"><span class="accent">🔒</span> 관리자</div>',
                unsafe_allow_html=True)

    if not st.session_state.admin_auth:
        _, col, _ = st.columns([1, 1.5, 1])
        with col:
            st.markdown("""
            <div style="background:white;border-radius:16px;padding:2rem 1.8rem;
                        box-shadow:0 4px 20px rgba(0,0,0,0.07);border:1px solid #E8EBF2;
                        text-align:center;">
                <div style="font-size:2rem;margin-bottom:0.7rem;">🔒</div>
                <div style="font-size:1rem;font-weight:700;color:#111827;margin-bottom:0.3rem;">
                    관리자 인증
                </div>
                <div style="font-size:0.8rem;color:#9ca3af;margin-bottom:1.4rem;">
                    관리자 비밀번호를 입력하세요
                </div>
            </div>
            """, unsafe_allow_html=True)
            pw = st.text_input("비밀번호", type="password", placeholder="관리자 비밀번호",
                               label_visibility="collapsed")
            if st.button("확인", type="primary", use_container_width=True):
                if pw == ADMIN_PASSWORD:
                    st.session_state.admin_auth = True
                    st.rerun()
                else:
                    st.error("비밀번호가 올바르지 않습니다.")
        return

    # 관리자 대시보드
    post_cnt, cmt_cnt = get_stats()
    unread = get_unread_count()
    suggestions = get_all_suggestions()
    total_sg = len(suggestions)

    # 요약 지표
    m1, m2, m3, m4 = st.columns(4)
    for col, label, val, color in [
        (m1, "전체 게시글", post_cnt, "#002C5F"),
        (m2, "전체 댓글",   cmt_cnt,  "#0050a0"),
        (m3, "전체 건의",   total_sg, "#D97706"),
        (m4, "미확인 건의", unread,   "#DC2626"),
    ]:
        with col:
            st.markdown(f"""
            <div style="background:white;border-radius:12px;padding:1.1rem 1.2rem;
                        border:1px solid #E8EBF2;box-shadow:0 2px 8px rgba(0,0,0,0.05);
                        border-top:3px solid {color};">
                <div style="font-size:0.75rem;color:#9ca3af;margin-bottom:0.3rem;">{label}</div>
                <div style="font-size:1.7rem;font-weight:700;color:{color};">{val}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns([4, 1])
    with c1:
        st.markdown("**건의함 목록**")
    with c2:
        if st.button("로그아웃", use_container_width=True):
            st.session_state.admin_auth = False
            st.rerun()

    if not suggestions:
        st.markdown("""
        <div class="empty-state">
            <div class="ei">📭</div>
            <p>접수된 건의사항이 없습니다.</p>
        </div>
        """, unsafe_allow_html=True)
        return

    unread_list = [s for s in suggestions if not s['is_read']]
    read_list   = [s for s in suggestions if s['is_read']]

    if unread_list:
        st.markdown(f"**🔴 미확인 {len(unread_list)}건**")
        st.markdown("<br>", unsafe_allow_html=True)
        for sg in unread_list:
            st.markdown(f"""
            <div style="background:white;border-radius:12px;padding:1.2rem 1.4rem;
                        margin-bottom:0.8rem;border:1px solid #FDE68A;
                        border-left:4px solid #F59E0B;
                        box-shadow:0 2px 8px rgba(0,0,0,0.05);">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;
                            margin-bottom:0.6rem;">
                    <div>
                        <span style="display:inline-block;background:#FEF3C7;color:#92400E;
                                     font-size:0.7rem;font-weight:700;padding:0.15rem 0.5rem;
                                     border-radius:20px;margin-bottom:0.4rem;">미확인</span>
                        <div style="font-size:0.97rem;font-weight:700;color:#111827;">
                            {sg['title']}
                        </div>
                    </div>
                    <div style="font-size:0.75rem;color:#9ca3af;white-space:nowrap;
                                margin-left:1rem;">{sg['created_at']}</div>
                </div>
                <div style="font-size:0.88rem;color:#374151;line-height:1.75;
                            white-space:pre-wrap;border-top:1px solid #FEF3C7;
                            padding-top:0.7rem;">{sg['content']}</div>
            </div>
            """, unsafe_allow_html=True)
            ca, cb2, _ = st.columns([1.5, 1.5, 5])
            with ca:
                if st.button("확인 처리", key=f"r_{sg['id']}",
                             use_container_width=True, type="primary"):
                    mark_as_read(sg['id']); st.rerun()
            with cb2:
                if st.button("삭제", key=f"ds_{sg['id']}", use_container_width=True):
                    delete_suggestion(sg['id']); st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)

    if read_list:
        st.markdown(f"**✅ 확인 완료 {len(read_list)}건**")
        st.markdown("<br>", unsafe_allow_html=True)
        for sg in read_list:
            st.markdown(f"""
            <div style="background:#FAFAFA;border-radius:12px;padding:1.2rem 1.4rem;
                        margin-bottom:0.8rem;border:1px solid #E5E7EB;
                        border-left:4px solid #D1D5DB;">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;
                            margin-bottom:0.6rem;">
                    <div>
                        <span style="display:inline-block;background:#F3F4F6;color:#6B7280;
                                     font-size:0.7rem;font-weight:600;padding:0.15rem 0.5rem;
                                     border-radius:20px;margin-bottom:0.4rem;">확인 완료</span>
                        <div style="font-size:0.97rem;font-weight:600;color:#6B7280;">
                            {sg['title']}
                        </div>
                    </div>
                    <div style="font-size:0.75rem;color:#9ca3af;white-space:nowrap;
                                margin-left:1rem;">{sg['created_at']}</div>
                </div>
                <div style="font-size:0.88rem;color:#6B7280;line-height:1.75;
                            white-space:pre-wrap;border-top:1px solid #E5E7EB;
                            padding-top:0.7rem;">{sg['content']}</div>
            </div>
            """, unsafe_allow_html=True)
            _, cd2, __ = st.columns([6, 1.5, 1])
            with cd2:
                if st.button("삭제", key=f"ds2_{sg['id']}", use_container_width=True):
                    delete_suggestion(sg['id']); st.rerun()


# ══════════════════════════════════════════════════════════════
# 사이드바 고정 (JS: 접기 버튼 제거 + 접혀있으면 강제 열기)
# ══════════════════════════════════════════════════════════════
components.html("""
<script>
function fixSidebar() {
    try {
        var doc = window.parent.document;

        // 접혀 있으면 강제로 열기
        var expandBtn = doc.querySelector('[data-testid="stSidebarCollapsedControl"] button');
        if (expandBtn) expandBtn.click();

        // 사이드바 내부 접기 버튼 숨기기
        var targets = doc.querySelectorAll(
            '[data-testid="stSidebarCollapseButton"], ' +
            'section[data-testid="stSidebar"] button[kind="header"], ' +
            'section[data-testid="stSidebar"] button[kind="minimal"]'
        );
        targets.forEach(function(el) {
            el.style.setProperty('display', 'none', 'important');
        });
    } catch(e) {}
}

fixSidebar();
setTimeout(fixSidebar, 300);
setTimeout(fixSidebar, 800);

// 게시글 카드 더블클릭 → 보기 버튼 클릭
function addCardDblClick() {
    try {
        var doc = window.parent.document;
        var cards = doc.querySelectorAll('.post-card');
        cards.forEach(function(card) {
            if (card.dataset.dbl) return;
            card.dataset.dbl = '1';
            card.style.cursor = 'pointer';
            card.addEventListener('dblclick', function() {
                var row = card.closest('[data-testid="stHorizontalBlock"]');
                if (row) {
                    var btn = row.querySelector('button');
                    if (btn) btn.click();
                }
            });
        });
    } catch(e) {}
}

addCardDblClick();
setTimeout(addCardDblClick, 500);
setTimeout(addCardDblClick, 1200);

// DOM 변경 감지 시 재실행
var obs = new MutationObserver(function() {
    fixSidebar();
    addCardDblClick();
});
try {
    obs.observe(window.parent.document.body, { childList: true, subtree: true });
} catch(e) {}
</script>
""", height=0, scrolling=False)

# ══════════════════════════════════════════════════════════════
# 라우팅
# ══════════════════════════════════════════════════════════════
render_sidebar()

if not st.session_state.access_ok:
    render_access_gate()
elif not st.session_state.nickname:
    render_nickname_setup()
else:
    render_main_banner()
    page = st.session_state.page
    if page == 'board':
        render_board()
    elif page == 'detail':
        render_detail()
    elif page == 'suggestion':
        render_suggestion()
    elif page == 'admin':
        render_admin()
