import streamlit as st
import requests
import xml.etree.ElementTree as ET

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
# 2. 실시간 응급실 API 연동 함수 (디버깅 포함)
# ----------------------------------------------------
API_KEY = "aa0cf3fc4d2a32edf9e6f8cf63cf46eaafb213b56f85d96e15b30484d0b75473"

@st.cache_data(ttl=30)
def fetch_realtime_emergency_data(stage1, stage2):
    url = "http://apis.data.go.kr/B552657/ErmctInfoInqireService/getEmrRltmSttusInfo"
    
    params = {
        'serviceKey': API_KEY,
        'STAGE1': stage1,
        'STAGE2': stage2 if stage2 != "전체" else "",
        'numOfRows': '20',
        'pageNo': '1'
    }
    
    try:
        # requests가 키를 이중 인코딩하지 않도록 안전하게 호출
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code != 200:
            return [], f"HTTP 에러 코드: {response.status_code}"
            
        root = ET.fromstring(response.content)
        
        # 공공데이터포털 에러 메시지 확인
        result_code = root.find(".//resultCode")
        result_msg = root.find(".//resultMsg")
        if result_code is not None and result_code.text != "00":
            return [], f"API 에러 [{result_code.text}]: {result_msg.text if result_msg is not None else '원인 불명'}"
            
        items = root.findall(".//item")
        if not items:
            return [], "검색된 응급실 데이터가 없습니다 (지역명 확인 필요)."
        
        hospital_list = []
        for item in items:
            def get_text(tag):
                node = item.find(tag)
                return node.text if node is not None and node.text else "-"
            
            h_data = {
                "name": get_text("dutyName"),
                "type": "응급의료기관",
                "gen_curr": int(get_text("hvec")) if get_text("hvec").isdigit() else 0,
                "ped_curr": int(get_text("hvicyn")) if get_text("hvicyn").isdigit() else 0,
                "mat_status": f"분만 가능 (잔여 {get_text('hpbd')}석)" if get_text('hpbd').isdigit() and int(get_text('hpbd')) > 0 else "미지원",
                "iso_neg_curr": int(get_text("hvcc")) if get_text("hvcc").isdigit() else 0,
                "phone": get_text("dutyTel1"),
                "lat": float(get_text("wgs84Lat")) if get_text("wgs84Lat").replace('.','',1).isdigit() else 33.3,
                "lng": float(get_text("wgs84Lon")) if get_text("wgs84Lon").replace('.','',1).isdigit() else 126.5
            }
            hospital_list.append(h_data)
            
        return hospital_list, None
        
    except Exception as e:
        return [], f"예외 발생: {str(e)}"

# ----------------------------------------------------
# 3. 사이드바: 지역 설정
# ----------------------------------------------------
st.sidebar.markdown("### 📍 실시간 지역 설정")
selected_state = st.sidebar.selectbox("시/도 선택", ["서울특별시", "부산광역시", "제주특별자치도", "경기도", "강원특별자치도"])

district_map = {
    "서울특별시": ["전체", "강동구", "강남구", "종로구", "중구", "송파구"],
    "부산광역시": ["전체", "서구", "부산진구", "해운대구"],
    "제주특별자치도": ["전체", "제주시", "서귀포시"],
    "경기도": ["전체", "수원시", "성남시", "고양시"],
    "강원특별자치도": ["전체", "춘천시", "원주시", "강릉시"]
}

selected_district = st.sidebar.selectbox("세부 지역(구/시) 선택", district_map.get(selected_state, ["전체"]))

# 실시간 데이터 호출
current_facilities, error_message = fetch_realtime_emergency_data(selected_state, selected_district)

# ----------------------------------------------------
# 4. 메인 화면 레이아웃 및 렌더링
# ----------------------------------------------------
location_title = f"{selected_state} {selected_district}" if selected_district != "전체" else f"{selected_state} 전체"
st.markdown(f"### 🚑 내 손안의 응급실 실시간 조회 ({location_title})")
st.caption("보건복지부 응급의료포털 실시간 병상 정보 연동 중")

# API 에러가 발생한 경우 화면에 원인 출력 (디버깅용)
if error_message:
    st.warning(f"⚠️ 실시간 API 연동 상태 안내: {error_message}\n\n(※ 방금 발급받은 인증키라면 10~30분 후 정상 작동하거나, 공공데이터포털 마이페이지에서 키 상태를 확인해 보세요.)")

# API 데이터가 없을 때만 임시 샘플 표시 (원래 원하셨던 다중 병원 구조 테스트용)
if not current_facilities:
    current_facilities = [
        {
            "name": f"{selected_state} 샘플 응급의료센터 A", "gen_curr": 5, "ped_curr": 2, 
            "mat_status": "분만 가능 (잔여 2석)", "iso_neg_curr": 1, "phone": "02-123-4567", "lat": 37.5, "lng": 127.0
        },
        {
            "name": f"{selected_state} 샘플 종합병원 B", "gen_curr": 3, "ped_curr": 1, 
            "mat_status": "미지원", "iso_neg_curr": 0, "phone": "02-987-6543", "lat": 37.51, "lng": 127.01
        }
    ]

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

    st.error(f"### 🚨 [{age}] 맞춤 초기 대응 가이드\n\n선택하신 증상에 따라 가까운 응급실의 병상 상태를 확인 후 신속히 이동하시기 바랍니다.")

with col_right:
    st.subheader(f"🏥 실시간 응급의료기관 현황 (총 {len(current_facilities)}건)")
    
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
            <div class="info-box"><div style="font-size:0.7rem; color:#64748B;">응급실일반</div><div style="font-weight:bold; font-size:0.85rem; color:#1E293B;">잔여 {best_hospital['gen_curr']}석</div></div>
            <div class="info-box"><div style="font-size:0.7rem; color:#64748B;">응급실소아</div><div style="font-weight:bold; font-size:0.85rem; color:#1E293B;">잔여 {best_hospital['ped_curr']}석</div></div>
            <div class="info-box"><div style="font-size:0.7rem; color:#64748B;">분만실</div><div style="font-weight:bold; font-size:0.8rem; color:#1E293B; margin-top:2px;">{best_hospital['mat_status']}</div></div>
            <div class="info-box"><div style="font-size:0.7rem; color:#64748B;">음압격리</div><div style="font-weight:bold; font-size:0.85rem; color:#1E293B;">잔여 {best_hospital['iso_neg_curr']}석</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 기타 병원 목록
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
                <div class="info-box"><div style="font-size:0.7rem; color:#64748B;">일반잔여</div><div style="font-weight:bold; font-size:0.85rem; color:#1E293B;">{h['gen_curr']}석</div></div>
                <div class="info-box"><div style="font-size:0.7rem; color:#64748B;">소아잔여</div><div style="font-weight:bold; font-size:0.85rem; color:#1E293B;">{h['ped_curr']}석</div></div>
                <div class="info-box"><div style="font-size:0.7rem; color:#64748B;">분만실</div><div style="font-weight:bold; font-size:0.8rem; color:#1E293B; margin-top:2px;">{h['mat_status']}</div></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
