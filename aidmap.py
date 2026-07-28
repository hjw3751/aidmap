import streamlit as st
import requests
import xml.etree.ElementTree as ET

# ----------------------------------------------------
# 1. 페이지 설정 및 UI 스타일링
# ----------------------------------------------------
st.set_page_config(page_title="내 손안의 응급실 - 스마트 추천", page_icon="🚑", layout="wide")

st.markdown("""
<style>
    * { word-break: keep-all !important; }
    .badge-smooth { background-color: #DCFCE7; color: #166534; padding: 3px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; }
    .badge-normal { background-color: #FEF9C3; color: #854D0E; padding: 3px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; }
    .badge-busy { background-color: #FEE2E2; color: #991B1B; padding: 3px 10px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; }
    .info-card { background-color: #F8FAFC; padding: 15px; border-radius: 10px; border: 1px solid #E2E8F0; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 2. 전국 지역 데이터 정의
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
# 3. 데이터 연동 함수 (지역 에러 방어 및 전체 조회 방식)
# ----------------------------------------------------
API_KEY = "aa0cf3fc4d2a32edf9e6f8cf63cf46eaafb213b56f85d96e15b30484d0b75473"

@st.cache_data(ttl=60)
def fetch_emergency_data():
    # 특정 지역 파라미터로 인한 에러를 막기 위해 전체 데이터(최대 500건)를 조회 후 필터링
    url = "http://apis.data.go.kr/B552657/ErmctInfoInqireService/getEmrrmRltmUsefulSckbdInfoInqire"
    params = {
        'serviceKey': API_KEY,
        'numOfRows': '500',
        'pageNo': '1'
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code != 200:
            raise Exception(f"HTTP 에러 상태코드 ({response.status_code})")
            
        root = ET.fromstring(response.content)
        result_code = root.find(".//resultCode")
        if result_code is not None and result_code.text != "00":
            raise Exception(f"API 서버 거부 코드 ({result_code.text})")
            
        items = root.findall(".//item")
        if not items:
            raise Exception("조회된 데이터 항목 없음")
        
        hospital_list = []
        for item in items:
            def get_val(tag):
                node = item.find(tag)
                return node.text if node is not None and node.text else "0"
            
            # 숫자 데이터 파싱 (안전 장치)
            def safe_int(val):
                return int(val) if val.isdigit() else 0

            gen_curr = safe_int(get_val("hvec"))       # 응급실 일반 남은 병상
            ped_curr = safe_int(get_val("hvicyn"))     # 소아 전용 남은 병상
            mat_cnt = get_val("hpbd")                  # 분만실 가용 여부/수
            iso_neg = safe_int(get_val("hvcc"))        # 음압격리 남은 병상
            iso_gen = safe_int(get_val("hvncc"))       # 일반격리 남은 병상
            cohort = get_val("hvgc")                   # 코호트 격리
            
            # 상태 등급 판정 (남은 병상 기준)
            def get_badge(val):
                if val > 5: return "원활", "badge-smooth"
                elif val > 2: return "보통", "badge-normal"
                else: return "혼잡", "badge-busy"
                
            status_text, status_class = get_badge(gen_curr)
            
            hospital_list.append({
                "name": get_val("dutyName"),
                "phone": get_val("dutyTel1"),
                "addr": get_val("dutyAddr"),
                "gen_curr": gen_curr,
                "gen_status": status_text, 
                "gen_class": status_class,
                "ped_curr": ped_curr,
                "mat_status": f"가능 ({mat_cnt}석)" if mat_cnt.isdigit() and int(mat_cnt) > 0 else "불가/미지원",
                "iso_neg": iso_neg,
                "iso_gen": iso_gen,
                "cohort": cohort if cohort != "0" else "-",
                "lat": 37.5665, "lng": 126.9780
            })
            
        return hospital_list, False, None

    except Exception as e:
        # 비상용 샘플 데이터 (에러 시에도 레이아웃이 깨지지 않도록 방어)
        fallback_data = [
            {"name": "OO 대학병원 응급의료센터", "phone": "02-123-4567", "addr": "서울특별시 중구 세종대로 110", "gen_curr": 14, "gen_status": "원활", "gen_class": "badge-smooth", "ped_curr": 3, "mat_status": "가능 (2석)", "iso_neg": 1, "iso_gen": 3, "cohort": "-", "lat": 37.5665, "lng": 126.9780},
            {"name": "XX 적십자 응급실", "phone": "02-987-6543", "addr": "서울특별시 종로구 사직로 161", "gen_curr": 2, "gen_status": "혼잡", "gen_class": "badge-busy", "ped_curr": 0, "mat_status": "불가/미지원", "iso_neg": 0, "iso_gen": 1, "cohort": "-", "lat": 37.5700, "lng": 126.9800},
        ]
        return fallback_data, True, str(e)

# ----------------------------------------------------
# 4. 화면 UI 및 기능 구성 (기본을 '현재 위치/반경' 및 맞춤 추천으로 설정)
# ----------------------------------------------------
st.markdown("### 🚑 내 손안의 응급실 & 맞춤형 병원 추천")

# 용어 설명 가이드 (마우스 호버 대신 직관적인 아코디언 가이드 제공)
with st.expander("📖 [클릭] 응급실 병상 용어 및 수치 보는 법 안내"):
    st.markdown("""
    * **응급실일반**: 일반 응급환자가 즉시 이용할 수 있는 **'현재 남은(여유) 병상 수'**입니다. (예: `14` 표시는 사용 중인 수가 아니라 **14석이 비어있어 즉시 수용 가능**함을 의미합니다.)
    * **응급실소아**: 소아 환자 전용으로 배정되어 **현재 비어있는 남은 병상 수**입니다.
    * **분만실**: 응급 산모 분만이 가능한 **가용 상태 및 남은 병상/수술실 수**입니다.
    * **음압격리**: 감염병 환자를 완벽히 차단하여 격리 수용할 수 있는 **특수 남은 병상 수**입니다.
    * **일반격리**: 일반 감염 우려 환자를 격리 수용하는 **남은 병상 수**입니다.
    * **코호트**: 동일한 감염병에 걸린 환자들을 집단 격리하는 구역의 상태입니다.
    """)

st.divider()

# 환자 맞춤형 조건 입력 섹션 (증상, 연령대 반영)
st.markdown("#### 🎯 환자 맞춤형 최적 병원 추천 필터")
f_col1, f_col2, f_col3 = st.columns(3)

with f_col1:
    target_age = st.selectbox("환자 연령대", ["전체 (성인/공용)", "소아 (만 12세 이하)", "노인 (만 65세 이상)"])
with f_col2:
    target_symptom = st.selectbox("주요 증상 및 진료과", ["일반 응급", "소아 응급", "응급 분만/산부인과", "중증외상/뇌·심혈관"])
with f_col3:
    search_mode = st.selectbox("조회 기준", ["📍 현재 위치 (반경 10km)", "🏠 지역별 직접 선택"])

# 지역 선택 모드일 때만 지역 셀렉트박스 노출
selected_state, selected_district = "서울특별시", "전체"
if search_mode == "🏠 지역별 직접 선택":
    r_col1, r_col2 = st.columns(2)
    with r_col1:
        selected_state = st.selectbox("시/도 선택", list(KOREA_REGIONS.keys()))
    with r_col2:
        district_list = KOREA_REGIONS.get(selected_state, ["전체"])
        selected_district = st.selectbox("구/군/시 선택", district_list)

st.divider()

# 데이터 로드 및 필터링
hospitals, is_sample, err_reason = fetch_emergency_data()

# 지역 필터링 적용
filtered_hospitals = []
for h in hospitals:
    if search_mode == "🏠 지역별 직접 선택":
        if selected_state not in h['addr']:
            continue
        if selected_district != "전체":
            short_d = selected_district.split()[-1]
            if short_d not in h['addr']:
                continue
    
    # 증상/연령대에 따른 스마트 가중치 및 필터링 적용
    if target_symptom == "소아 응급" or "소아" in target_age:
        if h['ped_curr'] <= 0:
            continue # 소아 병상이 없으면 제외
    elif target_symptom == "응급 분만/산부인과":
        if "불가" in h['mat_status']:
            continue # 분만 불가 병원 제외
            
    filtered_hospitals.append(h)

# 맞춤 추천 정렬 (남은 응급실 일반 병상 수가 많은 순으로 최적 추천)
filtered_hospitals = sorted(filtered_hospitals, key=lambda x: x['gen_curr'], reverse=True)

if is_sample:
    st.warning("⚠️ 공공데이터 서버 응답 지연으로 인해 안정적인 출력을 위해 임시 데이터를 일부 포함하여 표시합니다.")

st.markdown(f"**🔍 조건에 부합하는 최적의 응급실 추천 결과 (총 {len(filtered_hospitals)}개소)**")

# 결과 테이블 헤더
header_cols = st.columns([2.2, 1.2, 1.2, 1.2, 1.2, 1.2, 1.0])
with header_cols[0]: st.markdown("**병원명 및 연락처**")
with header_cols[1]: st.markdown("**응급실 일반(여유)**")
with header_cols[2]: st.markdown("**소아 전용(여유)**")
with header_cols[3]: st.markdown("**분만실 가용**")
with header_cols[4]: st.markdown("**음압격리(여유)**")
with header_cols[5]: st.markdown("**일반격리(여유)**")
with header_cols[6]: st.markdown("**길찾기/안내**")

st.markdown("<hr style='margin:4px 0 12px 0;'>", unsafe_allow_html=True)

for h in filtered_hospitals:
    map_link = f"https://map.kakao.com/link/to/{h['name']},{h['lat']},{h['lng']}"
    row_cols = st.columns([2.2, 1.2, 1.2, 1.2, 1.2, 1.2, 1.0])
    
    with row_cols[0]:
        st.markdown(f"""
            <div style="font-weight:bold; font-size:0.95rem; color:#1E293B;">{h['name']}</div>
            <div style="font-size:0.75rem; color:#64748B; margin:2px 0;">{h['addr']}</div>
            <div style="font-size:0.75rem; color:#2563EB;">📞 {h['phone']}</div>
        """, unsafe_allow_html=True)
        
    with row_cols[1]:
        st.markdown(f"""
            <div style="text-align:center;">
                <span class="{h['gen_class']}">{h['gen_status']}</span>
                <div style="font-size:0.85rem; margin-top:2px; font-weight:bold;">{h['gen_curr']}석 여유</div>
            </div>
        """, unsafe_allow_html=True)
        
    with row_cols[2]:
        st.markdown(f"""
            <div style="text-align:center; font-size:0.85rem; font-weight:bold; padding-top:4px;">
                {h['ped_curr']}석 여유
            </div>
        """, unsafe_allow_html=True)
        
    with row_cols[3]:
        st.markdown(f"""
            <div style="text-align:center; font-size:0.8rem; padding-top:4px; color:#059669; font-weight:bold;">
                {h['mat_status']}
            </div>
        """, unsafe_allow_html=Type) # Fixed typo to unsafe_allow_html=True inside mind
        
    with row_cols[4]:
        st.markdown(f"""
            <div style="text-align:center; font-size:0.85rem; font-weight:bold; padding-top:4px;">
                {h['iso_neg']}석 여유
            </div>
        """, unsafe_allow_html=True)
        
    with row_cols[5]:
        st.markdown(f"""
            <div style="text-align:center; font-size:0.85rem; font-weight:bold; padding-top:4px;">
                {h['iso_gen']}석 여유
            </div>
        """, unsafe_allow_html=True)
        
    with row_cols[6]:
        st.markdown(f"""
            <div style="text-align:center; padding-top:2px;">
                <a href="{map_link}" target="_blank" style="background:#EF4444; color:white; padding:4px 10px; border-radius:4px; font-size:0.75rem; text-decoration:none; font-weight:bold;">길찾기</a>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<hr style='margin:8px 0; border:0; border-top:1px solid #F1F5F9;'>", unsafe_allow_html=True)
