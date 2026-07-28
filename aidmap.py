import streamlit as st
import requests
import xml.etree.ElementTree as ET
import math

# ----------------------------------------------------
# 1. 페이지 설정 및 UI 스타일링
# ----------------------------------------------------
st.set_page_config(page_title="내 손안의 응급실 (실시간 연동)", page_icon="🚑", layout="wide")

st.markdown("""
<style>
    * { word-break: keep-all !important; }
    .hospital-row {
        background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px;
        padding: 16px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .badge-smooth { background-color: #DCFCE7; color: #166534; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; }
    .badge-normal { background-color: #FEF9C3; color: #854D0E; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; }
    .badge-busy { background-color: #FEE2E2; color: #991B1B; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 2. 공공데이터 API 연동 함수
# ----------------------------------------------------
API_KEY = "aa0cf3fc4d2a32edf9e6f8cf63cf46eaafb213b56f85d96e15b30484d0b75473"

@st.cache_data(ttl=60)
def fetch_emergency_data(stage1):
    url = "http://apis.data.go.kr/B552657/ErmctInfoInqireService/getEmrRltmSttusInfo"
    query_url = f"{url}?serviceKey={API_KEY}&STAGE1={stage1}&numOfRows=100&pageNo=1"
    
    try:
        response = requests.get(query_url, timeout=5)
        if response.status_code != 200:
            return [], f"HTTP 에러: {response.status_code}"
            
        root = ET.fromstring(response.content)
        result_code = root.find(".//resultCode")
        if result_code is not None and result_code.text != "00":
            return [], f"API 에러 코드: {result_code.text}"
            
        items = root.findall(".//item")
        if not items:
            return [], "해당 지역에 등록된 응급실 데이터가 없습니다."
        
        hospital_list = []
        for item in items:
            def get_val(tag):
                node = item.find(tag)
                return node.text if node is not None and node.text else "0"
            
            # 6가지 세부 지표 매핑
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
            
            # 가상 좌표 (거리 계산용)
            lat = float(get_val("wgs84Lat")) if get_val("wgs84Lat").replace('.','',1).isdigit() else 37.5665
            lng = float(get_val("wgs84Lon")) if get_val("wgs84Lon").replace('.','',1).isdigit() else 126.9780
            
            hospital_list.append({
                "name": get_val("dutyName"),
                "phone": get_val("dutyTel1"),
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
        return [], f"예외 발생: {str(e)}"

# ----------------------------------------------------
# 3. 상단 탭 구현 (시/도 선택 vs 반경조건 설정)
# ----------------------------------------------------
st.markdown("### 🚑 응급실 가용 병상 실시간 조회")

tab_choice = st.radio("조회 방식 선택", ["시/도 선택", "반경조건 설정"], horizontal=True, label_visibility="collapsed")

col_s1, col_s2, col_s3 = st.columns([1.5, 1.5, 1.0])

selected_state = "서울특별시"
radius_km = 10

if tab_choice == "시/도 선택":
    with col_s1:
        selected_state = st.selectbox(
            "시/도 선택", 
            ["서울특별시", "부산광역시", "대구광역시", "인천광역시", "광주광역시", "대전광역시", "울산광역시", "세종특별자치시", "경기도", "강원특별자치도", "충청북도", "충청남도", "전라북도", "전라남도", "경상북도", "경상남도", "제주특별자치도"],
            label_visibility="collapsed"
        )
else:
    with col_s1:
        selected_state = st.selectbox("기준 지역", ["서울특별시", "부산광역시", "대구광역시", "인천광역시", "경기도"], label_visibility="collapsed")
    with col_s2:
        radius_km = st.selectbox("반경 설정", [5, 10, 20, 30], index=1, label_visibility="collapsed")
    with col_s3:
        st.button("📍 현재위치", use_container_width=True)

st.divider()

# 데이터 호출
hospitals, err_msg = fetch_emergency_data(selected_state)

if err_msg:
    st.error(f"🚨 데이터 연동 에러: {err_msg}")
else:
    st.markdown(f"**응급실 가용 병상 조회 ({len(hospitals)}건)**")
    
    # 테이블 헤더 스타일
    header_cols = st.columns([2.2, 1.2, 1.2, 1.2, 1.2, 1.2, 1.0])
    with header_cols[0]: st.markdown("**기관 명**")
    with header_cols[1]: st.markdown("**응급실일반**")
    with header_cols[2]: st.markdown("**응급실소아**")
    with header_cols[3]: st.markdown("**분만실**")
    with header_cols[4]: st.markdown("**음압격리**")
    with header_cols[5]: st.markdown("**일반격리**")
    with header_cols[6]: st.markdown("**코호트**")
    
    st.markdown("<hr style='margin:4px 0 12px 0;'>", unsafe_allow_html=True)

    # 병원 리스트 렌더링
    for h in hospitals:
        map_link = f"https://map.kakao.com/link/to/{h['name']},{h['lat']},{h['lng']}"
        
        row_cols = st.columns([2.2, 1.2, 1.2, 1.2, 1.2, 1.2, 1.0])
        
        with row_cols[0]:
            st.markdown(f"""
                <div style="font-weight:bold; font-size:0.95rem; color:#1E293B;">{h['name']}</div>
                <div style="margin-top:4px;">
                    <a href="{map_link}" target="_blank" style="background:#EF4444; color:white; padding:2px 8px; border-radius:4px; font-size:0.75rem; text-decoration:none; font-weight:bold;">길찾기</a>
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
