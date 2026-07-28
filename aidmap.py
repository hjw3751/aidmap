import streamlit as st
import pandas as pd
import math
import textwrap

# ----------------------------------------------------
# 1. 페이지 설정 및 통합 커스텀 CSS (줄바꿈 버그 수정)
# ----------------------------------------------------
st.set_page_config(
    page_title="AIDMAP - 내 손안의 응급실 모듈",
    page_icon="🚑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* 한국어 단어 쪼개짐 방지 및 기본 배경 설정 */
    * {
        word-break: keep-all !important;
        font-family: 'Pretendard', -apple-system, sans-serif;
    }
    .main { background-color: #F8FAFC; }
    
    /* NEMC 메인 헤더 */
    .nemc-top-bar {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%);
        color: white !important;
        padding: 20px 24px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15);
    }
    .nemc-top-bar h2 { color: #FFFFFF !important; margin: 0; font-weight: 700; font-size: 1.5rem; }
    .nemc-top-bar p { color: #93C5FD !important; margin: 4px 0 0 0; font-size: 0.9rem; }

    /* 컨트롤러 박스 */
    .filter-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 20px;
    }

    /* KTAS 응급도 결과 박스 */
    .ktas-box {
        background-color: #FEF3C7;
        border-left: 6px solid #F59E0B;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 15px;
    }

    /* 오른쪽 병원 카드 (버그 수정 영역) */
    .hospital-card {
        background-color: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 16px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    }

    /* 진료 통제 뱃지 */
    .notice-badge {
        background-color: #FEF2F2;
        color: #991B1B;
        border: 1px solid #FECACA;
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: bold;
        margin: 8px 0;
    }

    /* 실시간 가용 병상 표 */
    .bed-grid {
        display: flex;
        gap: 12px;
        background-color: #F8FAFC;
        padding: 10px;
        border-radius: 6px;
        margin: 10px 0;
        font-size: 0.85rem;
    }

    /* 진료과 태그 */
    .dept-tag {
        display: inline-block;
        background-color: #E2E8F0;
        color: #334155;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.78rem;
        margin-right: 4px;
        margin-bottom: 4px;
    }

    /* 버튼 스타일 */
    .btn-action {
        display: inline-block;
        padding: 7px 12px;
        border-radius: 6px;
        font-size: 0.82rem;
        font-weight: bold;
        text-decoration: none !important;
        margin-right: 6px;
    }
    .btn-call { background-color: #2563EB; color: #FFFFFF !important; }
    .btn-kakao { background-color: #FEE500; color: #000000 !important; }
    .btn-naver { background-color: #03CF5D; color: #FFFFFF !important; }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 2. 더미 데이터 베이스
# ----------------------------------------------------
REGION_DATA = {
    "제주특별자치도": ["전체", "서귀포시", "제주시"],
    "서울특별시": ["전체", "중구", "강남구"]
}

FACILITY_DB = [
    {
        "cat": "응급실", "sido": "제주특별자치도", "sigungu": "서귀포시",
        "name": "제주특별자치도 서귀포의료원", "type": "지역응급의료센터",
        "address": "제주특별자치도 서귀포시 장수로 47", "phone": "064-730-3109",
        "gen_curr": 14, "gen_total": 16, "ped_curr": 1, "ped_total": 4, "mat_status": "가능(1실)",
        "lat": 33.2547, "lng": 126.5601,
        "departments": ["응급내시경", "성인위장관", "소아청소년과", "외과/골절"],
        "restriction": "⚠️ 응급 CT 정기 점검 중 (21:00 점검 완료 예정)"
    },
    {
        "cat": "응급실", "sido": "제주특별자치도", "sigungu": "제주시",
        "name": "제주대학교병원", "type": "권역응급의료센터",
        "address": "제주특별자치도 제주시 아란13길 15", "phone": "064-717-1900",
        "gen_curr": 18, "gen_total": 20, "ped_curr": 3, "ped_total": 5, "mat_status": "가능(2실)",
        "lat": 33.4670, "lng": 126.5450,
        "departments": ["응급내시경", "성인위장관", "소아청소년과", "심뇌혈관센터", "외과/골절"],
        "restriction": "🟢 전 과 정상 수용 및 심뇌혈관 응급 수술 가능"
    }
]

# ----------------------------------------------------
# 3. 메인 상단 브랜딩
# ----------------------------------------------------
st.markdown("""
<div class="nemc-top-bar">
    <h2>🚑 AIDMAP : 내 손안의 응급실 (통합 대시보드)</h2>
    <p>실시간 병상 가용 현황 | KTAS 응급도 분석 | 원터치 내비게이션 연동</p>
</div>
""", unsafe_allow_html=True)

# 상단 필터
with st.container():
    st.markdown('<div class="filter-card">', unsafe_allow_html=True)
    f_col1, f_col2, f_col3, f_col4 = st.columns([1.2, 1.2, 1.2, 1.0])
    with f_col1:
        selected_cat = st.selectbox("조회 대상", ["전체 시설", "🏥 응급의료기관", "🌙 달빛어린이병원"], index=0)
    with f_col2:
        selected_sido = st.selectbox("시/도 선택", list(REGION_DATA.keys()), index=0)
    with f_col3:
        selected_sigungu = st.selectbox("시/군/구 선택", REGION_DATA[selected_sido], index=1)
    with f_col4:
        st.write("&nbsp;")
        if st.button("🎯 GPS 현재위치", use_container_width=True):
            st.toast("📍 서귀포시 동홍동 기준 위치가 설정되었습니다.")
    st.markdown('</div>', unsafe_allow_html=True)

# 2열 레이아웃
col_left, col_right = st.columns([1.0, 1.2], gap="large")

# ====================================================
# [왼쪽 열] KTAS 분석 & 수식 & 연령별 안내
# ====================================================
with col_left:
    st.subheader("🩺 KTAS AI 응급도 분석")
    
    selected_symptom = st.selectbox(
        "환자의 대표 증상을 선택하세요:",
        ["🦴 골절 의심 / 출혈성 외상", "🫀 심한 흉통 및 호흡곤란", "👶 소아 39도 이상 고열", "🤒 단순 발열 및 약 처방"]
    )

    st.markdown("""
    <div class="ktas-box">
        <h4 style="margin:0 0 6px 0; color: #92400E;">🟡 KTAS 3단계 (응급)</h4>
        <p style="margin:0; font-size: 0.9rem; color: #78350F;">
            응급 처치가 필요한 상태입니다. 소아응급실 또는 지역응급센터로 이동하세요.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 수식 디자인 개선 (깔끔한 안내 상자 처리)
    st.markdown("""
    <div style="background-color: #F1F5F9; padding: 12px 16px; border-radius: 8px; border: 1px solid #E2E8F0;">
        <span style="font-size: 0.85rem; font-weight: bold; color: #334155;">💡 AI 종합 적합도 점수 산출 공식</span>
        <div style="margin-top: 6px; font-family: monospace; font-size: 0.88rem; color: #1E293B; background: white; padding: 8px; border-radius: 4px; text-align: center;">
            Score = (진료과 × 0.4) + (잔여병상 × 0.3) + (KTAS × 0.3) - (거리km × 2.0)
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # 줄바꿈 버그 해결된 연령별 타이틀
    st.subheader("🔊 연령별 응급처치 & 음성 안내")
    
    age = st.radio("환자 연령대:", ["영유아", "어린이", "성인", "노년층"], index=1, horizontal=True)
    
    st.info("💡 선택하신 연령대에 맞는 긴급 대처 수칙이 상단 모듈과 동기화되어 나타납니다.")

# ====================================================
# [오른쪽 열] HTML 깨짐을 완벽히 해결한 병원 카드 출력
# ====================================================
with col_right:
    st.subheader("🏥 응급의료기관 조회 결과")
    
    for h in FACILITY_DB:
        # 조건 필터링
        if h["sido"] != selected_sido:
            continue
        if selected_sigungu != "전체" and h["sigungu"] != selected_sigungu:
            continue

        # 1. 진료과 태그 조립
        dept_tags_html = "".join([f'<span class="dept-tag">{d}</span>' for d in h["departments"]])

        # 2. 버튼 URL
        kakao_url = f"https://map.kakao.com/link/to/{h['name']},{h['lat']},{h['lng']}"
        naver_url = f"https://map.naver.com/v5/search/{h['name']}"

        # 3. HTML 템플릿 (dedent 함수를 사용해 마크다운 코드블록 꼬임 버그를 근본적으로 차단)
        card_html = textwrap.dedent(f"""
            <div class="hospital-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <span style="background-color: #334155; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; font-weight: bold;">{h['type']}</span>
                        <h3 style="margin: 6px 0 2px 0; color: #0F172A; font-size: 1.15rem;">{h['name']}</h3>
                        <p style="margin: 0; font-size: 0.85rem; color: #64748B;">📍 {h['address']} (<b>0.1km</b>)</p>
                    </div>
                </div>
                
                <div class="notice-badge">{h['restriction']}</div>
                
                <div style="margin: 8px 0;">{dept_tags_html}</div>
                
                <div class="bed-grid">
                    <span>일반응급: <b>{h['gen_curr']}/{h['gen_total']}석</b></span>
                    <span>소아응급: <b>{h['ped_curr']}/{h['ped_total']}석</b></span>
                    <span>분만실: <b>{h['mat_status']}</b></span>
                </div>
                
                <div style="margin-top: 12px;">
                    <a href="tel:{h['phone']}" class="btn-action btn-call">📞 전화 걸기</a>
                    <a href="{kakao_url}" target="_blank" class="btn-action btn-kakao">🟡 카카오맵 길찾기</a>
                    <a href="{naver_url}" target="_blank" class="btn-action btn-naver">🟢 네이버 지도</a>
                </div>
            </div>
        """).strip()

        # 출력
        st.markdown(card_html, unsafe_allow_html=True)

st.divider()
st.caption("© 2026 AIDMAP - Emergency Medical Information Interface")
