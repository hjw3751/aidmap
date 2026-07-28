import streamlit as st
import requests
import xml.etree.ElementTree as ET

# ----------------------------------------------------
# 1. 페이지 설정 및 UI 스타일링
# ----------------------------------------------------
st.set_page_config(page_title="내 손안의 응급실 (실시간 연동)", page_icon="🚑", layout="wide")

st.markdown("""
<style>
    * { word-break: keep-all !important; }
    .badge-smooth { background-color: #DCFCE7; color: #166534; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; }
    .badge-normal { background-color: #FEF9C3; color: #854D0E; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; }
    .badge-busy { background-color: #FEE2E2; color: #991B1B; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 2. 대한민국 전 지역 (17개 시/도 및 모든 구/군/시) 데이터 정의
# ----------------------------------------------------
KOREA_REGIONS = {
    "서울특별시": ["전체", "강남구", "강동구", "강북구", "강서구", "관악구", "광진구", "구로구", "금천구", "노원구", "도봉구", "동대문구", "동작구", "마포구", "서대문구", "서초구", "성동구", "성북구", "송파구", "양천구", "영등포구", "용산구", "은평구", "종로구", "중구", "중랑구"],
    "부산광역시": ["전체", "강서구", "금정구", "기장군", "남구", "동구", "동래구", "부산진구", "북구", "사상구", "사하구", "서구", "수영구", "연제구", "영도구", "중구", "해운대구"],
    "대구광역시": ["전체", "남구", "달서구", "달성군", "동구", "북구", "서구", "수성구", "중구", "군위군"],
    "인천광역시": ["전체", "강화군", "계양구", "남동구", "동구", "미추홀구", "부평구", "서구", "연수구", "옹진군", "중구"],
    "광주광역시": ["전체", "광산구", "남구", "동구", "북구", "서구"],
    "대전광역시": ["전체", "대덕구", "동구", "서구", "유성구", "중구"],
    "울산광역시": ["전체", "남구", "동구", "북구", "울주군", "중구"],
    "세종특별자치시": ["전체", "세종시"],
    "경기도": ["전체", "가평군", "고양시 덕양구", "고양시 일산동구", "고양시 일산서구", "과천시", "광명시", "광주시", "구리시", "군포시", "김포시", "남양주시", "동두천시", "부천시", "성남시 분당구", "성남시 수정구", "성남시 중원구", "수원시 권선구", "수원시 영통구", "수원시 장안구", "수원시 팔달구", "시흥시", "안산시 단원구", "안산시 상록구", "안성시", "안양시 동안구", "안양시 만안구", "양주시", "양평군", "여주시", "연천군", "오산시", "용인시 기흥구", "용인시 수지구", "용인시 처인구", "의왕시", "의정부시", "이천시", "파주시", "평택시", "포천시", "하남시", "화성시"],
    "강원특별자치도": ["전체", "강릉시", "고성군", "동해시", "삼척시", "속초시", "양구군", "양양군", "영월군", "원주시", "인제군", "정선군", "철원군", "춘천시", "태백시", "평창군", "홍천군", "화천군", "횡성군"],
    "충청북도": ["전체", "괴산군", "단양군", "보은군", "영동군", "옥천군", "음성군", "제천시", "증평군", "진천군", "청주시 상당구", "청주시 서원구", "청주시 청원구", "청주시 흥덕구", "충주시"],
    "충청남도": ["전체", "계룡시", "공주시", "금산군", "논산시", "당진시", "보령시", "부여군", "서산시", "서천시", "아산시", "예산군", "천안시 동남구", "천안시 서북구", "청양군", "태안군", "홍성군"],
    "전북특별자치도": ["전체", "고창군", "군산시", "김제시", "남원시", "무주군", "부안군", "순창군", "완주군", "익산시", "임실군", "장수군", "전주시 덕진구", "전주시 완산구", "정읍시", "진안군"],
    "전라남도": ["전체", "강진군", "고흥군", "곡성군", "광양시", "구례군", "나주시", "담양군", "목포시", "무안군", "보성군", "순천시", "신안군", "여수시", "영광군", "영암군", "완도군", "장성군", "장흥군", "진도군", "함평군", "해남군", "화순군"],
    "경상북도": ["전체", "경산시", "경주시", "고령군", "구미시", "김천시", "문경시", "봉화군", "상주시", "성주군", "안동시", "영덕군", "영양군", "영주시", "영천시", "예천군", "울릉군", "울진군", "의성군", "청도군", "청송군", "칠곡군", "포항시 남구", "포항시 북구"],
    "경상남도": ["전체", "거제시", "거창군", "고성군", "김해시", "남해군", "밀양시", "사천시", "산청군", "양산시", "의령군", "진주시", "창녕군", "창원시 마산합포구", "창원시 마산회원구", "창원시 성산구", "창원시 의창구", "창원시 진해구", "통영시", "하동군", "함안군", "함양군", "합천군"],
    "제주특별자치도": ["전체", "서귀포시", "제주시"]
}

# ----------------------------------------------------
# 3. 공공데이터 API 연동 함수 (params 방식 적용)
# ----------------------------------------------------
API_KEY = "aa0cf3fc4d2a32edf9e6f8cf63cf46eaafb213b56f85d96e15b30484d0b75473"

@st.cache_data(ttl=60)
def fetch_emergency_data(stage1, stage2):
    url = "http://apis.data.go.kr/B552657/ErmctInfoInqireService/getEmrRltmSttusInfo"
    
    # params 딕셔너리를 사용하여 404 및 인코딩 오류 원천 차단
    params = {
        'serviceKey': API_KEY,
        'STAGE1': stage1,
        'numOfRows': '200',
        'pageNo': '1'
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code != 200:
            return [], f"HTTP 연결 에러 (상태코드: {response.status_code})"
            
        root = ET.fromstring(response.content)
        
        result_code = root.find(".//resultCode")
        result_msg = root.find(".//resultMsg")
        if result_code is not None and result_code.text != "00":
            msg = result_msg.text if result_msg is not None else "사유 불명"
            return [], f"공공데이터 서버 거부 [코드 {result_code.text}]: {msg}"
            
        items = root.findall(".//item")
        if not items:
            return [], "해당 지역에 등록된 응급실 데이터가 없습니다."
        
        hospital_list = []
        for item in items:
            def get_val(tag):
                node = item.find(tag)
                return node.text if node is not None and node.text else "0"
            
            duty_addr = get_val("dutyAddr")
            
            if stage2 != "전체":
                short_stage2 = stage2.split()[-1]
                if short_stage2 not in duty_addr:
                    continue
            
            gen_curr = int(get_val("hvec")) if get_val("hvec").isdigit() else 0
            ped_curr = int(get_val("hvicyn")) if get_val("hvicyn").isdigit() else 0
            mat_cnt = get_val("hpbd")
            iso_neg = int(get_val("hvcc")) if get_val("hvcc").isdigit() else 0
            iso_gen = int(get_val("hvncc")) if get_val("hvncc").isdigit() else 0
            cohort = get_val("hvgc") if get_val("hvgc").isdigit() else "-"
            
            def get_badge(val):
                if val > 5: return "원활", "badge-smooth"
                elif val > 2: return "보통", "badge-normal"
                else: return "혼잡", "badge-busy"
                
            status_text, status_class = get_badge(gen_curr)
            
            lat = float(get_val("wgs84Lat")) if get_val("wgs84Lat").replace('.','',1).isdigit() else 37.5665
            lng = float(get_val("wgs84Lon")) if get_val("wgs84Lon").replace('.','',1).isdigit() else 126.9780
            
            hospital_list.append({
                "name": get_val("dutyName"),
                "phone": get_val("dutyTel1"),
                "addr": duty_addr,
                "gen_curr": gen_curr,
                "gen_status": status_text, "gen_class": status_class,
                "ped_curr": ped_curr,
                "mat_status": f"가능/{mat_cnt}" if mat_cnt.isdigit() and int(mat_cnt) > 0 else "미지원",
                "iso_neg": iso_neg,
                "iso_gen": iso_gen,
                "cohort": cohort,
                "lat": lat, "lng": lng
            })
            
        return hospital_list, None
    except Exception as e:
        return [], f"시스템 예외 발생: {str(e)}"

# ----------------------------------------------------
# 4. 화면 UI 구성
# ----------------------------------------------------
st.markdown("### 🚑 응급실 가용 병상 실시간 조회")

tab_choice = st.radio("조회 방식", ["시/도 및 구/군/시 선택", "반경조건 설정"], horizontal=True, label_visibility="collapsed")

col_1, col_2, col_3 = st.columns([1.5, 1.5, 1.0])

selected_state = "서울특별시"
selected_district = "전체"

if tab_choice == "시/도 및 구/군/시 선택":
    with col_1:
        selected_state = st.selectbox("시/도 선택", list(KOREA_REGIONS.keys()), label_visibility="collapsed")
    with col_2:
        district_list = KOREA_REGIONS.get(selected_state, ["전체"])
        selected_district = st.selectbox("구/군/시 선택", district_list, label_visibility="collapsed")
else:
    with col_1:
        selected_state = st.selectbox("기준 시/도", list(KOREA_REGIONS.keys()), label_visibility="collapsed")
    with col_2:
        radius_km = st.selectbox("반경 설정", [5, 10, 20, 30], index=1, label_visibility="collapsed")
    with col_3:
        st.button("📍 현재위치", use_container_width=True)

st.divider()

hospitals, err_msg = fetch_emergency_data(selected_state, selected_district)

if err_msg:
    st.error(f"🚨 **API 연동 안내**\n\n{err_msg}")
else:
    st.markdown(f"**[{selected_state} {selected_district}] 응급실 가용 병상 조회 (총 {len(hospitals)}건)**")
    
    header_cols = st.columns([2.2, 1.2, 1.2, 1.2, 1.2, 1.2, 1.0])
    with header_cols[0]: st.markdown("**기관 명 및 주소**")
    with header_cols[1]: st.markdown("**응급실일반**")
    with header_cols[2]: st.markdown("**응급실소아**")
    with header_cols[3]: st.markdown("**분만실**")
    with header_cols[4]: st.markdown("**음압격리**")
    with header_cols[5]: st.markdown("**일반격리**")
    with header_cols[6]: st.markdown("**코호트**")
    
    st.markdown("<hr style='margin:4px 0 12px 0;'>", unsafe_allow_html=True)

    for h in hospitals:
        map_link = f"https://map.kakao.com/link/to/{h['name']},{h['lat']},{h['lng']}"
        row_cols = st.columns([2.2, 1.2, 1.2, 1.2, 1.2, 1.2, 1.0])
        
        with row_cols[0]:
            st.markdown(f"""
                <div style="font-weight:bold; font-size:0.95rem; color:#1E293B;">{h['name']}</div>
                <div style="font-size:0.75rem; color:#64748B; margin:2px 0;">{h['addr']}</div>
                <div>
                    <a href="{map_link}" target="_blank" style="background:#EF4444; color:white; padding:2px 8px; border-radius:4px; font-size:0.75rem; text-decoration:none; font-weight:bold;">길찾기</a>
                    <span style="font-size:0.75rem; color:#2563EB; margin-left:6px;">📞 {h['phone']}</span>
                </div>
            """, unsafe_allow_html=True)
            
        with row_cols[1]:
            st.markdown(f"""
                <div style="text-align:center;">
                    <span class="{h['gen_class']}">{h['gen_status']}</span>
                    <div style="font-size:0.85rem; margin-top:2px; font-weight:bold;">{h['gen_curr']}/20</div>
                </div>
            """, unsafe_allow_html=True)
            
        with row_cols[2]:
            st.markdown(f"""
                <div style="text-align:center; font-size:0.85rem; font-weight:bold; padding-top:4px;">
                    {h['ped_curr']}/3
                </div>
            """, unsafe_allow_html=True)
            
        with row_cols[3]:
            st.markdown(f"""
                <div style="text-align:center; font-size:0.8rem; padding-top:4px; color:#059669; font-weight:bold;">
                    {h['mat_status']}
                </div>
            """, unsafe_allow_html=True)
            
        with row_cols[4]:
            st.markdown(f"""
                <div style="text-align:center; font-size:0.85rem; font-weight:bold; padding-top:4px;">
                    {h['iso_neg']}/1
                </div>
            """, unsafe_allow_html=True)
            
        with row_cols[5]:
            st.markdown(f"""
                <div style="text-align:center; font-size:0.85rem; font-weight:bold; padding-top:4px;">
                    {h['iso_gen']}/2
                </div>
            """, unsafe_allow_html=True)
            
        with row_cols[6]:
            st.markdown(f"""
                <div style="text-align:center; font-size:0.85rem; color:#64748B; padding-top:4px;">
                    {h['cohort']}
                </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<hr style='margin:8px 0; border:0; border-top:1px solid #F1F5F9;'>", unsafe_allow_html=True)
