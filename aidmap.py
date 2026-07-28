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
    .reason-text { font-size: 0.95rem; color: #047857; background-color: #D1FAE5; padding: 8px 12px; border-radius: 6px; margin-top: 10px; display: inline-block; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 2. 하버사인 공식 (거리 계산기)
# ----------------------------------------------------
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)

# ----------------------------------------------------
# 3. 공공데이터 연동 (기본정보 API + 실시간 API 병합)
# ----------------------------------------------------
API_KEY = "aa0cf3fc4d2a32edf9e6f8cf63cf46eaafb213b56f85d96e15b30484d0b75473"

@st.cache_data(ttl=60)
def fetch_real_emergency_data(city):
    api_key_decoded = requests.utils.unquote(API_KEY)
    
    # [API 1] 응급의료기관 기본정보 (주소, 좌표, 전화번호 확보용)
    url_basic = "http://apis.data.go.kr/B552657/ErmctInfoInqireService/getErmctInfoInqire"
    params_basic = {
        'serviceKey': api_key_decoded,
        'STAGE1': city if city != "전체" else "",
        'numOfRows': '100',
        'pageNo': '1'
    }
    
    # [API 2] 실시간 병상정보 (잔여 병상수 확보용)
    url_rt = "http://apis.data.go.kr/B552657/ErmctInfoInqireService/getEmrrmRltmUsefulSckbdInfoInqire"
    params_rt = {
        'serviceKey': api_key_decoded,
        'STAGE1': city if city != "전체" else "",
        'numOfRows': '100',
        'pageNo': '1'
    }
    
    hospital_dict = {}
    
    try:
        # 1. 기본 정보 호출 및 파싱 (hpid를 키값으로 사용)
        res_basic = requests.get(url_basic, params=params_basic, timeout=10)
        res_basic.raise_for_status()
        root_basic = ET.fromstring(res_basic.content)
        
        if root_basic.findtext(".//resultCode") != "00":
            raise Exception("기본정보 API 오류: " + root_basic.findtext(".//resultMsg"))
            
        for item in root_basic.findall(".//item"):
            hpid = item.findtext("hpid")
            if not hpid: continue
            
            # 위경도 데이터가 없는 병원은 제외 (가상 좌표 절대 사용 안함)
            lat_str = item.findtext("wgs84Lat")
            lon_str = item.findtext("wgs84Lon")
            if not lat_str or not lon_str:
                continue
                
            hospital_dict[hpid] = {
                "hpid": hpid,
                "name": item.findtext("dutyName", "이름없음"),
                "addr": item.findtext("dutyAddr", "주소없음"),
                "phone": item.findtext("dutyTel3") or item.findtext("dutyTel1", "전화번호 없음"),
                "lat": float(lat_str),
                "lng": float(lon_str),
                # 아래 값들은 실시간 API에서 채워짐 (기본값 세팅)
                "gen_curr": 0, "ped_curr": 0, "mat_curr": 0, "has_realtime": False
            }
            
        # 2. 실시간 병상 정보 호출 및 병합
        res_rt = requests.get(url_rt, params=params_rt, timeout=10)
        res_rt.raise_for_status()
        root_rt = ET.fromstring(res_rt.content)
        
        if root_rt.findtext(".//resultCode") != "00":
            raise Exception("실시간 API 오류: " + root_rt.findtext(".//resultMsg"))
            
        for item in root_rt.findall(".//item"):
            hpid = item.findtext("hpid")
            if hpid in hospital_dict:
                # hvec: 응급실 잔여, hvicyn: 소아응급 잔여, hpbd: 산부인과 잔여
                hospital_dict[hpid]["gen_curr"] = int(item.findtext("hvec", "0"))
                hospital_dict[hpid]["ped_curr"] = int(item.findtext("hvicyn", "0"))
                hospital_dict[hpid]["mat_curr"] = int(item.findtext("hpbd", "0"))
                hospital_dict[hpid]["has_realtime"] = True
                
        # 실시간 데이터가 매핑된 병원만 반환
        final_list = [h for h in hospital_dict.values() if h["has_realtime"]]
        
        if not final_list:
            raise Exception("조건에 맞는 병원 데이터가 없습니다. (API 응답 없음)")
            
        return final_list, None

    except Exception as e:
        # 가상 데이터(Fallback) 전면 폐지 - 에러 발생 시 그대로 에러 반환
        return [], str(e)


# ----------------------------------------------------
# 4. 사용자 맞춤형 UI 
# ----------------------------------------------------
st.title("🚑 내 손안의 실시간 응급실 추천")

if "age_group" not in st.session_state:
    st.session_state.age_group = "선택안함"

st.markdown("### 1️⃣ 사용자 연령대를 먼저 선택해주세요.")
age_choice = st.radio("연령대 선택", ["선택안함", "일반 (청년/중장년층)", "노년층 (만 65세 이상)"], horizontal=True, label_visibility="collapsed")
st.session_state.age_group = age_choice

if st.session_state.age_group == "선택안함":
    st.info("👆 원활한 안내를 위해 위에서 연령대를 선택해주시면 다음 화면이 열립니다.")
    st.stop()

st.divider()

if st.session_state.age_group == "노년층 (만 65세 이상)":
    st.markdown("""
    <div class="guide-box">
        <div class="elderly-text">👴👵 어르신, 환영합니다! 글씨를 크게 키워드렸어요.</div>
        <div class="elderly-text">아래 마이크 버튼을 눌러 증상을 말씀해 주시면 더 편리합니다.</div>
    </div>
    """, unsafe_allow_html=True)
    
    stt_code = """
    <div style="padding: 10px; background-color: #FEF2F2; border-radius: 8px;">
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
            if(!SpeechRecognition) return;
            const recognition = new SpeechRecognition();
            recognition.lang = 'ko-KR';
            recognition.start();
            btn.innerText = "듣고 있습니다...";
            recognition.onresult = (e) => {
                resultText.innerText = "인식된 증상: " + e.results[0][0].transcript + " (아래 진료과를 확인해 주세요)";
                btn.innerText = "🎤 다시 말하기";
            };
        });
    </script>
    """
    components.html(stt_code, height=130)

st.markdown("### 2️⃣ 병상 현황 읽는 법")
st.markdown("""
<div class="guide-box" style="padding: 10px;">
    <span style="font-size: 0.95rem; color: #334155;">
    • 표기: <b>[현재 확보된 잔여 병상 수]</b> (실제 사용 가능한 빈자리만 표시합니다.)<br>
    • 상태: <span class="badge-smooth">원활 (5석 초과)</span> | <span class="badge-busy">혼잡 (0~2석 남음)</span>
    </span>
</div>
""", unsafe_allow_html=True)
st.divider()

st.markdown("### 3️⃣ 환자분의 현재 상태와 위치")

col1, col2, col3 = st.columns(3)
with col1:
    current_city = st.selectbox("📍 현재 지역", ["제주특별자치도", "서울특별시", "경기도", "부산광역시", "전체"])
with col2:
    target_symptom = st.selectbox("🤒 주요 증상", ["선택안함", "고열/오한", "심한 복통", "출혈/외상", "호흡 곤란", "진통(임산부)"])
with col3:
    target_dept = st.selectbox("🏥 필요 진료과", ["응급의학과 (기본)", "소아청소년과", "산부인과", "외과/정형외과"])

# ⚠️ 환자분의 현재 위치(서귀포시 동홍동)의 실제 좌표를 하드코딩 반영
# 서귀포시 동홍동 좌표: 위도 33.2576, 경도 126.5656
if current_city == "제주특별자치도":
    st.info("📍 현재 위치가 **'제주특별자치도 서귀포시 동홍동'**으로 자동 설정되었습니다.")
    current_lat, current_lon = 33.2576, 126.5656
else:
    # 다른 지역 선택 시 해당 지역의 도심 좌표 적용
    locations = {"서울특별시": (37.566, 126.978), "경기도": (37.275, 127.009), "부산광역시": (35.179, 129.075)}
    current_lat, current_lon = locations.get(current_city, (36.5, 127.5))

st.divider()

# ----------------------------------------------------
# 5. 스마트 병원 추천 알고리즘 (실제 데이터 기반)
# ----------------------------------------------------
with st.spinner("100% 실제 공공데이터를 불러와 거리를 계산하는 중입니다..."):
    hospitals, err_reason = fetch_real_emergency_data(current_city)

if err_reason:
    st.error("🚨 공공데이터 API 연동 중 오류가 발생했습니다.")
    st.error(f"오류 내용: {err_reason}")
    st.stop()

scored_hospitals = []
for h in hospitals:
    # 하버사인 공식으로 실제 위경도 기반 거리 도출
    dist = calculate_distance(current_lat, current_lon, h['lat'], h['lng'])
    h['distance'] = dist
    
    # 0석인 특수 병상 필터링
    if target_dept == "소아청소년과" and h['ped_curr'] <= 0:
        continue # 소아 병상 없으면 리스트에서 완전 제외
    if target_dept == "산부인과" and h['mat_curr'] <= 0:
        continue # 산부인과 병상 없으면 리스트에서 완전 제외
        
    # 점수 부여 (거리가 가깝고 잔여 병상이 많을수록 높음)
    dist_score = max(0, 100 - (dist * 2.5)) 
    bed_score = min(100, h['gen_curr'] * 4) 
    h['score'] = (dist_score * 0.6) + (bed_score * 0.4)
    
    # 추천 사유(Reason) 생성
    reasons = []
    if dist < 3.0: reasons.append(f"거리({dist}km)가 매우 가깝고")
    elif dist < 10.0: reasons.append(f"거리({dist}km)가 비교적 양호하며")
    else: reasons.append(f"거리는 다소 멀지만({dist}km)")
        
    if h['gen_curr'] > 5: reasons.append("일반 응급 잔여 병상이 여유롭습니다.")
    elif h['gen_curr'] > 0: reasons.append("일반 응급 병상이 남아있습니다.")
    else: reasons.append("일반 병상은 0석이지만 접수 확인이 필요합니다.")
        
    if target_dept == "소아청소년과":
        reasons.insert(1, f"소아 병상이 {h['ped_curr']}석 남아있으며")
    elif target_dept == "산부인과":
        reasons.insert(1, f"분만실 병상이 {h['mat_curr']}석 남아있으며")
        
    h['reason'] = " ".join(reasons)
    scored_hospitals.append(h)

# 점수순(추천순) 정렬
scored_hospitals = sorted(scored_hospitals, key=lambda x: x['score'], reverse=True)

# ----------------------------------------------------
# 6. 검색 결과 출력
# ----------------------------------------------------
st.markdown(f"### 4️⃣ 맞춤형 추천 결과 (조건에 맞는 병원: 총 {len(scored_hospitals)}곳)")

if not scored_hospitals:
    st.warning("조건에 맞는 병원을 찾지 못했습니다. (예: 현재 제주 지역에 잔여 소아/분만 병상이 0석인 경우) 진료과를 '응급의학과'로 변경해보세요.")
    st.stop()

# 🏆 최적 1순위 병원 강조
top_h = scored_hospitals[0]
st.markdown(f"""
<div class="recommend-box">
    <h3 style="margin-top: 0; color: #1E3A8A;">✨ AI 최적 추천: {top_h['name']}</h3>
    <div class="reason-text">💡 <b>추천 이유:</b> {top_h['reason']}</div>
    <ul style="font-size: 1.05rem; line-height: 1.8; margin-top: 15px;">
        <li><b>📍 실측 예상 거리:</b> 현재 동홍동 위치 기준 약 <b>{top_h['distance']} km</b></li>
        <li><b>🛏️ 응급 잔여 병상:</b> 현재 <b>{top_h['gen_curr']}석</b> 비어있음</li>
        <li><b>📞 병원 즉시 연락:</b> <a href="tel:{top_h['phone']}">{top_h['phone']}</a></li>
        <li style="font-size: 0.95rem; color: #475569;">주소: {top_h['addr']}</li>
    </ul>
</div>
""", unsafe_allow_html=True)

# 목록 출력 (거짓 병상 수 비율 삭제, 순수 잔여 병상만 표시)
for idx, h in enumerate(scored_hospitals):
    badge = "<span class='badge-smooth'>원활</span>" if h['gen_curr'] > 5 else ("<span class='badge-normal'>보통</span>" if h['gen_curr'] > 0 else "<span class='badge-busy'>혼잡/마감</span>")
    map_url = f"https://map.kakao.com/link/to/{h['name']},{h['lat']},{h['lng']}"
    
    st.markdown(f"""
    <div style="padding: 15px; border: 1px solid #E2E8F0; border-radius: 8px; margin-bottom: 12px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
            <h4 style="margin: 0;">{idx+1}. {h['name']} <span style="font-size: 0.8rem; color: #64748B;">(직선거리 {h['distance']}km)</span></h4>
            <a href="{map_url}" target="_blank" style="background-color: #EF4444; color: white; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-size: 0.8rem; font-weight: bold;">📍 길찾기</a>
        </div>
        <div style="font-size: 0.85rem; color: #475569; margin-bottom: 10px;">{h['addr']}</div>
        <div style="display: flex; gap: 10px; font-size: 0.9rem; flex-wrap: wrap;">
            <div style="background: #F1F5F9; padding: 6px 10px; border-radius: 6px;">📞 {h['phone']}</div>
            <div style="background: #F1F5F9; padding: 6px 10px; border-radius: 6px;">🛏️ 일반응급 잔여: {badge} <b>{h['gen_curr']}석</b></div>
            <div style="background: #F1F5F9; padding: 6px 10px; border-radius: 6px;">👶 소아 잔여: <b>{h['ped_curr']}석</b></div>
            <div style="background: #F1F5F9; padding: 6px 10px; border-radius: 6px;">🤰 분만실 잔여: <b>{h['mat_curr']}석</b></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
