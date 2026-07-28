import streamlit as st
import pandas as pd
import requests
import math
import time

# ----------------------------------------------------
# 0. 설정 및 API 키 관리
# ----------------------------------------------------
# 카카오 REST API 키 (카카오 디벨로퍼스 https://developers.kakao.com 에서 발급 가능)
# 테스트용 또는 실제 키가 없을 경우 모의 검색 결과로 동작하도록 예외 처리가 되어있습니다.
KAKAO_REST_API_KEY = "YOUR_KAKAO_REST_API_KEY"

# 1. 페이지 설정
st.set_page_config(
    page_title="AIDMAP - 내 손안의 맞춤형 응급실",
    page_icon="🚑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. 다크모드/라이트모드 완벽 대응 고대비 Custom CSS
st.markdown("""
<style>
    .manual-card {
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 15px;
        color: #1A202C !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .manual-card h3, .manual-card h4, .manual-card li, .manual-card p, .manual-card div {
        color: #1A202C !important;
    }
    .bg-infant { background-color: #FFF5F5; border-left: 6px solid #E53E3E; }
    .bg-child { background-color: #FEFCBF; border-left: 6px solid #D69E2E; }
    .bg-adult { background-color: #EBF8FF; border-left: 6px solid #3182CE; }
    .bg-senior { background-color: #F0FFF4; border-left: 6px solid #38A169; }

    .guide-box {
        background-color: #EDF2F7;
        border: 2px solid #CBD5E0;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        color: #2D3748 !important;
    }
    .guide-box * { color: #2D3748 !important; }

    .hospital-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        color: #2D3748 !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .hospital-card * { color: #2D3748 !important; }
    
    .badge-ok { background-color: #C6F6D5; color: #22543D !important; padding: 4px 8px; border-radius: 6px; font-weight: bold; }
    .badge-busy { background-color: #FEEBC8; color: #744210 !important; padding: 4px 8px; border-radius: 6px; font-weight: bold; }
    .badge-full { background-color: #FED7D7; color: #742A2A !important; padding: 4px 8px; border-radius: 6px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# Helper Functions (유틸리티 함수)
# ----------------------------------------------------

# 두 위도/경도 좌표 간 직선 거리 계산 (Haversine Formula - km 단위)
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)

# 카카오 키워드 장소/도로명 검색 함수
def search_location_kakao(keyword):
    if not KAKAO_REST_API_KEY or KAKAO_REST_API_KEY == "YOUR_KAKAO_REST_API_KEY":
        # API 키가 등록되지 않았을 때의 Mock 검색 처리 (테스트용)
        if "동홍동" in keyword or "짜장나라" in keyword or "서귀포" in keyword:
            return [{
                'place_name': '짜장나라 (동홍동)',
                'road_address_name': '제주특별자치도 서귀포시 동홍서로 12',
                'address_name': '제주특별자치도 서귀포시 동홍동 123-4',
                'y': '33.2565',
                'x': '126.5680'
            }]
        return []

    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"}
    params = {"query": keyword}
    try:
        res = requests.get(url, headers=headers, params=params, timeout=3)
        if res.status_code == 200:
            return res.json().get('documents', [])
    except Exception:
        pass
    return []

# ----------------------------------------------------
# [팝업/모달] 사용 설명서
# ----------------------------------------------------
if "first_visit" not in st.session_state:
    st.session_state.first_visit = True

with st.expander("📖 **[필독] AIDMAP 서비스 사용 설명서** (처음 오셨다면 클릭하세요!)", expanded=st.session_state.first_visit):
    st.markdown("""
    <div class="guide-box">
        <h4>🚨 AIDMAP에 오신 것을 환영합니다!</h4>
        <p>본 서비스는 긴급 상황 시 <b>빠르고 직관적인 맞춤형 응급처치</b>와 <b>주변 응급실 잔여 병상 현황</b>을 한눈에 파악할 수 있도록 제작되었습니다.</p>
        <hr>
        <b>💡 주요 기능 활용법:</b>
        <ol>
            <li><b>연령대 선택:</b> 환자 연령(영유아, 어린이, 성인, 노년층)을 선택하면 맞춤형 응급처치 수칙이 안내됩니다.</li>
            <li><b>상세 위치 검색 & 거반 거리 정렬:</b> '서귀포시 동홍동 짜장나라'와 같이 도로명/상호명을 검색하면 기준 위치로부터 가장 가까운 응급실 순으로 실시간 병상이 정렬됩니다.</li>
            <li><b>실시간 병상 갱신:</b> ⚡ 갱신 버튼으로 실시간 잔여 병상을 새로고침할 수 있습니다.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    if st.button("닫기 및 이용 시작하기"):
        st.session_state.first_visit = False
        st.rerun()

# 타이틀
st.title("🚑 AIDMAP : 내 손안의 맞춤형 응급실")
st.caption("환자 연령별 맞춤 응급처치 가이드 및 위치 기반 실시간 응급실 가용 병상 시각화")

st.divider()

# 메인 2열 레이아웃
col1, col2 = st.columns([1.1, 0.9], gap="large")

# ----------------------------------------------------
# 왼쪽 열: 연령대별 맞춤 응급 매뉴얼
# ----------------------------------------------------
with col1:
    st.subheader("👤 연령대 맞춤 응급처치 가이드")
    
    age_group = st.radio(
        "환자의 연령대를 선택해주세요:",
        ["👶 영유아 (0~5세)", "🧒 어린이 (6~12세)", "🧑 청소년 및 성인", "🧓 노년층 (65세 이상)"],
        index=2,
        horizontal=True
    )

    if "영유아" in age_group:
        st.markdown("""
        <div class="manual-card bg-infant">
            <h3>👶 영유아 긴급 대처 수칙</h3>
            <ul>
                <li><b>고열 (38℃ 이상):</b> 옷을 가볍게 입히고 미지근한 물을 적신 수건으로 몸을 닦아줍니다.</li>
                <li><b>영아 기도폐쇄 (하임리히법):</b> 아이를 엎드리게 한 뒤 등 중앙을 5회 때리고, 뒤집어 가슴 중앙을 5회 압박합니다.</li>
                <li><b>열성경련:</b> 억지로 움직이지 못하게 막지 말고, 옆으로 눕혀 기도를 확보한 후 119에 신고합니다.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    elif "어린이" in age_group:
        st.markdown("""
        <div class="manual-card bg-child">
            <h3>🧒 어린이 맞춤 설명서 (쉽게 따라 해요!)</h3>
            <p style="font-size: 1.1rem; font-weight: bold;">당황하지 말고 아래 순서대로 해보세요!</p>
            <ol style="font-size: 1.05rem; line-height: 1.8;">
                <li><b>119에 전화하기:</b> 주변 어른이나 119에 바로 크게 도움을 요청해요.</li>
                <li><b>뜨거운 것에 데였을 때:</b> 얼음을 바로 대지 말고, 시원한 흐르는 물에 15분 동안 대고 있으세요.</li>
                <li><b>넘어져서 피가 날 때:</b> 깨끗한 휴지나 거즈로 피가 나는 곳을 지그시 꾹 눌러주세요.</li>
                <li><b>뼈가 아프거나 부러졌을 때:</b> 부상당한 팔다리를 움직이지 말고 가만히 기다려요.</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

    elif "성인" in age_group:
        st.markdown("""
        <div class="manual-card bg-adult">
            <h3>🧑 성인 핵심 응급처치 수칙</h3>
            <ul>
                <li><b>심정지 의심:</b> 의식 확인 후 즉시 119 신고 및 AED 요청. 분당 100~120회 속도로 가슴 중앙 압박.</li>
                <li><b>뇌졸중(FAST):</b> 안면마비, 팔 마비, 발음 어눌함 발생 시 즉시 골든타임 내 응급실 이송.</li>
                <li><b>대량 출혈:</b> 상처 부위를 깨끗한 거즈로 직접 강하게 압박하며 심장보다 높게 유지.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class="manual-card bg-senior">
            <h3>🧓 노년층 응급처치 수칙</h3>
            <ul>
                <li><b>낙상 사고:</b> 뼈가 약하므로 무리하게 일어나지 말고, 그 자리에서 119를 기다립니다.</li>
                <li><b>심혈관 질환:</b> 갑작스러운 흉통이나 턱·어깨 통증, 숨참 증상 발생 시 즉시 응급 이송.</li>
                <li><b>저혈당 쇼크:</b> 의식이 있으면 사탕이나 주스를 섭취하고, 의식이 없으면 아무것도 먹이지 않습니다.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("🔊 어르신을 위한 음성 안내")
        tts_text = "노년층 응급처치 수칙입니다. 첫째, 낙상 사고 시 무리하게 일어나지 마시고 119를 기다리세요. 둘째, 갑작스러운 가슴 통증이나 호흡곤란 시 즉시 응급실로 이동하셔야 합니다."
        
        tts_html = f"""
        <div style="background-color: #E6FFFA; padding: 15px; border-radius: 10px; border: 1px solid #319795;">
            <p style="color: #234E52 !important; font-weight: bold; margin-bottom: 8px;"> 아래 버튼을 누르면 응급처치 수칙을 음성으로 읽어드립니다.</p>
            <button onclick="speakText()" style="background-color: #319795; color: white; border: none; padding: 10px 20px; font-size: 16px; border-radius: 8px; cursor: pointer; font-weight: bold;">
                🔊 음성 안내 듣기
            </button>
            <button onclick="window.speechSynthesis.cancel()" style="background-color: #E53E3E; color: white; border: none; padding: 10px 15px; font-size: 16px; border-radius: 8px; cursor: pointer; margin-left: 10px;">
                ⏹️ 정지
            </button>
        </div>
        <script>
            function speakText() {{
                window.speechSynthesis.cancel();
                var msg = new SpeechSynthesisUtterance('{tts_text}');
                msg.lang = 'ko-KR';
                msg.rate = 0.85;
                window.speechSynthesis.speak(msg);
            }}
        </script>
        """
        st.components.v1.html(tts_html, height=100)

# ----------------------------------------------------
# 오른쪽 열: 실시간 응급실 병상 시각화 & 현황 (고도화)
# ----------------------------------------------------
with col2:
    st.subheader("🏥 실시간 응급실 병상 시각화")
    
    # 상단 실시간 정보 갱신 버튼
    top_col1, top_col2 = st.columns([3, 1])
    with top_col1:
        st.write("📍 **기준 위치 설정 및 도로명 검색**")
    with top_col2:
        if st.button("⚡ 실시간 갱신", use_container_width=True):
            st.toast("최신 병상 정보가 업데이트되었습니다!")
            time.sleep(0.3)
            st.rerun()

    # 기본 GPS / 위치 설정 (기본값: 서귀포시청 기준 좌표)
    user_lat, user_lng = 33.2541, 126.5601
    current_loc_name = "제주특별자치도 서귀포시 (현재 내 위치)"

    # 장소/도로명 검색 입력창
    search_keyword = st.text_input(
        "상세 장소 또는 도로명 검색 (예: 제주특별자치도 서귀포시 동홍동 짜장나라)", 
        placeholder="검색어를 입력 후 엔터를 누르세요..."
    )

    if search_keyword:
        places = search_location_kakao(search_keyword)
        if places:
            place_options = {}
            for idx, p in enumerate(places):
                addr = p['road_address_name'] if p['road_address_name'] else p['address_name']
                label = f"{p['place_name']} ({addr})"
                place_options[label] = (float(p['y']), float(p['x']), addr)

            selected_place_label = st.selectbox("🎯 상세 주소를 선택하세요:", list(place_options.keys()))
            if selected_place_label:
                user_lat, user_lng, addr_detail = place_options[selected_place_label]
                current_loc_name = selected_place_label
                st.info(f"📍 설정된 위치: **{selected_place_label}**")
        else:
            st.warning("검색 결과가 없습니다. 기본 서귀포시 기준으로 조회합니다.")

    # 응급의료기관 데이터베이스 (위도/경도 포함)
    raw_hospitals = [
        {"name": "서귀포의료원", "beds": 4, "total": 10, "phone": "064-730-3109", "lat": 33.2547, "lng": 126.5601},
        {"name": "제주대학교병원", "beds": 1, "total": 12, "phone": "064-717-1900", "lat": 33.4670, "lng": 126.5450},
        {"name": "한마음병원", "beds": 0, "total": 8, "phone": "064-750-9000", "lat": 33.4962, "lng": 126.5441},
        {"name": "한국병원", "beds": 6, "total": 10, "phone": "064-750-0000", "lat": 33.5008, "lng": 126.5178},
    ]

    # 설정된 위치 기준으로 각 병원까지의 거리 실시간 재계산 및 정렬
    calculated_hospitals = []
    for h in raw_hospitals:
        dist_km = calculate_distance(user_lat, user_lng, h["lat"], h["lng"])
        
        # 병상 상태 자동 판별
        if h["beds"] >= 3:
            status = "여유"
        elif h["beds"] > 0:
            status = "혼잡"
        else:
            status = "만석"

        calculated_hospitals.append({
            "name": h["name"],
            "beds": h["beds"],
            "total": h["total"],
            "status": status,
            "phone": h["phone"],
            "dist_val": dist_km,
            "dist_str": f"{dist_km}km"
        })

    # 거리순(가장 가까운 병원순)으로 정렬
    calculated_hospitals.sort(key=lambda x: x["dist_val"])
    df_hospitals = pd.DataFrame(calculated_hospitals)

    # 1) 요약 메트릭
    m1, m2, m3 = st.columns(3)
    m1.metric("총 응급의료기관", f"{len(df_hospitals)}곳")
    m2.metric("수용 가능 병원", f"{len(df_hospitals[df_hospitals['beds'] > 0])}곳", delta="이용 가능")
    m3.metric("총 잔여 병상", f"{df_hospitals['beds'].sum()}석")

    # 2) 시각화 차트
    st.markdown("#### 📊 거리순 병원별 잔여 응급 병상 현황")
    chart_df = df_hospitals.set_index("name")[["beds"]]
    chart_df.columns = ["잔여 병상 수"]
    st.bar_chart(chart_df, color="#3182CE", height=200)

    # 3) 상세 카드형 UI
    st.markdown("#### 🏥 위치 맞춤 상세 병상 현황 및 연락처")
    for hosp in calculated_hospitals:
        if hosp["status"] == "여유":
            badge = '<span class="badge-ok">🟢 여유 (즉시 가능)</span>'
        elif hosp["status"] == "혼잡":
            badge = '<span class="badge-busy">🟡 혼잡 (대기 예상)</span>'
        else:
            badge = '<span class="badge-full">🔴 만석 (이송전 확인)</span>'
            
        st.markdown(f"""
        <div class="hospital-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h4 style="margin: 0;">{hosp['name']} <span style="font-size: 0.85rem; color: #718096; font-weight: normal;">(📍 거리 {hosp['dist_str']})</span></h4>
                {badge}
            </div>
            <div style="margin-top: 10px; display: flex; justify-content: space-between; align-items: center;">
                <p style="margin: 0; font-size: 1.05rem;">잔여 일반 병상: <b>{hosp['beds']}석</b> / {hosp['total']}석</p>
                <a href="tel:{hosp['phone']}" style="background-color: #3182CE; color: white !important; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 0.9rem;">📞 전화 걸기</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.divider()
st.caption("© 2026 AIDMAP Project | 사용자 중심 응급의료 서비스 프로토타입")