import streamlit as st

# ----------------------------------------------------
# 1. 페이지 설정 및 커스텀 CSS (텍스트 잘림 방지 및 모바일 최적화)
# ----------------------------------------------------
st.set_page_config(page_title="내 손안의 응급실", page_icon="🚑", layout="wide")

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
        display: flex; gap: 10px; margin-top: 12px; justify-content: space-between;
    }
    .info-box {
        flex: 1; background-color: #F8FAFC; padding: 10px; border-radius: 8px; text-align: center;
        border: 1px solid #E2E8F0;
    }
    .dept-tag {
        display: inline-block; background-color: #EFF6FF; color: #1E40AF;
        padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; margin: 2px;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 2. 사이드바: 지역 선택 기능 (다른 지역 조회)
# ----------------------------------------------------
st.sidebar.markdown("### 📍 지역 설정")
selected_region = st.sidebar.selectbox(
    "조회할 지역을 선택하세요:", 
    ["제주특별자치도", "서울특별시", "부산광역시", "경기도", "강원특별자치도"]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **팁:** 제주도에 거주하시더라도 타지역(서울 등)의 응급실 상황을 미리 확인하실 수 있습니다.")

# ----------------------------------------------------
# 3. 메인 화면 헤더 및 이용 안내
# ----------------------------------------------------
st.markdown(f"### 🚑 내 손안의 응급실 ({selected_region})")
st.caption("실시간 응급실 병상 정보 및 연령·증상별 맞춤 대응 가이드")
st.divider()

with st.container(border=True):
    st.markdown("""
    #### 💡 이용 안내 및 병상 수 읽는 법
    1. **병상 정보 표기:** `잔여 6석 / 전체 16석` 형태로 표시되어 현재 몇 개의 빈자리가 있는지 직관적으로 알 수 있습니다.
    2. 환자의 **현재 증상**과 **연령대**를 선택해 주세요.
    3. 노년층 등 음성 안내가 필요한 경우 아래의 **[🔊 음성으로 가이드 듣기]** 버튼을 활용하세요.
    """)

# ----------------------------------------------------
# 4. 지역별 병원 데이터베이스
# ----------------------------------------------------
region_database = {
    "제주특별자치도": [
        {
            "name": "제주특별자치도서귀포의료원", "type": "지역응급의료센터",
            "gen_curr": 13, "gen_total": 16, "status": "원활",
            "ped_curr": 1, "ped_total": 4, "ped_status": "혼잡",
            "mat_status": "분만 가능 (잔여 1석)", "distance_km": 0.1,
            "departments": ["응급내시경", "성인 위장관"],
            "phone": "064-730-3109", "lat": 33.2547, "lng": 126.5601
        },
        {
            "name": "제주한라병원", "type": "권역외상센터",
            "gen_curr": 0, "gen_total": 15, "status": "혼잡",
            "ped_curr": 3, "ped_total": 3, "ped_status": "원활",
            "mat_status": "분만 가능 (잔여 2석)", "distance_km": 29.8,
            "departments": ["순환기내과", "재관류중재술", "심근경색"],
            "phone": "064-740-5158", "lat": 33.4898, "lng": 126.4842
        },
        {
            "name": "제주중앙병원", "type": "지역응급의료센터",
            "gen_curr": 6, "gen_total": 16, "status": "혼잡",
            "ped_curr": 1, "ped_total": 1, "ped_status": "원활",
            "mat_status": "미지원", "distance_km": 30.5,
            "departments": ["정형외과", "응급내시경", "성인 위장관"],
            "phone": "064-786-7000", "lat": 33.4931, "lng": 126.4740
        },
        {
            "name": "제주대학교병원", "type": "권역응급의료센터",
            "gen_curr": 0, "gen_total": 20, "status": "혼잡",
            "ped_curr": 0, "ped_total": 0, "ped_status": "미지원",
            "mat_status": "분만 가능 (잔여 3석)", "distance_km": 31.4,
            "departments": ["안과", "소화기내과", "산부인과응급", "분만"],
            "phone": "064-717-1900", "lat": 33.4670, "lng": 126.5450
        },
        {
            "name": "한마음병원", "type": "지역응급의료센터",
            "gen_curr": 2, "gen_total": 10, "status": "보통",
            "ped_curr": 1, "ped_total": 3, "ped_status": "보통",
            "mat_status": "미지원", "distance_km": 31.8,
            "departments": ["신경과"],
            "phone": "064-710-1119", "lat": 33.4965, "lng": 126.5432
        },
        {
            "name": "제주한국병원", "type": "응급의료기관",
            "gen_curr": 5, "gen_total": 9, "status": "보통",
            "ped_curr": 0, "ped_total": 0, "ped_status": "미지원",
            "mat_status": "미지원", "distance_km": 32.1,
            "departments": [],
            "phone": "064-750-0119", "lat": 33.5002, "lng": 126.5187
        }
    ],
    "서울특별시": [
        {
            "name": "서울대학교병원", "type": "권역응급의료센터",
            "gen_curr": 4, "gen_total": 30, "status": "보통",
            "ped_curr": 2, "ped_total": 5, "ped_status": "원활",
            "mat_status": "분만 가능 (잔여 2석)", "distance_km": 1.2,
            "departments": ["소아응급", "심혈관응급", "중증외상"],
            "phone": "02-2072-2114", "lat": 37.5796, "lng": 126.9990
        },
        {
            "name": "강남세브란스병원", "type": "권역응급의료센터",
            "gen_curr": 1, "gen_total": 25, "status": "혼잡",
            "ped_curr": 0, "ped_total": 3, "ped_status": "혼잡",
            "mat_status": "분만 가능 (잔여 1석)", "distance_km": 8.5,
            "departments": ["응급중환자실", "심장혈관"],
            "phone": "02-2019-2114", "lat": 37.4938, "lng": 127.0450
        }
    ],
    "부산광역시": [
        {
            "name": "부산대학교병원", "type": "권역응급의료센터",
            "gen_curr": 8, "gen_total": 28, "status": "원활",
            "ped_curr": 3, "ped_total": 4, "ped_status": "원활",
            "mat_status": "분만 가능 (잔여 3석)", "distance_km": 3.4,
            "departments": ["권역외상", "소아응급"],
            "phone": "051-240-7000", "lat": 35.1017, "lng": 129.0256
        }
    ],
    "경기도": [
        {
            "name": "아주대학교병원", "type": "권역응급의료센터",
            "gen_curr": 2, "gen_total": 35, "status": "혼잡",
            "ped_curr": 4, "ped_total": 6, "ped_status": "원활",
            "mat_status": "분만 가능 (잔여 4석)", "distance_km": 4.1,
            "departments": ["중증외상센터", "응급의학과"],
            "phone": "031-219-5114", "lat": 37.2787, "lng": 127.0441
        }
    ],
    "강원특별자치도": [
        {
            "name": "강원대학교병원", "type": "지역응급의료센터",
            "gen_curr": 7, "gen_total": 18, "status": "원활",
            "ped_curr": 1, "ped_total": 2, "ped_status": "원활",
            "mat_status": "분만 가능 (잔여 1석)", "distance_km": 2.5,
            "departments": ["응급의학과"],
            "phone": "033-258-2114", "lat": 37.8722, "lng": 127.7479
        }
    ]
}

current_facilities = region_database.get(selected_region, region_database["제주특별자치도"])

# 최적 병원 선정 정렬
def calc_score(h):
    score = 100 - (h["distance_km"] * 1.5)
    if h["status"] == "혼잡" or h["gen_curr"] == 0:
        score -= 40
    elif h["status"] == "원활":
        score += 20
    return score

current_facilities.sort(key=calc_score, reverse=True)
best_hospital = current_facilities[0]
other_hospitals = current_facilities[1:]

# ----------------------------------------------------
# 5. UI 배치 (좌우 분할)
# ----------------------------------------------------
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
    selected_symptom = st.selectbox("현재 가장 심각한 증상을 선택하세요:", symptoms)
    age = st.radio("환자 연령대:", ["영유아", "어린이", "성인", "노년층"], index=2, horizontal=True)

    # 연령대별 차별화된 가이드 작성
    if "외상" in selected_symptom:
        if age == "노년층":
            guide_text = "어르신 골절은 낙상으로 인한 2차 쇼크 위험이 큽니다. 환자를 절대 움직이지 말고 그 상태로 편안하게 유지시킨 뒤 119에 즉시 연락하세요."
        else:
            guide_text = "출혈 부위를 깨끗한 천으로 강하게 압박하고, 의심되는 골절 부위는 부목을 대어 고정하세요."
    elif "가슴 통증" in selected_symptom:
        if age == "노년층":
            guide_text = "급성 심근경색 가능성이 매우 높습니다. 절대 안정을 취하게 하고 조이는 옷을 풀어준 뒤 즉시 구급차를 부르세요."
        else:
            guide_text = "편안한 자세로 심호흡을 유도하고 통증이 지속되면 즉시 응급실로 이동 준비를 하세요."
    elif age == "노년층":
        guide_text = "노년층 환자는 증상이 급격히 악화될 수 있으므로, 보호자가 체온과 맥박을 수시로 확인하며 신속히 병원으로 이동해야 합니다."
    else:
        guide_text = "환자를 편안하게 눕히고 안정을 취하게 한 뒤 체온 변화를 관찰하세요."

    st.error(f"### 🚨 [{age}] 맞춤 초기 대응 가이드\n\n{guide_text}")

    # 🔊 노년층 및 사용자 편의를 위한 음성 지원 서비스 추가 (Web Speech API 활용)
    voice_script = f"{age} 환자 맞춤 응급 가이드입니다. {guide_text}"
    st.markdown(f"""
        <script>
        function speakText() {{
            const text = "{voice_script}";
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'ko-KR';
            window.speechSynthesis.speak(utterance);
        }}
        </script>
        <button onclick="speakText()" style="
            width: 100%; background-color: #2563EB; color: white; padding: 12px; 
            border: none; border-radius: 8px; font-weight: bold; font-size: 1rem; cursor: pointer; margin-top: 10px;">
            🔊 음성으로 가이드 읽어주기 (노년층 추천)
        </button>
    """, unsafe_allow_html=True)


with col_right:
    st.subheader(f"🏥 {selected_region} 응급의료기관 (총 {len(current_facilities)}건)")
    
    # 최우선 권장 병원 카드 (반응형 구조로 텍스트 잘림 원천 차단)
    best_map = f"https://map.kakao.com/link/to/{best_hospital['name']},{best_hospital['lat']},{best_hospital['lng']}"
    dept_tags_best = "".join([f'<span class="dept-tag">{d}</span>' for d in best_hospital["departments"]])
    
    st.markdown(f"""
    <div class="best-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <span style="background-color: #22C55E; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold;">최우선 권장 병원</span>
                <h3 style="margin: 6px 0 2px 0; color: #1E293B; font-size: 1.25rem;">{best_hospital['name']}</h3>
                <span style="font-size: 0.85rem; color: #64748B;">📞 {best_hospital['phone']} | 📍 {best_hospital['distance_km']}km</span>
            </div>
            <a href="{best_map}" target="_blank" style="background-color: #2563EB; color: white; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-size: 0.85rem; font-weight: bold;">길찾기</a>
        </div>
        <div style="margin: 10px 0;">{dept_tags_best}</div>
        <div class="info-grid">
            <div class="info-box">
                <div style="font-size:0.75rem; color:#64748B;">응급실 일반</div>
                <div style="font-weight:bold; font-size:1rem; color:#1E293B;">잔여 {best_hospital['gen_curr']}석 / 전체 {best_hospital['gen_total']}석</div>
                <div style="font-size:0.75rem; color:#059669; font-weight:bold;">상태: {best_hospital['status']}</div>
            </div>
            <div class="info-box">
                <div style="font-size:0.75rem; color:#64748B;">응급실 소아</div>
                <div style="font-weight:bold; font-size:1rem; color:#1E293B;">잔여 {best_hospital['ped_curr']}석 / 전체 {best_hospital['ped_total']}석</div>
                <div style="font-size:0.75rem; color:#64748B;">상태: {best_hospital['ped_status']}</div>
            </div>
            <div class="info-box">
                <div style="font-size:0.75rem; color:#64748B;">분만실</div>
                <div style="font-weight:bold; font-size:0.9rem; color:#1E293B; margin-top:4px;">{best_hospital['mat_status']}</div>
            </div>
        </div>
        <div style="background-color: #FFFFFF; padding: 10px; border-radius: 6px; margin-top: 12px; font-size: 0.85rem; color: #334155; border: 1px solid #BBF7D0;">
            💡 <b>추천 사유:</b> 현재 위치에서 {best_hospital['distance_km']}km 거리에 있으며, 응급실 병상 가용 상태가 가장 원활하여 신속한 대처가 가능합니다.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 기타 병원 목록 카드
    st.markdown("#### 기타 주변 응급의료기관")
    for h in other_hospitals:
        h_map = f"https://map.kakao.com/link/to/{h['name']},{h['lat']},{h['lng']}"
        dept_tags_h = "".join([f'<span class="dept-tag">{d}</span>' for d in h["departments"]]) if h["departments"] else "<span style='font-size:0.75rem; color:#94A3B8;'>진료과 정보 없음</span>"
        
        st.markdown(f"""
        <div class="hospital-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <h4 style="margin: 0 0 2px 0; color: #1E293B; font-size: 1.1rem;">{h['name']} <span style="font-size:0.75rem; font-weight:normal; color:#64748B;">({h['type']})</span></h4>
                    <span style="font-size: 0.85rem; color: #64748B;">📞 {h['phone']} | 📍 {h['distance_km']}km</span>
                </div>
                <a href="{h_map}" target="_blank" style="background-color: #EFF6FF; color: #2563EB; padding: 6px 12px; border-radius: 6px; text-decoration: none; font-size: 0.85rem; font-weight: bold;">길찾기</a>
            </div>
            <div style="margin: 8px 0;">{dept_tags_h}</div>
            <div class="info-grid">
                <div class="info-box">
                    <div style="font-size:0.75rem; color:#64748B;">응급실 일반</div>
                    <div style="font-weight:bold; font-size:0.9rem; color:#1E293B;">잔여 {h['gen_curr']} / 전체 {h['gen_total']}</div>
                    <div style="font-size:0.75rem; color:#64748B;">({h['status']})</div>
                </div>
                <div class="info-box">
                    <div style="font-size:0.75rem; color:#64748B;">응급실 소아</div>
                    <div style="font-weight:bold; font-size:0.9rem; color:#1E293B;">잔여 {h['ped_curr']} / 전체 {h['ped_total']}</div>
                    <div style="font-size:0.75rem; color:#64748B;">({h['ped_status']})</div>
                </div>
                <div class="info-box">
                    <div style="font-size:0.75rem; color:#64748B;">분만실</div>
                    <div style="font-weight:bold; font-size:0.85rem; color:#1E293B; margin-top:4px;">{h['mat_status']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
