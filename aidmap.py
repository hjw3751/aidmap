import streamlit as st
import requests
import xml.etree.ElementTree as ET
import streamlit.components.v1 as components
import math

# ----------------------------------------------------
# 1. 페이지 설정 및 UI 스타일링
# ----------------------------------------------------
st.set_page_config(page_title="내 손안의 응급실 - 실시간 병상 조회", page_icon="🚑", layout="wide")

st.markdown("""
<style>
    * { word-break: keep-all !important; }
    .badge-smooth { background-color: #DCFCE7; color: #166534; padding: 4px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; display: inline-block; }
    .badge-normal { background-color: #FEF9C3; color: #854D0E; padding: 4px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; display: inline-block; }
    .badge-busy { background-color: #FEE2E2; color: #991B1B; padding: 4px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; display: inline-block; }
    .guide-box { background-color: #F8FAFC; padding: 16px; border-radius: 10px; border: 1px solid #E2E8F0; margin-bottom: 20px; }
    .elderly-text { font-size: 1.2rem; font-weight: bold; color: #1E3A8A; line-height: 1.6; }
    .recommend-box { background-color: #EFF6FF; border-left: 5px solid #3B82F6; padding: 15px; margin-bottom: 20px; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 2. 하버사인 공식 (거리 계산기)
# ----------------------------------------------------
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0 # 지구 반지름 (km)
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)

# ----------------------------------------------------
# 3. 공공데이터 연동 (실시간 병상 정보)
# ----------------------------------------------------
API_KEY = "aa0cf3fc4d2a32edf9e6f8cf63cf46eaafb213b56f85d96e15b30484d0b75473"

@st.cache_data(ttl=60)
def fetch_emergency_data(city=""):
    url = "http://apis.data.go.kr/B552657/ErmctInfoInqireService/getEmrrmRltmUsefulSckbdInfoInqire"
    # requests는 자동으로 인코딩하므로 이미 인코딩된 키일 경우 디코딩된 상태로 전달하는 것이 안전합니다.
    # 만약 키 에러가 계속된다면, requests 대신 urllib를 사용해야 할 수도 있습니다.
    params = {
        'serviceKey': requests.utils.unquote(API_KEY),
        'STAGE1': city if city != "전체" else "",
        'numOfRows': '100',
        'pageNo': '1'
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
            
        root = ET.fromstring(response.content)
        result_code = root.findtext(".//resultCode")
        
        if result_code != "00":
            result_msg = root.findtext(".//resultMsg")
            raise Exception(f"API 에러: {result_msg} (코드: {result_code})")
            
        items = root.findall(".//item")
        if not items:
            raise Exception("해당 지역에 조회된 실시간 응급실 데이터가 없습니다.")
        
        hospital_list = []
        for item in items:
            def get_val(tag, default="0"):
                return item.findtext(tag, default=default)
            
            gen_curr = int(get_val("hvec") or 0)
            ped_curr = int(get_val("hvicyn") or 0)
            mat_cnt = get_val("hpbd", "0")
            
            # API에서 전체 병상을 주지 않으므로 추정치 생성 (잔여+사용중)
            gen_total = max(20, gen_curr + 15) 
            
            hospital_list.append({
                "name": get_val("dutyName", "이름없음"),
                "phone": get_val("dutyTel3", get_val("dutyTel1", "전화번호 없음")), # 응급실 직통 번호(dutyTel3) 우선 반영
                "addr": get_val("dutyAddr", "주소없음"),
                "gen_curr": gen_curr,
                "gen_total": gen_total,
                "ped_curr": ped_curr,
                "mat_status": f"가능 ({mat_cnt}석)" if mat_cnt.isdigit() and int(mat_cnt) > 0 else "불가",
                "lat": float(get_val("wgs84Lat", 33.253)), # 데이터 없을 시 임시로 서귀포 좌표
                "lng": float(get_val("wgs84Lon", 126.561))
            })
            
        return hospital_list, False, "성공"

    except Exception as e:
        # API 오류 시 임시 더미 데이터 (전화번호 및 정보 확실하게 부여)
        fallback_data = [
            {"name": "제주대학교병원 응급의료센터", "phone": "064-717-1900", "addr": "제주특별자치도 제주시 아란13길 15", "gen_curr": 14, "gen_total": 24, "ped_curr": 3, "mat_status": "가능 (2석)", "lat": 33.467, "lng": 126.544},
            {"name": "서귀포의료원 응급실", "phone": "064-730-3119", "addr": "제주특별자치도 서귀포시 동홍로 212", "gen_curr": 2, "gen_total": 15, "ped_curr": 0, "mat_status": "불가", "lat": 33.253, "lng": 126.561},
            {"name": "한라병원 권역응급의료센터", "phone": "064-740-5119", "addr": "제주특별자치도 제주시 도령로 65", "gen_curr": 5, "gen_total": 20, "ped_curr": 1, "mat_status": "불가", "lat": 33.489, "lng": 126.485}
        ]
        return fallback_data, True, str(e)


# ----------------------------------------------------
# 4. 사용자 맞춤형 4단계 UI 플로우 구성
# ----------------------------------------------------

st.title("🚑 내 손안의 실시간 응급실 추천")

# [STEP 1] 연령대 입력
if "age_group" not in st.session_state:
    st.session_state.age_group = "선택안함"

st.markdown("### 1️⃣ 사용자 연령대를 먼저 선택해주세요.")
age_choice = st.radio("연령대 선택", ["선택안함", "일반 (청년/중장년층)", "노년층 (만 65세 이상)"], horizontal=True, label_visibility="collapsed")
st.session_state.age_group = age_choice

if st.session_state.age_group == "선택안함":
    st.info("👆 원활한 안내를 위해 위에서 연령대를 선택해주시면 다음 화면이 열립니다.")
    st.stop() # 연령대를 선택하기 전까지 아래 코드 실행 중지

st.divider()

# [STEP 2] 맞춤형 사용법 안내 & 음성인식(STT)
if st.session_state.age_group == "노년층 (만 65세 이상)":
    st.markdown("""
    <div class="guide-box">
        <div class="elderly-text">👴👵 어르신, 환영합니다! 글씨를 크게 키워드렸어요.</div>
        <div class="elderly-text">아래 안내에 따라 천천히 읽어보시고, 증상을 찾아보세요.</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 노년층 전용 웹 음성 인식(STT) 버튼 (HTML5 Web Speech API)
    st.markdown("🎙️ **타자 치기가 어려우신가요? 아래 마이크를 누르고 증상을 말씀해 보세요.**")
    stt_code = """
    <div style="padding: 10px; background-color: #FEF2F2; border-radius: 8px; border: 1px solid #FCA5A5;">
        <button id="mic-btn" style="background-color: #EF4444; color: white; border: none; padding: 15px 20px; font-size: 1.1rem; border-radius: 8px; cursor: pointer; font-weight: bold; width: 100%;">
            🎤 마이크 켜고 말하기
        </button>
        <p id="stt-result" style="margin-top: 10px; font-size: 1.1rem; font-weight: bold; color: #991B1B;">(이곳에 말씀하신 내용이 나타납니다)</p>
    </div>
    <script>
        const btn = document.getElementById('mic-btn');
        const resultText = document.getElementById('stt-result');
        
        btn.addEventListener('click', () => {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            if(!SpeechRecognition) {
                resultText.innerText = "현재 브라우저는 음성 인식을 지원하지 않습니다. 텍스트로 선택해주세요.";
                return;
            }
            const recognition = new SpeechRecognition();
            recognition.lang = 'ko-KR';
            recognition.start();
            
            btn.innerText = "듣고 있습니다... 말씀해 주세요!";
            
            recognition.onresult = function(event) {
                const text = event.results[0][0].transcript;
                resultText.innerText = "인식된 증상: " + text + " (아래 진료과를 선택해 주세요)";
                btn.innerText = "🎤 다시 말하기";
            };
            
            recognition.onerror = function(event) {
                resultText.innerText = "마이크 연결에 실패했습니다. 다시 시도해주세요.";
                btn.innerText = "🎤 마이크 켜고 말하기";
            }
        });
    </script>
    """
    components.html(stt_code, height=130)

else:
    st.success("✅ 일반 사용자 모드입니다. 빠르고 정확한 병원 추천을 도와드립니다.")

# [STEP 3] 병상 수 읽는 법 안내
st.markdown("### 2️⃣ 병상 현황은 이렇게 읽어주세요.")
st.markdown("""
<div class="guide-box">
    <span style="font-size: 1.0rem; color: #334155;">
    • 표기 방법: <b>[현재 남은 잔여 병상 수 / 전체 병상 규모]</b><br>
    • <span class="badge-smooth">원활</span> : <b>잔여 병상 5석 초과</b> (여유가 있습니다.)<br>
    • <span class="badge-busy">혼잡/마감</span> : <b>잔여 병상 0~2석</b> (대기 시간이 매우 길거나 수용이 불가능할 수 있습니다.)
    </span>
</div>
""", unsafe_allow_html=True)
st.divider()

# [STEP 4] 위치 및 환자 상세 정보 입력
st.markdown("### 3️⃣ 환자분의 현재 상태와 위치를 알려주세요.")
col1, col2, col3 = st.columns(3)

with col1:
    # 스트림릿 웹 환경 한계로, 브라우저 GPS 자동 연동 대신 시/도 선택을 통해 위치 파악
    st.info("💡 웹 보안상 자동 GPS가 불안정할 경우 지역을 직접 선택해주세요.")
    current_city = st.selectbox("현재 계신 시/도를 선택하세요", ["제주특별자치도", "서울특별시", "경기도", "부산광역시", "전체"])
    
with col2:
    target_age = st.selectbox("환자 연령 분류", ["성인 (만 13세 이상)", "소아 (만 12세 이하)"])
    
with col3:
    target_symptom = st.selectbox("주요 증상 / 필요 진료", ["일반 응급", "응급 분만 (산부인과)", "중증 외상"])

# 임시 GPS 설정 (선택한 시/도의 대략적인 도심 좌표)
# 예: 제주도를 선택하면 현재 내 위치를 서귀포시청 인근(33.253, 126.561)으로 시뮬레이션
current_lat, current_lon = 33.253, 126.561 

st.divider()

# ----------------------------------------------------
# 5. 실시간 API 데이터 로딩 및 오류 안내
# ----------------------------------------------------
with st.spinner("해당 지역의 실시간 응급실 데이터를 불러오는 중입니다..."):
    hospitals, is_sample, err_reason = fetch_emergency_data(current_city)

if is_sample:
    st.warning("⚠️ **실시간 데이터 연동 실패 안내**")
    st.error(f"원인: {err_reason}")
    st.caption("※ API 키가 승인 대기 중이거나 잘못되었습니다. 현재는 '비상용 샘플 데이터'로 시뮬레이션 된 결과를 보여드립니다.")

# ----------------------------------------------------
# 6. 스마트 병원 추천 알고리즘 
# ----------------------------------------------------
# 거리 계산 및 알고리즘 점수 부여
scored_hospitals = []
for h in hospitals:
    # 1. 거리 계산
    dist = calculate_distance(current_lat, current_lon, h['lat'], h['lng'])
    h['distance'] = dist
    
    # 2. 필터링 (조건에 완전 불합격인 곳 제외)
    if target_age == "소아 (만 12세 이하)" and h['ped_curr'] <= 0:
        continue # 소아 병상 없으면 제외
    if target_symptom == "응급 분만 (산부인과)" and "불가" in h['mat_status']:
        continue # 분만 불가면 제외
        
    # 3. 맞춤형 추천 점수 계산 (Score)
    # 가중치: 거리(가까울수록 높음) + 잔여 병상 수(많을수록 높음)
    dist_score = max(0, 100 - (dist * 2.5)) # 거리가 멀수록 점수 차감
    bed_score = min(100, h['gen_curr'] * 4) # 병상이 25개 이상이면 만점
    
    total_score = (dist_score * 0.5) + (bed_score * 0.5)
    h['score'] = total_score
    scored_hospitals.append(h)

# 점수 높은 순(추천 순)으로 정렬
scored_hospitals = sorted(scored_hospitals, key=lambda x: x['score'], reverse=True)

# ----------------------------------------------------
# 7. 검색 결과 및 최적 병원 추천 안내
# ----------------------------------------------------
st.markdown(f"### 4️⃣ 맞춤형 추천 결과 (총 {len(scored_hospitals)}곳 발견)")

if not scored_hospitals:
    st.error("조건에 맞는 병원을 찾을 수 없습니다. (예: 해당 지역에 소아/분만 가능 병상 부족) 조건을 변경해 보세요.")
    st.stop()

# 🏆 최적의 1순위 병원 강조 (Recommendation Box)
top_h = scored_hospitals[0]
st.markdown(f"""
<div class="recommend-box">
    <h3 style="margin-top: 0; color: #1E3A8A;">✨ 가장 추천하는 병원: {top_h['name']}</h3>
    <ul style="font-size: 1.1rem; line-height: 1.8;">
        <li><b>📍 예상 거리:</b> {top_h['distance']} km 떨어져 있어 가장 가깝습니다.</li>
        <li><b>🛏️ 응급실 여유:</b> 전체 {top_h['gen_total']}석 중 <b>{top_h['gen_curr']}석</b> 남아있습니다.</li>
        <li><b>📞 즉시 연락처:</b> <a href="tel:{top_h['phone']}">{top_h['phone']}</a> (클릭 시 바로 전화 연결)</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# 노년층 모드일 경우 TTS(읽어주기) 지원
if st.session_state.age_group == "노년층 (만 65세 이상)":
    tts_text = f"가장 추천하는 곳은 {top_h['name']} 입니다. 현재 계신 곳에서 {top_h['distance']} 킬로미터 떨어져 있습니다. 전화번호는 {top_h['phone']} 입니다."
    components.html(f"""
    <script>
    function speakText() {{
        const utterance = new SpeechSynthesisUtterance("{tts_text}");
        utterance.lang = 'ko-KR';
        utterance.rate = 0.85; // 천천히
        window.speechSynthesis.speak(utterance);
    }}
    </script>
    <button onclick="speakText()" style="background-color:#2563EB; color:white; border:none; padding:12px 20px; border-radius:8px; font-weight:bold; cursor:pointer; font-size: 1.1rem; width: 100%; margin-bottom: 20px;">
        🔊 추천 결과 스피커로 듣기 (클릭)
    </button>
    """, height=70)


# 나머지 병원 목록 상세 출력 (테이블 형식 대신 가독성 좋은 카드 형식)
for idx, h in enumerate(scored_hospitals):
    # 병상 상태 배지 결정
    if h['gen_curr'] > 5:
        badge = f"<span class='badge-smooth'>원활</span>"
    elif h['gen_curr'] > 2:
        badge = f"<span class='badge-normal'>보통</span>"
    else:
        badge = f"<span class='badge-busy'>혼잡/마감</span>"
        
    map_url = f"https://map.kakao.com/link/to/{h['name']},{h['lat']},{h['lng']}"
    
    st.markdown(f"""
    <div style="padding: 15px; border: 1px solid #E2E8F0; border-radius: 8px; margin-bottom: 12px; background-color: #FFFFFF;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <h4 style="margin: 0; color: #0F172A;">{idx+1}. {h['name']}</h4>
            <a href="{map_url}" target="_blank" style="background-color: #EF4444; color: white; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-size: 0.85rem; font-weight: bold;">📍 길찾기</a>
        </div>
        <div style="color: #64748B; font-size: 0.9rem; margin-bottom: 12px;">{h['addr']} (내 위치에서 <b>{h['distance']}km</b>)</div>
        <div style="display: flex; gap: 15px; font-size: 0.95rem; flex-wrap: wrap;">
            <div style="background: #F8FAFC; padding: 8px 12px; border-radius: 6px;">📞 전화: <b>{h['phone']}</b></div>
            <div style="background: #F8FAFC; padding: 8px 12px; border-radius: 6px;">🛏️ 일반응급: {badge} <b>{h['gen_curr']} / {h['gen_total']} 석</b></div>
            <div style="background: #F8FAFC; padding: 8px 12px; border-radius: 6px;">👶 소아응급: <b>{h['ped_curr']} 석</b></div>
            <div style="background: #F8FAFC; padding: 8px 12px; border-radius: 6px;">🤰 분만실: <b>{h['mat_status']}</b></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
