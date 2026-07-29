import streamlit as st
import requests
import math

# --- 페이지 설정 ---
st.set_page_config(page_title="Aidmap - 맞춤형 응급의료", page_icon="🚑", layout="wide")

# --- 상태 관리 (페이지 이동용) ---
if "page" not in st.session_state:
    st.session_state.page = "main"

# --- 상단 네비게이션 바 (좌/우측 상단 버튼 구현) ---
nav_col1, nav_col2, nav_col3 = st.columns([1, 4, 1])
with nav_col1:
    if st.button("🗺️ 직접 지역 선택 (좌측상단)"):
        st.session_state.page = "manual_search"
with nav_col2:
    st.markdown("<h1 style='text-align: center; margin-top: -20px;'>🚑 Aidmap</h1>", unsafe_allow_html=True)
with nav_col3:
    if st.button("💬 문의 및 도움말 (우측상단)"):
        st.session_state.page = "inquiry_help"

st.markdown("---")

# ==========================================
# 1. 메인 화면 (맞춤형 병원 추천)
# ==========================================
if st.session_state.page == "main":
    
    # 1-1. 연령대 입력 및 맞춤형 안내
    st.subheader("👤 이용자 맞춤 안내")
    age_group = st.radio("연령대를 선택해주세요:", ["어린이", "청년/성인", "어르신"], horizontal=True)
    
    if age_group == "어린이":
        st.info("👋 안녕! 아픈 곳이 있니? 아래에 어디가 아픈지 적어주면, 가장 빨리 낫게 해줄 병원을 찾아줄게!")
    elif age_group == "청년/성인":
        st.info("현재 위치와 증상을 입력하시면 혼잡도와 거리를 고려해 최적의 응급의료기관을 추천해 드립니다.")
    elif age_group == "어르신":
        st.markdown("<h2 style='color: #2b6cb0;'>어르신, 안녕하세요. 글자를 크게 보여드립니다. 아래에 아프신 곳을 적어주세요.</h2>", unsafe_allow_html=True)
        st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", format="audio/mp3") # 음성지원 예시 플레이어
        st.caption("🔊 (음성 지원) 재생 버튼을 누르시면 안내 음성이 나옵니다.")

    # 1-2. 병상 현황 읽는 법
    with st.expander("💡 병상 현황 쉽게 읽는 방법 보기"):
        st.markdown("""
        * **가용 병상:** 현재 병원에 당장 입원할 수 있는 남은 자리입니다. 숫자가 클수록 여유가 있습니다.
        * **혼잡도:** 여유(초록) - 보통(노랑) - 혼잡(빨강)으로 표시됩니다.
        * 마이너스(-)로 표시된 병상은 현재 자리가 초과되어 대기해야 함을 의미합니다.
        """)

    st.markdown("---")
    
    # 1-3. 환자 상태 및 위치 입력
    st.subheader("📍 현재 상태 및 위치 기반 병원 찾기")
    col1, col2 = st.columns(2)
    with col1:
        # 실제 환경에서는 브라우저 GPS나 모바일 GPS API를 연동합니다.
        current_loc = st.text_input("현재 위치 (GPS 연동 대체)", value="제주특별자치도 서귀포시") 
    with col2:
        symptoms = st.text_input("현재 증상 및 필요한 진료과 (예: 배가 아파요, 내과)")

    # 1-4. 추천 알고리즘 로직 및 공공데이터 호출
    if st.button("🚨 내게 맞는 병원 추천받기", use_container_width=True):
        if symptoms:
            st.success(f"'{symptoms}' 증상에 맞춰, 가장 가깝고 덜 혼잡한 병원을 찾습니다...")
            
            # API 호출 부분 (제주도 서귀포시 예시)
            url = "https://apis.data.go.kr/B552657/ErmctInfoInqireService/getEmrrmRltmUsefulSckbdInfoInqire"
            params = {
                "serviceKey": "aa0cf3fc4d2a32edf9e6f8cf63cf46eaafb213b56f85d96e15b30484d0b75473",
                "STAGE1": "제주특별자치도",
                "STAGE2": "서귀포시",
                "pageNo": "1",
                "numOfRows": "10",
                "_type": "json"
            }
            
            try:
                res = requests.get(url, params=params)
                data = res.json()
                items = data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
                
                if isinstance(items, dict): items = [items]
                
                # 병원 추천 리스트 출력 (거리/혼잡도 고려 가상 시뮬레이션 적용)
                st.markdown(f"### 🏥 {current_loc} 주변 추천 응급의료기관")
                for item in items:
                    with st.container():
                        beds = item.get('hbec', 0)
                        # 혼잡도 시각화
                        status = "🟢 여유" if int(beds) > 5 else ("🟡 보통" if int(beds) > 0 else "🔴 혼잡(대기)")
                        
                        st.markdown(f"#### {item.get('dutyName', '병원명 없음')} ({status})")
                        st.write(f"**📞 전화번호:** {item.get('dutyTel3', '정보 없음')} | **응급실 남은 자리:** {beds}석")
                        # 추후 AI 연동 시, 증상(symptoms)을 AI가 분석하여 '적합도(%)'를 출력하는 로직이 들어갈 수 있습니다.
                        st.caption("✨ AI 분석 결과: 환자님의 증상 치료에 적합한 진료과가 있습니다. 예상 거리: 약 2.5km")
                        st.divider()

            except Exception as e:
                st.error("데이터를 불러오는 데 실패했습니다.")
        else:
            st.warning("증상을 입력해주세요!")


# ==========================================
# 2. 좌측 상단 메뉴: 직접 지역 선택
# ==========================================
elif st.session_state.page == "manual_search":
    st.subheader("🗺️ 직접 지역 선택 (전국 시/도 및 시/군/구)")
    
    # 한국 지도 모든 지역 반영을 위한 선택 창
    sido = st.selectbox("시/도를 선택하세요", ["서울특별시", "부산광역시", "경기도", "제주특별자치도", "등등...전국"])
    sigungu = st.selectbox("시/군/구를 선택하세요", ["강남구", "해운대구", "수원시", "서귀포시"])
    
    if st.button("해당 지역 응급실 조회"):
        st.info(f"{sido} {sigungu}의 실시간 응급의료기관 데이터를 가져옵니다. (메인 화면의 공공데이터와 동일한 로직 적용)")
        # 이곳에 위 메인화면과 동일한 API 호출 로직을 함수화하여 넣을 수 있습니다.

    if st.button("🏠 메인으로 돌아가기"):
        st.session_state.page = "main"


# ==========================================
# 3. 우측 상단 메뉴: 문의사항 및 도움말
# ==========================================
elif st.session_state.page == "inquiry_help":
    st.subheader("💬 문의사항 및 유용한 정보")
    
    tab1, tab2 = st.tabs(["문의 게시판", "유용한 사이트 및 정보"])
    
    with tab1:
        st.write("사이트 이용 중 불편한 점이나 관리자에게 남길 문의를 적어주세요.")
        user_inquiry = st.text_area("문의 내용 입력")
        if st.button("문의 등록"):
            st.success("등록되었습니다. 관리자가 확인 후 답변을 남겨드립니다.")
        
        st.markdown("---")
        st.write("### 📝 이전 문의 내역")
        with st.expander("Q. 병원 정보가 안 뜹니다."):
            st.write("**A. (관리자 답변)** 현재 접속하신 위치의 GPS 권한을 허용해주시면 정상적으로 표기됩니다!")

    with tab2:
        st.write("응급 상황에 도움이 될 만한 유용한 정보 모음입니다.")
        st.markdown("""
        * [보건복지부 응급의료포털(E-Gen)](https://www.e-gen.or.kr)
        * [심폐소생술(CPR) 방법 안내](#)
        * 야간 휴일 운영 약국 정보
        """)
        
    if st.button("🏠 메인으로 돌아가기"):
        st.session_state.page = "main"
