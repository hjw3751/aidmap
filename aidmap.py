import streamlit as st
import requests
import xml.etree.ElementTree as ET
import math

# ----------------------------------------------------
# 1. 페이지 설정 및 커스텀 CSS
# ----------------------------------------------------
st.set_page_config(page_title="내 손안의 응급실 (실시간)", page_icon="🚑", layout="wide")

st.markdown("""
<style>
    * { word-break: keep-all !important; }
    .hospital-card {
        background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px;
        padding: 20px; margin-bottom: 16px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .best-card {
        background-color: #F0FDF4; border: 2px solid #22C55E; border-radius: 12px;
        padding: 24px; margin-bottom: 24px; box-shadow: 0 4px 12px rgba(34, 197, 94, 0.1);
    }
    .info-grid {
        display: flex; gap: 8px; margin-top: 12px; justify-content: space-between; overflow-x: auto;
    }
    .info-box {
        flex: 1; background-color: #F8FAFC; padding: 8px; border-radius: 8px; text-align: center;
        border: 1px solid #E2E8F0; min-width: 75px;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 2. 실시간 응급실 API 연동 함수 (전체 조회 최적화)
# ----------------------------------------------------
# 사용자가 발급받은 인증키 적용
API_KEY = "aa0cf3fc4d2a32edf9e6f8cf63cf46eaafb213b56f85d96e15b30484d0b75473"

@st.cache_data(ttl=60)
def fetch_realtime_emergency_data(stage1):
    # 국립중앙의료원_전국 응급의료기관 정보 조회 서비스 (실시간 병상 포함 통합 엔드포인트)
    url = "http://apis.data.go.kr/B552657/ErmctInfoInqireService/getEmrRltmSttusInfo"
    
    # STAGE2를 비우고 시/도(STAGE1) 전체로 요청하여 해당 지역의 모든 병원을 누락없이 가져옴
    query_url = f"{url}?serviceKey={API_KEY}&STAGE1={stage1}&numOfRows=100&pageNo=1"
    
    try:
        response = requests.get(query_url, timeout=5)
        if response.status_code != 200:
            return [], f"HTTP 에러: {response.status_code}"
            
        root = ET.fromstring(response.content)
        
        # API 내부 에러 체크
        result_code = root.find(".//resultCode")
        result_msg = root.find(".//resultMsg")
        if result_code is not None and result_code.text != "00":
            return [], f"API 에러 [{result_code.text}]: {result_msg.text if result_msg is not None else '사유 불명'}"
            
        items = root.findall(".//item")
        if not items:
            return [], "해당 지역에 등록된 응급실 데이터가 없습니다."
        
        hospital_list = []
        for item in items:
            def get_text(tag):
                node = item.find(tag)
                return node.text if node is not None and node.text else "-"
            
            gen_curr = int(get_text("hvec")) if get_text("hvec").isdigit() else 0
            ped_curr = int(get_text("hvicyn")) if get_text("hvicyn").isdigit() else 0
            mat_cnt = get_text("hpbd")
            iso_neg = int(get_text("hvcc")) if get_text("hvcc").isdigit() else 0
            
            status = "원활" if gen_curr > 5 else ("보통" if gen_curr > 2 else "혼잡")
            
            lat = float(get_text("wgs84Lat")) if get_text("wgs84Lat").replace('.','',1).isdigit() else 37.5665
            lng = float(get_text("wgs84Lon")) if get_text("wgs84Lon").replace('.','',1).isdigit() else 126.9780
            
            h_data = {
                "name": get_text("dutyName"),
                "gen_curr": gen_curr,
                "ped_curr": ped_curr,
                "mat_status": f"분만 가능 (잔여 {mat_cnt}석)" if mat_cnt.isdigit() and int(mat_cnt) > 0 else "미지원",
                "iso_neg_curr": iso_neg,
                "status": status,
                "phone": get_text("dutyTel1"),
                "lat": lat,
                "lng": lng
            }
            hospital_list.append(h_data)
            
        return hospital_list, None
        
    except Exception as e:
        return [], f"예외 발생: {str(e)}"

# ----------------------------------------------------
# 3. 사이드바: 지역 설정
# ----------------------------------------------------
st.sidebar.markdown("### 📍 실시간 지역 설정")
selected_state = st.sidebar.selectbox(
    "시/도 선택", 
    ["서울특별시", "부산광역시", "대구광역시", "인천광역시", "광주광역시", "대전광역시", "울산광역시", "세종특별자치시", "경기도", "강원특별자치도", "충청북도", "충청남도", "전라북도", "전라남도", "경상북도", "경상남도", "제주특별자치도"]
)

# 데이터 호출 (시/도 전체를 던져서 해당 지역 모든 구/병원이 다 나오도록 함)
current_facilities, error_msg = fetch_realtime_emergency_data(selected_state)

# ----------------------------------------------------
# 4. 메인 화면 레이아웃 및 렌더링
# ----------------------------------------------------
st.markdown(f"### 🚑 내 손안의 응급실 실시간 조회 ({selected_state} 전체 병원)")
st.caption("보건복지부 원본 공공데이터 실시간 연동 중")

if error_msg:
    st.error(f"🚨 연동 에러: {error_msg}")
else:
    st.success(f"✨ 연동 성공! 총 {len(current_facilities)}개의 응급의료기관 데이터를 실시간으로 불러왔습니다.")

st.divider()

col_left, col_right = st.columns([1.0, 1.2], gap="large")

with col_left:
    st.subheader("🩺 환자 상태 입력")
    symptoms = [
        "🦴 심한 외상 및 출혈 (골절 의심)", 
        "🫀 가슴 통증 및 호흡곤란", 
        "🗣️ 갑작스러운 안면 마비 및 말 어눌함",
        "🔥 심한 화상",
        "👶 소아 39도 이상 고열 및 경련"
    ]
    selected_symptom = st.selectbox("현재 가장 심각한 증상을 선택하세요:", symptoms)
    age = st.radio("환자 연령대:", ["영유아", "어린이", "성인", "노년층"], index=2, horizontal=True)

    st.error(f"### 🚨 [{age}] 맞춤 초기 대응 가이드\n\n선택하신 증상에 따라 아래 추천 목록을 참고하여 신속히 이동하시기 바랍니다.")

with col_right:
    st.subheader(f"🏥 실시간 응급의료기관 목록 ({len(current_facilities)}곳)")
    
    if current_facilities:
        # 병상 여유 있는 순으로 정렬
        current_facilities.sort(key=lambda x: x['gen_curr'], reverse=True)
        best_hospital = current_facilities[0]
        other_hospitals = current_facilities[1:]

        # 최우선 권장 병원
        best_map = f"https://map.kakao.com/link/to/{best_hospital['name']},{best_hospital['lat']},{best_hospital['lng']}"
        st.markdown(f"""
        <div class="best-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <span style="background-color: #22C55E; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold;">실시간 최우선 권장</span>
                    <h3 style="margin: 6px 0 2px 0; color: #1E293B; font-size: 1.25rem;">{best_hospital['name']}</h3>
                    <span style="font-size: 0.85rem; color: #64748B;">📞 {best_hospital['phone']}</span>
                </div>
                <a href="{best_map}" target="_blank" style="background-color: #2563EB; color: white; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-size: 0.85rem; font-weight: bold;">길찾기</a>
            </div>
            <div class="info-grid">
                <div class="info-box"><div style="font-size:0.7rem; color:#64748B;">일반병상</div><div style="font-weight:bold; font-size:0.85rem; color:#1E293B;">잔여 {best_hospital['gen_curr']}석</div><div style="font-size:0.7rem; color:#059669; font-weight:bold;">{best_hospital['status']}</div></div>
                <div class="info-box"><div style="font-size:0.7rem; color:#64748B;">소아병상</div><div style="font-weight:bold; font-size:0.85rem; color:#1E293B;">잔여 {best_hospital['ped_curr']}석</div></div>
                <div class="info-box"><div style="font-size:0.7rem; color:#64748B;">분만실</div><div style="font-weight:bold; font-size:0.8rem; color:#1E293B; margin-top:2px;">{best_hospital['mat_status']}</div></div>
                <div class="info-box"><div style="font-size:0.7rem; color:#64748B;">음압격리</div><div style="font-weight:bold; font-size:0.85rem; color:#1E293B;">잔여 {best_hospital['iso_neg_curr']}석</div></div>
            </div>
            <div style="background-color: #FFFFFF; padding: 10px; border-radius: 6px; margin-top: 12px; font-size: 0.85rem; color: #334155; border: 1px solid #BBF7D0;">
                💡 <b>실시간 추천 사유:</b> 일반 응급실 잔여 병상({best_hospital['gen_curr']}석)이 가장 여유 있어 신속한 진료가 예상됩니다.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 나머지 병원 전체 목록
        for h in other_hospitals:
            h_map = f"https://map.kakao.com/link/to/{h['name']},{h['lat']},{h['lng']}"
            st.markdown(f"""
            <div class="hospital-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <h4 style="margin: 0 0 2px 0; color: #1E293B; font-size: 1.1rem;">{h['name']}</h4>
                        <span style="font-size: 0.85rem; color: #64748B;">📞 {h['phone']}</span>
                    </div>
                    <a href="{h_map}" target="_blank" style="background-color: #EFF6FF; color: #2563EB; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-size: 0.85rem; font-weight: bold;">길찾기</a>
                </div>
                <div class="info-grid">
                    <div class="info-box"><div style="font-size:0.7rem; color:#64748B;">일반병상</div><div style="font-weight:bold; font-size:0.85rem; color:#1E293B;">잔여 {h['gen_curr']}석</div></div>
                    <div class="info-box"><div style="font-size:0.7rem; color:#64748B;">소아병상</div><div style="font-weight:bold; font-size:0.85rem; color:#1E293B;">잔여 {h['ped_curr']}석</div></div>
                    <div class="info-box"><div style="font-size:0.7rem; color:#64748B;">분만실</div><div style="font-weight:bold; font-size:0.8rem; color:#1E293B; margin-top:2px;">{h['mat_status']}</div></div>
                    <div class="info-box"><div style="font-size:0.7rem; color:#64748B;">음압격리</div><div style="font-weight:bold; font-size:0.85rem; color:#1E293B;">잔여 {h['iso_neg_curr']}석</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("표출할 병원 데이터가 없습니다.")
