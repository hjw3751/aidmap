import streamlit as st

# ----------------------------------------------------
# 1. 페이지 설정
# ----------------------------------------------------
st.set_page_config(page_title="내 손안의 응급실", page_icon="🚑", layout="wide")

# 상단 타이틀 배너 (네이티브 마크업 사용)
st.markdown("""
    ### 🚑 내 손안의 응급실
    현재 위치 기반 실시간 병상 조회 및 초기 대응 가이드
""")
st.divider()

# 💡 사이트 이용 안내
with st.container(border=True):
    st.markdown("""
    #### 💡 사이트 이용 안내
    1. 환자의 **현재 증상**과 **연령대**를 선택해 주세요.
    2. 화면에 안내되는 **상황별 맞춤 응급처치**를 먼저 실시하여 환자의 안정을 확보하세요.
    3. 우측 상단에 현재 위치(서귀포시 기준)와 실시간 병상 여유도를 계산하여 **가장 빠르게 진료받을 수 있는 병원**을 추천해 드립니다.
    """)

col_left, col_right = st.columns([1.0, 1.2], gap="large")

with col_left:
    st.subheader("🩺 환자 상태 입력")
    
    # 증상 선택 폭 대폭 확대
    symptoms = [
        "🦴 심한 외상 및 출혈 (골절 의심)", 
        "🫀 가슴 통증 및 호흡곤란", 
        "🗣️ 갑작스러운 안면 마비 및 말 어눌함",
        "🥜 심각한 알레르기 반응 (호흡 곤란 동반)",
        "🔥 심한 화상",
        "👶 소아 39도 이상 고열 및 경련", 
        "🤒 가벼운 단순 발열 및 약 처방"
    ]
    selected_symptom = st.selectbox("현재 가장 심각한 증상을 선택하세요:", symptoms)
    age = st.radio("환자 연령대:", ["영유아", "어린이", "성인", "노년층"], index=2, horizontal=True)

    # 증상별 구체적인 응급처치 가이드
    if "외상" in selected_symptom:
        guide_text = "**1. 즉각적인 지혈:** 깨끗한 천이나 거즈로 출혈 부위를 직접 강하게 압박하세요.\n\n**2. 고정:** 골절이 의심될 경우, 뼈를 맞추려 하지 말고 부목(두꺼운 잡지, 막대기 등)을 대어 다친 부위가 움직이지 않게 고정하세요."
    elif "가슴 통증" in selected_symptom:
        guide_text = "**1. 기도 확보 및 안정:** 환자를 편안한 자세로 눕히고 꽉 조이는 옷이나 벨트를 풀어주세요.\n\n**2. 심폐소생술(CPR) 준비:** 환자의 의식이 희미해지면 즉시 119에 신고한 뒤, 구급대원의 지시에 따라 가슴 정중앙을 강하고 빠르게 압박하세요."
    elif "소아" in selected_symptom:
        guide_text = f"**1. 체온 조절:** 미지근한 물을 적신 수건으로 **{age}**의 몸을 가볍게 문질러 닦아주세요. 찬물이나 알코올은 절대 금물입니다.\n\n**2. 해열제 교차복용:** 2시간 간격으로 아세트아미노펜과 이부프로펜 계열 해열제를 교차로 먹이며 병원으로 이동하세요."
    elif "알레르기" in selected_symptom:
        guide_text = "**1. 원인 물질 차단:** 알레르기를 유발한 음식이나 벌레 등에서 즉시 멀어지세요.\n\n**2. 자가 주사기 사용:** 아나필락시스 진단을 받은 적이 있고 에피네프린 자가 주사기가 있다면 즉시 허벅지 바깥쪽에 주사한 후 119를 부르세요."
    else:
        guide_text = "**1. 안위 유지:** 환자를 편안하게 눕히고 체온을 유지해 주세요.\n\n**2. 수분 섭취:** 탈수를 막기 위해 소량의 물을 자주 마시게 하되, 의식이 흐릿한 경우 억지로 물을 먹이지 마세요."

    st.error(f"### 🚨 즉각적인 초기 대응 가이드\n\n{guide_text}")


with col_right:
    st.subheader("🏥 주변 응급의료기관 정보 (총 6건)")
    st.caption("※ 가용병상수 / 전체병상수 기준으로 표기됩니다.")
    
    # ----------------------------------------------------
    # 제주 지역 전체 6개 병원 데이터베이스
    # ----------------------------------------------------
    facilities = [
        {
            "name": "제주대학교병원", "type": "센터",
            "gen_curr": "-1*", "gen_total": "20", "status": "혼잡",
            "ped_curr": "-", "ped_total": "-", "ped_status": "-",
            "mat_status": "가능/3", "distance_km": 31.4,
            "departments": ["안과", "소화기내과", "산부인과응급", "산과수술", "분만"],
            "phone": "064-717-1900", "lat": 33.4670, "lng": 126.5450
        },
        {
            "name": "제주중앙", "type": "센터",
            "gen_curr": "6", "gen_total": "16", "status": "혼잡",
            "ped_curr": "1", "ped_total": "1", "ped_status": "원활",
            "mat_status": "-", "distance_km": 30.5,
            "departments": ["정형외과", "응급내시경", "성인 위장관"],
            "phone": "064-786-7000", "lat": 33.4931, "lng": 126.4740
        },
        {
            "name": "제주특별자치도서귀포의료원", "type": "센터",
            "gen_curr": "13", "gen_total": "16", "status": "원활",
            "ped_curr": "1", "ped_total": "4", "ped_status": "혼잡",
            "mat_status": "가능/1", "distance_km": 0.1,  # 현재 위치(서귀포) 기준 가장 가깝게 설정
            "departments": ["응급내시경", "성인 위장관"],
            "phone": "064-730-3109", "lat": 33.2547, "lng": 126.5601
        },
        {
            "name": "제주한국", "type": "기관",
            "gen_curr": "5", "gen_total": "9", "status": "보통",
            "ped_curr": "-", "ped_total": "-", "ped_status": "-",
            "mat_status": "-", "distance_km": 32.1,
            "departments": [],
            "phone": "064-750-0119", "lat": 33.5002, "lng": 126.5187
        },
        {
            "name": "제주한라병원", "type": "외상",
            "gen_curr": "0", "gen_total": "15", "status": "혼잡",
            "ped_curr": "3", "ped_total": "3", "ped_status": "원활",
            "mat_status": "가능/2", "distance_km": 29.8,
            "departments": ["순환기내과", "재관류중재술", "심근경색"],
            "phone": "064-740-5158", "lat": 33.4898, "lng": 126.4842
        },
        {
            "name": "한마음병원", "type": "센터",
            "gen_curr": "-", "gen_total": "-", "status": "보통",
            "ped_curr": "-", "ped_total": "-", "ped_status": "-",
            "mat_status": "-", "distance_km": 31.8,
            "departments": ["신경과"],
            "phone": "064-710-1119", "lat": 33.4965, "lng": 126.5432
        }
    ]

    # 내부 최적화 정렬 로직 (수식 UI 노출 없음)
    def calc_score(h):
        score = 100 - (h["distance_km"] * 1.5)
        if h["status"] == "혼잡" or h["gen_curr"] == "0":
            score -= 40
        elif h["status"] == "원활":
            score += 20
        return score

    facilities.sort(key=calc_score, reverse=True)
    best = facilities[0]
    others = facilities[1:]

    # 1. 최우선 권장 병원 카드 (상단 배치)
    with st.container(border=True):
        st.markdown("🌟 **[최우선 권장 병원]**")
        hc1, hc2 = st.columns([3, 1])
        with hc1:
            st.markdown(f"### {best['name']} (`{best['type']}`)")
            st.write(f"📞 전화번호: {best['phone']}")
        with hc2:
            map_link = f"https://map.kakao.com/link/to/{best['name']},{best['lat']},{best['lng']}"
            st.link_button("📍 길찾기", map_link, use_container_width=True)
            
        depts = ", ".join([f"`{d}`" for d in best["departments"]]) if best["departments"] else "정보 없음"
        st.write(f"진료과: {depts}")
        
        bc1, bc2, bc3 = st.columns(3)
        bc1.metric("응급실 일반", f"{best['gen_curr']}/{best['gen_total']}", best["status"])
        bc2.metric("응급실 소아", f"{best['ped_curr']}/{best['ped_total']}", best["ped_status"])
        bc3.metric("분만실", best["mat_status"])
        
        st.info(f"💡 **추천 사유:** 현재 위치에서 {best['distance_km']}km로 가장 가깝고, 응급실 병상 상태가 '{best['status']}' 상태여서 가장 신속한 진료가 가능합니다.")

    # 2. 나머지 병원 목록 카드
    st.markdown("#### 기타 주변 응급의료기관")
    for h in others:
        with st.container(border=True):
            oc1, oc2 = st.columns([3, 1])
            with oc1:
                st.markdown(f"**{h['name']}** (`{h['type']}`)")
            with oc2:
                h_map = f"https://map.kakao.com/link/to/{h['name']},{h['lat']},{h['lng']}"
                st.link_button(f"길찾기 ({h['distance_km']}km)", h_map, use_container_width=True)
            
            h_depts = ", ".join([f"`{d}`" for d in h["departments"]]) if h["departments"] else "정보 없음"
            st.write(f"진료과: {h_depts}")
            
            oc3, oc4, oc5 = st.columns(3)
            oc3.metric("응급실 일반", f"{h['gen_curr']}/{h['gen_total']}", h["status"])
            oc4.metric("응급실 소아", f"{h['ped_curr']}/{h['ped_total']}", h["ped_status"])
            oc5.metric("분만실", h["mat_status"])
