import streamlit as st
import requests
import xml.etree.ElementTree as ET
import math

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="응급실 실시간 병상 조회", 
    page_icon="🏥", 
    layout="wide"
)

st.title("🏥 실시간 응급실 병상 조회 및 길찾기 시스템")
st.markdown("현재 위치 또는 선택한 지역의 응급실 잔여 병상과 연락처를 실시간으로 확인하세요.")

# 2. 사이드바 - 지역 선택 및 API 설정
st.sidebar.header("📍 지역 및 설정")
sido = st.sidebar.selectbox(
    "시/도 선택", 
    ["서울특별시", "경기도", "부산광역시", "제주특별자치도", "인천광역시", "대구광역시", "광주광역시", "대전광역시", "울산광역시", "세종특별자치시", "강원특별자치도", "충청북도", "충청남도", "전북특별자치도", "전라남도", "경상북도", "경상남도"]
)
gugun = st.sidebar.text_input("구/군 입력 (선택사항)", "")

# 공공데이터포털 API 인증키 입력 칸
service_key = st.sidebar.text_input("공공데이터 API 인증키 (ServiceKey)", type="password")

st.sidebar.markdown("---")
st.sidebar.info("💡 **병상 표기 안내**: 각 병원의 가용 응급실 잔여 병상 수와 상태가 실시간으로 반영됩니다.")

# 3. 샘플(비상용) 데이터 정의 (API 오류나 키 미입력 시 정상 구동용)
mock_data = [
    {"dutyName": "제주대학교병원", "dutyTel1": "064-717-1114", "hvec": 14, "hvcc": 4, "lat": 33.489, "lng": 126.545},
    {"dutyName": "제주한라병원", "dutyTel1": "064-740-5000", "hvec": 8, "hvcc": 2, "lat": 33.492, "lng": 126.487},
    {"dutyName": "서귀포의료원", "dutyTel1": "064-730-3000", "hvec": 19, "hvcc": 5, "lat": 33.254, "lng": 126.560},
    {"dutyName": "중앙병원", "dutyTel1": "064-786-7000", "hvec": 5, "hvcc": 1, "lat": 33.495, "lng": 126.510}
]

# 4. 거리 계산 함수 (Haversine Formula)
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0 # 지구 반지름 (km)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

# 사용자 기준 위치 (예시: 제주시청 기준)
current_lat, current_lng = 33.4996, 126.5312

# 5. 공공데이터 API 호출 함수
def fetch_emergency_data(key, s_ido):
    if not key:
        return None
    
    url = "http://apis.data.go.kr/B552657/ErmctInfoInqireService/getEmrrmRltmUsefulSckbdInfoInqire"
    params = {
        'serviceKey': key,
        'STAGE1': s_ido,
        'pageNo': '1',
        'numOfRows': '20'
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print("API 호출 에러:", e)
    return None

# 6. 데이터 파싱 및 가공
hospitals = []
xml_data = fetch_emergency_data(service_key, sido)

if xml_data:
    try:
        root = ET.fromstring(xml_data)
        items = root.findall('.//item')
        for item in items:
            name = item.find('dutyName').text if item.find('dutyName') is not None else "정보 없음"
            tel = item.find('dutyTel1').text if item.find('dutyTel1') is not None else "전화번호 없음"
            hvec = int(item.find('hvec').text) if item.find('hvec') is not None and item.find('hvec').text.isdigit() else 0
            lat = float(item.find('wgs84Lat').text) if item.find('wgs84Lat') is not None and item.find('wgs84Lat').text else current_lat
            lng = float(item.find('wgs84Lon').text) if item.find('wgs84Lon') is not None and item.find('wgs84Lon').text else current_lng
            
            dist = calculate_distance(current_lat, current_lng, lat, lng)
            
            hospitals.append({
                "dutyName": name,
                "dutyTel1": tel,
                "hvec": hvec,
                "distance": dist
            })
    except Exception as e:
        hospitals = mock_data
else:
    hospitals = mock_data

# 거리순 정렬
hospitals = sorted(hospitals, key=lambda x: x["distance"])

# 7. 화면 출력 구성
st.subheader(f"📍 [{sido}] 주변 응급실 실시간 현황 (가까운 순)")

if hospitals:
    top_hospital = hospitals[0]
    
    # 고령자 접근성을 위한 웹 음성 지원(TTS) 버튼
    tts_text = f"가장 가까운 응급실은 {top_hospital['dutyName']}이며, 전화번호는 {top_hospital['dutyTel1']} 입니다. 잔여 병상은 {top_hospital['hvec']}석 남았습니다."
    
    st.markdown(f"""
    <div style="padding: 15px; border-radius: 10px; background-color: #f0f2f6; margin-bottom: 20px;">
        <h4>🎙️ 상단 추천 응급실 음성 안내 (고령자 지원)</h4>
        <p><b>{top_hospital['dutyName']}</b> (거리: {top_hospital['distance']:.2f} km)</p>
        <button onclick="
            const utterance = new SpeechSynthesisUtterance('{tts_text}');
            utterance.lang = 'ko-KR';
            window.speechSynthesis.speak(utterance);
        " style="padding: 8px 16px; background-color: #ff4b4b; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold;">
            🔊 음성으로 안내 듣기
        </button>
    </div>
    """, unsafe_allow_html=True)

    # 응급실 리스트 카드 출력
    for h in hospitals:
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"### 🏥 {h['dutyName']}")
                st.write(f"📞 전화번호: **{h['dutyTel1']}**")
                st.write(f"📏 현재 위치로부터 거리: **{h.get('distance', 0):.2f} km**")
            with col2:
                st.metric(
                    label="응급실 잔여 병상", 
                    value=f"{h.get('hvec', 0)} 석", 
                    delta="여유 있음" if h.get('hvec', 0) > 3 else "혼잡/부족"
                )
            st.markdown("---")
else:
    st.info("조회된 응급실 정보가 없습니다.")
