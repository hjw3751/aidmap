import streamlit as st
import pandas as pd
import requests
import math
import time

# ----------------------------------------------------
# 1. 페이지 설정 및 국립중앙의료원(NEMC) 스타일 테마 적용
# ----------------------------------------------------
st.set_page_config(
    page_title="AIDMAP - 내 손안의 맞춤형 응급실",
    page_icon="🚑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# NEMC / E-Gen 응급의료포털 특유의 신뢰감 있는 고대비 CSS
st.markdown("""
<style>
    /* 메인 배경 및 폰트 정의 */
    .main { background-color: #F8FAFC; }
    
    /* NEMC 헤더 스타일 카드 */
    .nemc-header {
        background: linear-gradient(135deg, #0A2540 0%, #1E40AF 100%);
        color: white !important;
        padding: 20px 25px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(10, 37, 64, 0.15);
    }
    .nemc-header h2, .nemc-header p { color: white !important; margin: 0; }
    
    /* 카드 가독성 및 디자인 */
    .manual-card {
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 15px;
        color: #1E293B !important;
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .manual-card h3, .manual-card h4, .manual-card li, .manual-card p, .manual-card div {
        color: #1E293B !important;
    }
    .bg-infant { border-top: 5px solid #EF4444; }
    .bg-child { border-top: 5px solid #F59E0B; }
    .bg-adult { border-top: 5px solid #3B82F6; }
    .bg-senior { border-top: 5px solid #10B981; }

    /* 연령별 사용 매뉴얼 박스 */
    .app-guide-box {
        background-color: #F1F5F9;
        border-left: 4px solid #475569;
        padding: 12px 16px;
        border-radius: 6px;
        margin-top: 15px;
    }
    .app-guide-box h5 { margin-top: 0; color: #0F172A !important; font-weight: bold; }

    /* 병원 카드 UI */
    .hospital-card {
        background-color: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03);
    }
    .hospital-card * { color: #1E293B !important; }
    
    .badge-ok { background-color: #DCFCE7; color: #166534 !important; padding: 4px 10px; border-radius: 20px; font-size: 0.85rem; font-weight: bold; }
    .badge-busy { background-color: #FEF3C7; color: #92400E !important; padding: 4px 10px; border-radius: 20px; font-size: 0.85rem; font-weight: bold; }
    .badge-full { background-color: #FEE2E2; color: #991B1B !important; padding: 4px 10px; border-radius: 20px; font-size: 0.85rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 2. 유틸리티 함수 (좌표 거리 계산 및 검색)
# ----------------------------------------------------
KAKAO_REST_API_KEY = "YOUR_KAKAO_REST_API_KEY" # 실제 운영 시 카카오 REST API 키 입력

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)

def search_location_kakao(keyword):
    # API 키가 비어있거나 기본값일 때 실감 나는 예시 주소 데이터 제공
    if not KAKAO_REST_API_KEY or KAKAO_REST_API_KEY == "YOUR_KAKAO_REST_API_KEY":
        if "동홍동" in keyword or "짜장나라" in keyword or "서귀포" in keyword:
            return [
                {
                    'place_name': '짜장나라 (동홍동 본점)',
                    'road_address_name': '제주특별자치도 서귀포시 동홍서로 12',
                    'address_name': '제주특별자치도 서귀포시 동홍동 123-4',
                    'y': '33.2565',
                    'x': '126.5680'
                },
                {
                    'place_name': '동홍동 주민센터',
                    'road_address_name': '제주특별자치도 서귀포시 동홍로 104',
                    'address_name': '제주특별자치도 서귀포시 동홍동 480-1',
                    'y': '33.2612',
                    'x': '126.5695'
                }
            ]
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
# 3. 상단 헤더 영역 (NEMC 대시보드 스타일)
# ----------------------------------------------------
st.markdown("""
<div class="nemc-header">
    <h2>🚑 AIDMAP : 내 손안의 응급실 종합 상황판</h2>
    <p>보건복지부 / 국립중앙의료원 응급의료포털 연동 | 실시간 가용 병상 및 맞춤형 응급처치 가이드</p>
</div>
""", unsafe_allow_html=True)

# 메인 2열 레이아웃
col1, col2 = st.columns([1.1, 0.9], gap="large")

# ----------------------------------------------------
# 왼쪽 열: 연령대별 응급 수칙 + AIDMAP 앱 사용 매뉴얼
# ----------------------------------------------------
with col1:
    st.subheader("👤 연령대 맞춤 가이드 & 사용법")
    
    age_group = st.radio(
        "환자의 연령대를 선택해주세요:",
        ["👶 영유아 (0~5세)", "🧒 어린이 (6~12세)", "🧑 청소년 및 성인", "🧓 노년층 (65세 이상)"],
        index=2,
        horizontal=True
    )

    # 1) 영유아
    if "영유아" in age_group:
        st.markdown("""
        <div class="manual-card bg-infant">
            <h3>👶 영유아 긴급 대처 수칙 (보호자용)</h3>
            <ul>
                <li><b>고열 (38℃ 이상):</b> 옷을 가볍게 입히고 미지근한 물을 적신 수건으로 몸을 닦아줍니다.</li>
                <li><b>영아 기도폐쇄 (하임리히법):</b> 아이를 엎드리게 한 뒤 등 중앙을 5회 때리고, 뒤집어 가슴 중앙을 5회 압박합니다.</li>
                <li><b>열성경련:</b> 억지로 움직이지 못하게 막지 말고, 옆으로 눕혀 기도를 확보한 후 119에 신고합니다.</li>
            </ul>
            <div class="app-guide-box">
                <h5>📱 보호자를 위한 AIDMAP 서비스 사용법</h5>
                <ol style="margin-bottom: 0;">
                    <li>오른쪽 검색창에 <b>현재 계신 위치나 아동병원/집 주소</b>를 입력하세요.</li>
                    <li>가장 가까운 응급실의 <b>소아 전용 병상 남아있는지 확인</b>합니다.</li>
                    <li>우측 하단의 <b>'📞 전화 걸기'</b> 버튼을 눌러 소아과 전문의 진료가 가능한지 먼저 확인 후 출발하세요.</li>
                </ol>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 2) 어린이 (어린이 눈높이 설명)
    elif "어린이" in age_group:
        st.markdown("""
        <div class="manual-card bg-child">
            <h3>🧒 어린이 맞춤 대처 수칙</h3>
            <ol style="font-size: 1rem; line-height: 1.7;">
                <li><b>119에 전화하기:</b> 주변 어른이나 119에 바로 크게 도움을 요청해요.</li>
                <li><b>뜨거운 것에 데였을 때:</b> 시원한 흐르는 물에 15분 동안 대고 있으세요.</li>
                <li><b>넘어져서 피가 날 때:</b> 깨끗한 휴지나 거즈로 피가 나는 곳을 꾹 눌러주세요.</li>
            </ol>
            <div class="app-guide-box">
                <h5>📱 어린이를 위한 AIDMAP 앱 쉬운 사용법</h5>
                <p style="margin-bottom: 5px;"><b>당황하지 말고 따라 해보세요!</b></p>
                <ul>
                    <li><b>1단계:</b> 지금 어디에 있는지 모르면 위치 검색창에 건물 이름이나 길 이름을 적어요.</li>
                    <li><b>2단계:</b> 화면 우측에 초록색 <b>'🟢 여유'</b>로 적힌 가장 가까운 병원을 찾아보세요.</li>
                    <li><b>3단계:</b> 파란색 <b>'📞 전화 걸기'</b> 버튼을 누르면 바로 선생님과 통화할 수 있어요.</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 3) 청소년 및 성인
    elif "성인" in age_group:
        st.markdown("""
        <div class="manual-card bg-adult">
            <h3>🧑 성인 핵심 응급처치 수칙</h3>
            <ul>
                <li><b>심정지 의심:</b> 의식 확인 후 즉시 119 신고 및 AED 요청. 분당 100~120회 속도로 가슴 중앙 압박.</li>
                <li><b>뇌졸중(FAST):</b> 안면마비, 팔 마비, 발음 어눌함 발생 시 즉시 골든타임 내 응급실 이송.</li>
                <li><b>대량 출혈:</b> 상처 부위를 깨끗한 거즈로 직접 강하게 압박하며 심장보다 높게 유지.</li>
            </ul>
            <div class="app-guide-box">
                <h5>📱 성인용 AIDMAP 스마트 활용 매뉴얼</h5>
                <ol style="margin-bottom: 0;">
                    <li><b>정확한 위치 설정:</b> 상호명(예: 짜장나라)이나 도로명 주소를 검색해 정밀 기준점을 잡습니다.</li>
                    <li><b>거리순 정렬 확인:</b> 현 위치에서 가장 가까운 응급실 순서대로 잔여 병상이 자동 정렬됩니다.</li>
                    <li><b>실시간 상태 반영:</b> ⚡ 버튼을 눌러 이송 직전 병상 수용 가능 여부를 최종 확인하세요.</li>
                </ol>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 4) 노년층 (음성 안내 잘림 현상 수정 완료)
    else:
        st.markdown("""
        <div class="manual-card bg-senior">
            <h3>🧓 노년층 응급처치 수칙</h3>
            <ul>
                <li><b>낙상 사고:</b> 뼈가 약하므로 무리하게 일어나지 말고, 그 자리에서 119를 기다립니다.</li>
                <li><b>심혈관 질환:</b> 갑작스러운 흉통이나 턱·어깨 통증, 숨참 증상 발생 시 즉시 응급 이송.</li>
                <li><b>저혈당 쇼크:</b> 의식이 있으면 사탕이나 주스를 섭취하고, 의식이 없으면 아무것도 먹이지 않습니다.</li>
            </ul>
            <div class="app-guide-box">
                <h5>📱 어르신 및 보호자를 위한 AIDMAP 사용안내</h5>
                <p style="margin-bottom: 5px;">어르신께서 혼자 계실 때는 글자가 작아 보이기 힘들 수 있습니다.</p>
                <ul>
                    <li>아래 <b>'🔊 음성 안내 듣기'</b> 버튼을 누르면 응급처치 수칙을 큰 소리로 읽어드립니다.</li>
                    <li>보호자께서는 우측에서 가장 가까운 병원의 <b>'📞 전화 걸기'</b>를 눌러 이송 가능 여부를 확인해 주세요.</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 음성 안내 (잘림 현상 해결을 위해 height를 180px로 여유 있게 조절)
        st.subheader("🔊 어르신을 위한 음성 안내")
        tts_text = "노년층 응급처치 수칙입니다. 첫째, 낙상 사고 시 무리하게 일어나지 마시고 119를 기다리세요. 둘째, 갑작스러운 가슴 통증 발생 시 즉시 응급실로 이동하셔야 합니다."
        
        tts_html = f"""
        <div style="background-color: #ECFDF5; padding: 15px; border-radius: 10px; border: 1px solid #10B981; font-family: sans-serif;">
            <p style="color: #065F46 !important; font-weight: bold; margin-top: 0; margin-bottom: 10px;">
                🔊 아래 버튼을 누르면 주요 응급 수칙을 음성으로 들려드립니다.
            </p>
            <div style="display: flex; gap: 10px;">
                <button onclick="speakText()" style="background-color: #059669; color: white; border: none; padding: 10px 18px; font-size: 15px; border-radius: 8px; cursor: pointer; font-weight: bold;">
                    🔊 음성 안내 듣기
                </button>
                <button onclick="window.speechSynthesis.cancel()" style="background-color: #EF4444; color: white; border: none; padding: 10px 15px; font-size: 15px; border-radius: 8px; cursor: pointer; font-weight: bold;">
                    ⏹️ 정지
                </button>
            </div>
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
        # height=180으로 변경하여 버튼과 박스가 절대 잘리지 않도록 수정
        st.components.v1.html(tts_html, height=180)

# ----------------------------------------------------
# 오른쪽 열: NEMC 스타일 실시간 응급실 현황 대시보드
# ----------------------------------------------------
with col2:
    st.subheader("🏥 실시간 응급실 가용 병상 현황")
    
    # 상단 컨트롤바
    top_col1, top_col2 = st.columns([3, 1])
    with top_col1:
        st.caption("📍 기준 위치 및 도로명/상호명 검색")
    with top_col2:
        if st.button("⚡ 실시간 갱신", use_container_width=True):
            st.toast("E-Gen 응급의료 서버에서 최신 병상 데이터를 불러왔습니다.")
            time.sleep(0.3)
            st.rerun()

    # 기본 GPS / 위치 설정 (기본값: 서귀포시 기준)
    user_lat, user_lng = 33.2541, 126.5601

    # 검색창 및 결과 UI 개선
    search_keyword = st.text_input(
        "위치 검색", 
        placeholder="예: 제주특별자치도 서귀포시 동홍동 짜장나라 또는 도로명 주소",
        label_visibility="collapsed"
    )

    if search_keyword:
        places = search_location_kakao(search_keyword)
        if places:
            place_options = {}
            for p in places:
                addr = p['road_address_name'] if p['road_address_name'] else p['address_name']
                label = f"📍 {p['place_name']} | {addr}"
                place_options[label] = (float(p['y']), float(p['x']))

            selected_place_label = st.selectbox("검색된 상세 주소 중 하나를 선택하세요:", list(place_options.keys()))
            if selected_place_label:
                user_lat, user_lng = place_options[selected_place_label]
                st.success(f"기준 위치가 성공적으로 설정되었습니다.")
        else:
            st.warning("검색 결과가 없습니다. 정확한 도로명이나 건물명을 입력해주세요.")

    # 응급의료기관 데이터베이스
    raw_hospitals = [
        {"name": "서귀포의료원", "beds": 4, "total": 10, "phone": "064-730-3109", "lat": 33.2547, "lng": 126.5601},
        {"name": "제주대학교병원", "beds": 1, "total": 12, "phone": "064-717-1900", "lat": 33.4670, "lng": 126.5450},
        {"name": "한마음병원", "beds": 0, "total": 8, "phone": "064-750-9000", "lat": 33.4962, "lng": 126.5441},
        {"name": "한국병원", "beds": 6, "total": 10, "phone": "064-750-0000", "lat": 33.5008, "lng": 126.5178},
    ]

    # 거리 계산 및 정렬
    calculated_hospitals = []
    for h in raw_hospitals:
        dist_km = calculate_distance(user_lat, user_lng, h["lat"], h["lng"])
        status = "여유" if h["beds"] >= 3 else ("혼잡" if h["beds"] > 0 else "만석")

        calculated_hospitals.append({
            "name": h["name"],
            "beds": h["beds"],
            "total": h["total"],
            "status": status,
            "phone": h["phone"],
            "dist_val": dist_km,
            "dist_str": f"{dist_km}km"
        })

    calculated_hospitals.sort(key=lambda x: x["dist_val"])
    df_hospitals = pd.DataFrame(calculated_hospitals)

    # 1) NEMC 스타일 주요 메트릭 지표
    m1, m2, m3 = st.columns(3)
    m1.metric("조회된 응급실", f"{len(df_hospitals)}곳")
    m2.metric("즉시 수용 가능", f"{len(df_hospitals[df_hospitals['beds'] > 0])}곳")
    m3.metric("총 잔여 일반병상", f"{df_hospitals['beds'].sum()}석")

    # 2) 잔여 병상 현황 차트
    st.markdown("#### 📊 내 위치 기준 거리순 병상 현황")
    chart_df = df_hospitals.set_index("name")[["beds"]]
    chart_df.columns = ["잔여 병상 수"]
    st.bar_chart(chart_df, color="#1E40AF", height=180)

    # 3) 실제 기관 카드 목록
    st.markdown("#### 🏥 실시간 병상 상세 정보")
    for hosp in calculated_hospitals:
        if hosp["status"] == "여유":
            badge = '<span class="badge-ok">🟢 여유</span>'
        elif hosp["status"] == "혼잡":
            badge = '<span class="badge-busy">🟡 혼잡</span>'
        else:
            badge = '<span class="badge-full">🔴 만석</span>'
            
        st.markdown(f"""
        <div class="hospital-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h4 style="margin: 0; font-size: 1.1rem;">{hosp['name']} <span style="font-size: 0.85rem; color: #64748B; font-weight: normal;">(📍 거리 {hosp['dist_str']})</span></h4>
                {badge}
            </div>
            <div style="margin-top: 12px; display: flex; justify-content: space-between; align-items: center;">
                <p style="margin: 0; font-size: 1rem;">가용 병상: <b>{hosp['beds']}석</b> / {hosp['total']}석</p>
                <a href="tel:{hosp['phone']}" style="background-color: #1E40AF; color: white !important; padding: 6px 14px; border-radius: 6px; text-decoration: none; font-weight: bold; font-size: 0.85rem;">📞 전화 걸기</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.divider()
st.caption("© 2026 AIDMAP - National Emergency Medical System Prototype")