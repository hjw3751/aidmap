import streamlit as st
import pandas as pd
import time

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="AIDMAP - 내 손안의 응급실",
    page_icon="🚑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #E63946;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4A5568;
        margin-bottom: 20px;
    }
    .card-infant { background-color: #FFF5F5; border-left: 5px solid #E53E3E; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    .card-child { background-color: #FEFCBF; border-left: 5px solid #D69E2E; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    .card-adult { background-color: #EBF8FF; border-left: 5px solid #3182CE; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    .card-senior { background-color: #F0FFF4; border-left: 5px solid #38A169; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

# 헤더 섹션
st.markdown('<p class="main-header">🚑 AIDMAP : 내 손안의 맞춤형 응급실</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">연령대별 맞춤 응급처치 매뉴얼과 실시간 응급실 가용 병상 정보 서비스</p>', unsafe_allow_html=True)

st.divider()

# 레이아웃 분할: 왼쪽 (응급 매뉴얼), 오른쪽 (실시간 응급실 조회)
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("👤 연령대별 맞춤 응급 매뉴얼")
    
    age_group = st.radio(
        "환자의 연령대를 선택하세요:",
        ["영유아 (0~5세)", "어린이 (6~12세)", "청소년 및 성인", "노년층 (65세 이상)"],
        index=2
    )

    if age_group == "영유아 (0~5세)":
        st.markdown("""
        <div class="card-infant">
            <h4>👶 영유아 응급처치 수칙</h4>
            <ul>
                <li><b>고열 (38℃ 이상):</b> 옷을 벗기고 미지근한 물로 몸을 닦아줍니다. 해열제 복용 시 교차복용 주기를 확인하세요.</li>
                <li><b>영아 기도폐쇄:</b> 등 압박 5회 + 가슴 압박 5회를 119 도착 시까지 교대로 시행합니다.</li>
                <li><b>열성경련:</b> 주변의 위험한 물건을 치우고, 아이를 옆으로 눕혀 기도를 확보합니다. (인공호흡 금지)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    elif age_group == "어린이 (6~12세)":
        st.markdown("""
        <div class="card-child">
            <h4>🧒 어린이 응급처치 수칙</h4>
            <ul>
                <li><b>골절/타박상:</b> 부상 부위를 무리하게 움직이지 말고 부목이나 판판한 것으로 고정 후 냉찜질을 해줍니다.</li>
                <li><b>화상:</b> 즉시 흐르는 미지근한 수돗물로 15분 이상 식힙니다. 얼음을 직접 대면 조직 손상이 악화됩니다.</li>
                <li><b>코피:</b> 고개를 앞으로 약간 숙이고 콧볼 양쪽을 10분간 지그시 눌러줍니다.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    elif age_group == "청소년 및 성인":
        st.markdown("""
        <div class="card-adult">
            <h4>🧑 청소년 및 성인 응급처치 수칙</h4>
            <ul>
                <li><b>심정지 의심:</b> 의식 및 호흡 확인 후 즉시 119 신고 및 AED(자동심장충격기)를 요청하고 가슴압박(분당 100~120회)을 시행합니다.</li>
                <li><b>뇌졸중(FAST):</b> 안면마비(Face), 팔 마비(Arm), 언어장애(Speech) 발생 시 골든타임(3시간) 확보를 위해 즉시 응급실로 이송합니다.</li>
                <li><b>Severe Bleeding (지혈):</b> 출혈 부위를 깨끗한 헝겊이나 거즈로 직접 강하게 압박합니다.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class="card-senior">
            <h4>🧓 노년층 응급처치 수칙</h4>
            <ul>
                <li><b>낙상 사고:</b> 골절 위험이 높으므로 무리하게 일으키지 말고 통증 부위를 확인 후 119에 신고합니다.</li>
                <li><b>심혈관 질환:</b> 갑작스러운 흉통, 턱/어깨 통증, 호흡곤란 발생 시 즉시 응급 이송 조치를 취합니다.</li>
                <li><b>저혈당 쇼크:</b> 의식이 있는 경우 포도당 캔디나 사탕/주스를 섭취시키고, 의식이 없으면 아무것도 입에 넣지 않습니다.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.subheader("🏥 실시간 응급실 병상 조회")
    
    region = st.text_input("조회할 지역(시/군/구)을 입력하세요:", value="서귀포시")
    
    if st.button("🔍 실시간 가용 병상 검색", type="primary"):
        with st.spinner(f"'{region}' 지역 응급의료기관 실시간 정보 조회 중..."):
            time.sleep(1) # API 로딩 효과 연출
            
            # Mock Data (추후 국립중앙의료원 응급의료 API 연동 구역)
            mock_hospitals = pd.DataFrame({
                "병원명": ["서귀포의료원", "제주대학교병원", "한마음병원", "한국병원"],
                "응급실 전화": ["064-730-3109", "064-717-1900", "064-750-9000", "064-750-0000"],
                "잔여 일반응급": [3, 1, 0, 5],
                "수술실 가능 여부": ["가능", "가능", "불가 (점검 중)", "가능"],
                "거리가까운순": ["2.1 km", "38.5 km", "40.1 km", "41.2 km"]
            })
            
            st.success(f"📍 '{region}' 인근 실시간 응급실 현황")
            st.dataframe(mock_hospitals, use_container_width=True, hide_index=True)
            
            st.info("💡 **TIP:** 잔여 병상이 0인 경우 수술이나 긴급 처치가 지연될 수 있으므로, 출발 전 응급실 전화번호로 사전 확인을 권장합니다.")

st.divider()

# 하단 푸터
st.caption("© 2026 AIDMAP Project | 국립중앙의료원 응급의료포털 API 연동 기반 프로토타입")
