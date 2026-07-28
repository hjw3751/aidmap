import streamlit as st

# ----------------------------------------------------
# 1. 페이지 설정
# ----------------------------------------------------
st.set_page_config(page_title="내 손안의 응급실", page_icon="🚑", layout="wide")

st.markdown("""
    ### 🚑 내 손안의 응급실
    실시간 병상 조회 및 연령·증상별 맞춤 초기 대응 가이드
""")
st.divider()

# ----------------------------------------------------
# 2. 탭 구성 (내 주변 / 다른 지역 조회)
# ----------------------------------------------------
tab_local, tab_other = st.tabs(["📍 내 주변 응급실 (제주/서귀포)", "🗺️ 다른 지역 응급실 조회"])

# ====================================================
# [탭 1] 제주/서귀포 지역 (기존 기능 고도화)
# ====================================================
with tab_local:
    with st.container(border=True):
        st.markdown("""
        #### 💡 이용 안내
        1. 환자의 **현재 증상**과 **연령대**를 선택해 주세요. 연령에 따라 맞춤 가이드가 다르게 제공됩니다.
        2. 화면에 안내되는 **상황별 맞춤 응급처치**를 먼저 실시하여 환자의 안정을 확보하세요.
        3. 실시간 병상 여유도를 분석하여 **가장 빠르게 진료받을 수 있는 병원**을 추천해 드립니다.
        """)

    col_left, col_right = st.columns([1.0, 1.2], gap="large")

    with col_left:
        st.subheader("🩺 환자 상태 입력")
        
        symptoms = [
            "🦴 심한 외상 및 출혈 (골절 의심)", 
            "🫀 가슴 통증 및 호흡곤란", 
            "🗣️ 갑작스러운 안면 마비 및 말 어눌함",
            "🥜 심각한 알레르기 반응 (호흡 곤란 동반)",
            "🔥 심한 화상",
            "👶 소아 39도 이상 고열 및 경련", 
            "🤒 가벼운 단순 발열 및 약 처방"
        ]
        selected_symptom = st.selectbox("현재 가장 심각한 증상을 선택하세요:", symptoms, key="local_symptom")
        age = st.radio("환자 연령대:", ["영유아", "어린이", "성인", "노년층"], index=2, horizontal=True, key="local_age")

        # 연령대 및 증상별로 완전히 차별화된 맞춤 응급처치 가이드
        guide_text = ""
        
        if "외상" in selected_symptom:
            if age in ["영유아", "어린이"]:
                guide_text = f"**[{age} 맞춤 응급처치]**\n\n1. **아이 달래기 및 고정:** 아이가 놀라 움직이면 골절 부위가 악화되므로 품에 안아 진정시키고 부목으로 고정하세요.\n2. **직접 압박:** 출혈 부위는 깨끗한 거즈나 손수건으로 직접 누르되, 아이의 체중을 고려해 너무 강한 압박은 피하세요."
            else:
                guide_text = f"**[{age} 맞춤 응급처치]**\n\n1. **환부 고정:** 부러진 뼈가 피부를 찌르지 않도록 단단한 물체(잡지, 막대기 등)로 위아래 관절을 포함해 고정하세요.\n2. **지혈 및 쇼크 방지:** 출혈 부위를 강하게 압박하고, 다리를 심장보다 약간 높게 하여 쇼크를 예방하세요."
        
        elif "가슴 통증" in selected_symptom:
            if age == "노년층":
                guide_text = f"**[{age} 맞춤 응급처치]**\n\n1. **심근경색 의심 및 절대 안정:** 환자를 절대 움직이지 않게 하고 편안한 자세로 앉히거나 눕히세요. 꽉 조이는 옷과 벨트를 즉시 푸세요.\n2. **119 즉시 신고:** 심혈관 질환 위험이 매우 높으므로 자가 운전은 절대 금하며 119를 부르고 아스피린 복용 여부를 확인하세요."
            else:
                guide_text = f"**[{age} 맞춤 응급처치]**\n\n1. **호흡 안정:** 편안한 자세를 유지하게 하고 심호흡을 유도하세요.\n2. **응급 체제 전환:** 통증이 10분 이상 지속되면 즉시 119 신고 및 심폐소생술 준비를 하세요."
        
        elif "소아" in selected_symptom or "고열" in selected_symptom:
            if age in ["영유아", "어린이"]:
                guide_text = f"**[{age} 맞춤 응급처치]**\n\n1. **미지근한 마사지:** 미지근한 물을 적신 수건으로 아이의 목, 겨드랑이를 부드럽게 닦아주세요. (찬물이나 알코올 절대 금지)\n2. **해열제 투여:** 체중에 맞는 아세트아미노펜 또는 이부프로펜 계열 해열제를 교차 복용하며 열성 경련 여부를 주시하세요."
            else:
                guide_text = f"**[{age} 맞춤 응급처치]**\n\n1. **수분 보충:** 미지근한 물을 자주 마시게 하여 탈수를 방지하세요.\n2. **체온 모니터링:** 해열제를 복용하고 30분 단위로 체온 변화를 체크하세요."
        
        elif "알레르기" in selected_symptom:
            guide_text = f"**[{age} 맞춤 응급처치]**\n\n1. **원인 차단:** 알레르기 유발 물질(음식, 벌레 등)과의 접촉을 즉시 차단하세요.\n2. **에피네프린 투여:** 자가 주사기가 있다면 즉시 허벅지 외측에 투여하고 119에 신고하세요."
        
        else:
            guide_text = f"**[{age} 맞춤 응급처치]**\n\n1. **안위 유지:** 편안한 장소에서 휴식을 취하게 하세요.\n2. **증상 관찰:** 체온과 맥박을 체크하며 증상이 악화되는지 지켜보세요."

        st.error(f"### 🚨 {age} 맞춤 초기 대응 가이드\n\n{guide_text}")

    with col_right:
        st.subheader("🏥 제주 지역 응급의료기관 정보 (총 6건)")
        st.caption("※ 가용병상수 / 전체병상수 기준")
        
        facilities_jeju = [
            {
                "name": "제주대학교병원", "type": "센터",
                "gen_curr": "-1*", "gen_total": "20", "status": "혼잡",
                "ped_curr": "-", "ped_total": "-", "ped_status": "-",
                "mat_status": "가능 (잔여 3석)", "distance_km": 31.4,
                "departments": ["안과", "소화기내과", "산부인과응급", "산과수술", "분만"],
                "phone": "064-717-1900", "lat": 33.4670, "lng": 126.5450
            },
            {
                "name": "제주중앙", "type": "센터",
                "gen_curr": "6", "gen_total": "16", "status": "혼잡",
                "ped_curr": "1", "ped_total": "1", "ped_status": "원활",
                "mat_status": "불지원", "distance_km": 30.5,
                "departments": ["정형외과", "응급내시경", "성인 위장관"],
                "phone": "064-786-7000", "lat": 33.4931, "lng": 126.4740
            },
            {
                "name": "제주특별자치도서귀포의료원", "type": "센터",
                "gen_curr": "13", "gen_total": "16", "status": "원활",
                "ped_curr": "1", "ped_total": "4", "ped_status": "혼잡",
                "mat_status": "가능 (잔여 1석)", "distance_km": 0.1,
                "departments": ["응급내시경", "성인 위장관"],
                "phone": "064-730-3109", "lat": 33.2547, "lng": 126.5601
            },
            {
                "name": "제주한국", "type": "기관",
                "gen_curr": "5", "gen_total": "9", "status": "보통",
                "ped_curr": "-", "ped_total": "-", "ped_status": "-",
                "mat_status": "불지원", "distance_km": 32.1,
                "departments": [],
                "phone": "064-750-0119", "lat": 33.5002, "lng": 126.5187
            },
            {
                "name": "제주한라병원", "type": "외상",
                "gen_curr": "0", "gen_total": "15", "status": "혼잡",
                "ped_curr": "3", "ped_total": "3", "ped_status": "원활",
                "mat_status": "가능 (잔여 2석)", "distance_km": 29.8,
                "departments": ["순환기내과", "재관류중재술", "심근경색"],
                "phone": "064-740-5158", "lat": 33.4898, "lng": 126.4842
            },
            {
                "name": "한마음병원", "type": "센터",
                "gen_curr": "-", "gen_total": "-", "status": "보통",
                "ped_curr": "-", "ped_total": "-", "ped_status": "-",
                "mat_status": "불지원", "distance_km": 31.8,
                "departments": ["신경과"],
                "phone": "064-710-1119", "lat": 33.4965, "lng": 126.5432
            }
        ]

        def calc_score(h):
            score = 100 - (h["distance_km"] * 1.5)
            if h["status"] == "혼잡" or h["gen_curr"] == "0":
                score -= 40
            elif h["status"] == "원활":
                score += 20
            return score

        facilities_jeju.sort(key=calc_score, reverse=True)
        best_j = facilities_jeju[0]
        others_j = facilities_jeju[1:]

        with st.container(border=True):
            st.markdown("🌟 **[최우선 권장 병원]**")
            jc1, jc2 = st.columns([3, 1])
            with jc1:
                st.markdown(f"### {best_j['name']} (`{best_j['type']}`)")
                st.write(f"📞 전화번호: {best_j['phone']}")
            with jc2:
                map_link = f"https://map.kakao.com/link/to/{best_j['name']},{best_j['lat']},{best_j['lng']}"
                st.link_button("📍 길찾기", map_link, use_container_width=True)
                
            depts = ", ".join([f"`{d}`" for d in best_j["departments"]]) if best_j["departments"] else "정보 없음"
            st.write(f"진료과: {depts}")
            
            jb1, jb2, jb3 = st.columns(3)
            jb1.metric("응급실 일반", f"{best_j['gen_curr']}/{best_j['gen_total']}", best_j["status"])
            jb2.metric("응급실 소아", f"{best_j['ped_curr']}/{best_j['ped_total']}", best_j["ped_status"])
            jb3.metric("분만실", best_j["mat_status"])
            
            st.info(f"💡 **추천 사유:** 현재 위치에서 {best_j['distance_km']}km로 가장 가깝고, 응급실 병상 상태가 '{best_j['status']}' 상태여서 가장 신속한 진료가 가능합니다.")

        st.markdown("#### 기타 제주 지역 응급의료기관")
        for h in others_j:
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


# ====================================================
# [탭 2] 다른 지역 조회 (서울, 부산 등 확장 탭)
# ====================================================
with tab_other:
    st.subheader("🗺️ 타 지역 응급의료기관 실시간 조회")
    selected_region = st.selectbox("조회할 지역을 선택하세요:", ["서울특별시", "부산광역시", "경기도", "강원특별자치도"])
    
    # 지역별 샘플 데이터베이스
    other_region_data = {
        "서울특별시": [
            {"name": "서울대학교병원", "type": "권역응급", "gen_curr": "4", "gen_total": "30", "status": "보통", "ped_curr": "2", "ped_total": "5", "ped_status": "원활", "mat_status": "가능 (잔여 2석)", "phone": "02-2072-2114", "lat": 37.5796, "lng": 126.9990},
            {"name": "강남세브란스병원", "type": "권역응급", "gen_curr": "1", "gen_total": "25", "status": "혼잡", "ped_curr": "0", "ped_total": "3", "ped_status": "혼잡", "mat_status": "가능 (잔여 1석)", "phone": "02-2019-2114", "lat": 37.4938, "lng": 127.0450},
        ],
        "부산광역시": [
            {"name": "부산대학교병원", "type": "권역응급", "gen_curr": "8", "gen_total": "28", "status": "원활", "ped_curr": "3", "ped_total": "4", "ped_status": "원활", "mat_status": "가능 (잔여 3석)", "phone": "051-240-7000", "lat": 35.1017, "lng": 129.0256},
            {"name": "동아대학교병원", "type": "지역응급", "gen_curr": "3", "gen_total": "20", "status": "보통", "ped_curr": "1", "ped_total": "2", "ped_status": "보통", "mat_status": "불지원", "phone": "051-240-5000", "lat": 35.1187, "lng": 129.0163},
        ],
        "경기도": [
            {"name": "아주대학교병원", "type": "권역응급", "gen_curr": "2", "gen_total": "35", "status": "혼잡", "ped_curr": "4", "ped_total": "6", "ped_status": "원활", "mat_status": "가능 (잔여 4석)", "phone": "031-219-5114", "lat": 37.2787, "lng": 127.0441},
            {"name": "분당서울대학교병원", "type": "권역응급", "gen_curr": "10", "gen_total": "30", "status": "원활", "ped_curr": "2", "ped_total": "4", "ped_status": "원활", "mat_status": "가능 (잔여 2석)", "phone": "031-787-7114", "lat": 37.3523, "lng": 127.1245},
        ],
        "강원특별자치도": [
            {"name": "강원대학교병원", "type": "지역응급", "gen_curr": "7", "gen_total": "18", "status": "원활", "ped_curr": "1", "ped_total": "2", "ped_status": "원활", "mat_status": "가능 (잔여 1석)", "phone": "033-258-2114", "lat": 37.8722, "lng": 127.7479},
        ]
    }
    
    current_hospitals = other_region_data.get(selected_region, [])
    st.markdown(f"### 📍 {selected_region} 응급의료기관 목록 (총 {len(current_hospitals)}건)")
    
    for oh in current_hospitals:
        with st.container(border=True):
            orc1, orc2 = st.columns([3, 1])
            with orc1:
                st.markdown(f"**{oh['name']}** (`{oh['type']}`)")
                st.write(f"📞 전화번호: {oh['phone']}")
            with orc2:
                oh_map = f"https://map.kakao.com/link/to/{oh['name']},{oh['lat']},{oh['lng']}"
                st.link_button("📍 길찾기", oh_map, use_container_width=True)
            
            om1, om2, om3 = st.columns(3)
            om1.metric("응급실 일반", f"{oh['gen_curr']}/{oh['gen_total']}", oh["status"])
            om2.metric("응급실 소아", f"{oh['ped_curr']}/{oh['ped_total']}", oh["ped_status"])
            om3.metric("분만실", oh["mat_status"])
