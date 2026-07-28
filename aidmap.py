import streamlit as st
import textwrap

# ----------------------------------------------------
# 1. 페이지 설정 및 디자인 (CSS)
# ----------------------------------------------------
st.set_page_config(page_title="내 손안의 응급실", page_icon="🚑", layout="wide")

st.markdown("""
<style>
    * { word-break: keep-all !important; font-family: 'Pretendard', sans-serif; }
    .main { background-color: #F8FAFC; }
    
    .nemc-top-bar {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        color: white !important; padding: 24px; border-radius: 12px; margin-bottom: 24px;
    }
    
    .guide-box {
        background-color: #FFFFFF; border-left: 4px solid #3B82F6; padding: 16px; 
        border-radius: 8px; margin-bottom: 24px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    .first-aid-box {
        background-color: #FEF2F2; border-left: 4px solid #EF4444; padding: 18px; 
        border-radius: 8px; margin-top: 16px;
    }

    .best-hospital-card {
        background-color: #FFFFFF; border: 2px solid #2563EB; border-radius: 12px;
        padding: 24px; margin-bottom: 24px; box-shadow: 0 6px 16px rgba(37, 99, 235, 0.1);
    }
    
    .recommend-reason {
        background-color: #F8FAFC; color: #334155; padding: 14px 18px;
        border-radius: 8px; font-size: 0.95rem; margin-top: 16px; border: 1px solid #E2E8F0;
    }

    .hospital-card {
        background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px;
        padding: 20px; margin-bottom: 16px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    
    .bed-grid { 
        display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; 
        background-color: #F1F5F9; padding: 12px; border-radius: 8px; 
        margin: 12px 0; font-size: 0.85rem; text-align: center;
    }
    
    .dept-tag { 
        display: inline-block; background-color: #F1F5F9; color: #475569; 
        padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; 
        margin-right: 6px; margin-bottom: 6px; border: 1px solid #CBD5E1;
    }
    
    .btn-kakao { 
        display: inline-block; background-color: #FEE500; color: #000000 !important; 
        padding: 8px 16px; border-radius: 8px; font-size: 0.9rem; font-weight: bold; text-decoration: none; 
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 2. 실시간 병상 및 의료기관 데이터베이스 (전체 세부 데이터 반영)
# ----------------------------------------------------
FACILITY_DB = [
    {
        "name": "제주대학교병원", "type": "센터",
        "gen_curr": "-1*", "gen_total": "20", "status": "혼잡",
        "ped_curr": "-", "ped_total": "-", "ped_status": "-",
        "mat_status": "가능/3", "distance_km": 31.4,
        "departments": ["안과", "소화기내과", "산부인과응급", "산과수술", "분만"],
        "lat": 33.4670, "lng": 126.5450, "phone": "064-717-1900"
    },
    {
        "name": "제주중앙", "type": "센터",
        "gen_curr": "6", "gen_total": "16", "status": "혼잡",
        "ped_curr": "1", "ped_total": "1", "ped_status": "원활",
        "mat_status": "-", "distance_km": 30.5,
        "departments": ["정형외과", "응급내시경", "성인 위장관"],
        "lat": 33.4931, "lng": 126.4740, "phone": "064-786-7000"
    },
    {
        "name": "제주특별자치도서귀포의료원", "type": "센터",
        "gen_curr": "13", "gen_total": "16", "status": "원활",
        "ped_curr": "1", "ped_total": "4", "ped_status": "혼잡",
        "mat_status": "가능/1", "distance_km": 0.1,  # 현재 위치(서귀포) 기준 가장 가깝게 설정
        "departments": ["응급내시경", "성인 위장관"],
        "lat": 33.2547, "lng": 126.5601, "phone": "064-730-3109"
    },
    {
        "name": "제주한국", "type": "기관",
        "gen_curr": "5", "gen_total": "9", "status": "보통",
        "ped_curr": "-", "ped_total": "-", "ped_status": "-",
        "mat_status": "-", "distance_km": 32.1,
        "departments": [],
        "lat": 33.5002, "lng": 126.5187, "phone": "064-750-0119"
    },
    {
        "name": "제주한라병원", "type": "외상",
        "gen_curr": "0", "gen_total": "15", "status": "혼잡",
        "ped_curr": "3", "ped_total": "3", "ped_status": "원활",
        "mat_status": "가능/2", "distance_km": 29.8,
        "departments": ["순환기내과", "재관류중재술", "심근경색"],
        "lat": 33.4898, "lng": 126.4842, "phone": "064-740-5158"
    },
    {
        "name": "한마음병원", "type": "센터",
        "gen_curr": "-", "gen_total": "-", "status": "보통",
        "ped_curr": "-", "ped_total": "-", "ped_status": "-",
        "mat_status": "-", "distance_km": 31.8,
        "departments": ["신경과"],
        "lat": 33.4965, "lng": 126.5432, "phone": "064-710-1119"
    }
]

# ----------------------------------------------------
# 3. 최적 병원 추천 로직 (UI에 노출되지 않음)
# ----------------------------------------------------
def calculate_hospital_score(hospital):
    score = 100
    # 거리 패널티
    score -= (hospital["distance_km"] * 1.5)
    # 혼잡도 가감점
    if hospital["status"] == "혼잡" or hospital["gen_curr"] == "0":
        score -= 40
    elif hospital["status"] == "원활":
        score += 20
    return score

# 내부적으로 점수를 계산하여 가장 최적의 병원 도출
FACILITY_DB.sort(key=calculate_hospital_score, reverse=True)
best_hospital = FACILITY_DB[0]
other_hospitals = FACILITY_DB[1:]

# ----------------------------------------------------
# 4. 앱 화면 UI 구현
# ----------------------------------------------------
st.markdown('<div class="nemc-top-bar"><h1 style="margin:0; font-size:1.8rem;">🚑 내 손안의 응급실</h1><p style="margin:5px 0 0 0; color:#CBD5E1;">현재 위치 기반 실시간 병상 조회 및 초기 대응 가이드</p></div>', unsafe_allow_html=True)

# 💡 사이트 이용 안내
st.markdown("""
<div class="guide-box">
    <b style="color: #1D4ED8; font-size: 1.1rem;">이용 안내</b>
    <ol style="margin: 8px 0 0 0; padding-left: 20px; color: #475569; line-height: 1.7;">
        <li>환자의 <b>현재 증상</b>과 <b>연령대</b>를 선택해 주세요.</li>
        <li>화면에 안내되는 <b>상황별 맞춤 응급처치</b>를 먼저 실시하여 환자의 안정을 확보하세요.</li>
        <li>우측 상단에 현재 위치(서귀포시 기준)와 실시간 병상 여유도를 계산하여 <b>가장 빠르게 진료받을 수 있는 병원</b>을 추천해 드립니다.</li>
    </ol>
</div>
""", unsafe_allow_html=True)

col_left, col_right = st.columns([1.0, 1.2], gap="large")

with col_left:
    st.subheader("🩺 환자 상태 입력")
    
    # 파일 3: 증상 선택 폭 대폭 확대
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

    # 파일 4: 증상과 연령에 맞춘 구체적이고 실질적인 응급처치 가이드 제공
    first_aid_guide = ""
    if "외상" in selected_symptom:
        first_aid_guide = "<b>1. 즉각적인 지혈:</b> 깨끗한 천이나 거즈로 출혈 부위를 직접 강하게 압박하세요.<br><b>2. 고정:</b> 골절이 의심될 경우, 뼈를 맞추려 하지 말고 부목(두꺼운 잡지, 막대기 등)을 대어 다친 부위가 움직이지 않게 고정하세요."
    elif "가슴 통증" in selected_symptom:
        first_aid_guide = "<b>1. 기도 확보 및 안정:</b> 환자를 편안한 자세로 눕히고 꽉 조이는 옷이나 벨트를 풀어주세요.<br><b>2. 심폐소생술(CPR) 준비:</b> 환자의 의식이 희미해지면 즉시 119에 신고한 뒤, 구급대원의 지시에 따라 가슴 정중앙을 강하고 빠르게 압박하세요."
    elif "소아" in selected_symptom:
        first_aid_guide = f"<b>1. 체온 조절:</b> 미지근한 물을 적신 수건으로 <b>{age}</b>의 몸을 가볍게 문질러 닦아주세요. 찬물이나 알코올은 절대 금물입니다.<br><b>2. 해열제 교차복용:</b> 2시간 간격으로 아세트아미노펜과 이부프로펜 계열 해열제를 교차로 먹이며 병원으로 이동하세요."
    elif "알레르기" in selected_symptom:
        first_aid_guide = "<b>1. 원인 물질 차단:</b> 알레르기를 유발한 음식이나 벌레 등에서 즉시 멀어지세요.<br><b>2. 자가 주사기 사용:</b> 아나필락시스 진단을 받은 적이 있고 에피네프린 자가 주사기가 있다면 즉시 허벅지 바깥쪽에 주사한 후 119를 부르세요."
    else:
        first_aid_guide = "<b>1. 안위 유지:</b> 환자를 편안하게 눕히고 체온을 유지해 주세요.<br><b>2. 수분 섭취:</b> 탈수를 막기 위해 소량의 물을 자주 마시게 하되, 의식이 흐릿한 경우 억지로 물을 먹이지 마세요."

    st.markdown(f"""
    <div class="first-aid-box">
        <h4 style="margin: 0 0 12px 0; color: #B91C1C;">🚨 즉각적인 초기 대응 가이드</h4>
        <p style="margin: 0; font-size: 0.95rem; color: #7F1D1D; line-height: 1.6;">{first_aid_guide}</p>
    </div>
    """, unsafe_allow_html=True)


with col_right:
    st.subheader(f"🏥 주변 응급의료기관 정보 (총 {len(FACILITY_DB)}건)")
    st.caption("※ 가용병상수 / 전체병상수 기준으로 표기됩니다.")
    
    # 1. 가장 최적의 병원 추천 (상단 배치)
    dept_tags = "".join([f'<span class="dept-tag">{d}</span>' for d in best_hospital["departments"]])
    map_url = f"https://map.kakao.com/link/to/{best_hospital['name']},{best_hospital['lat']},{best_hospital['lng']}"
    
    best_card = textwrap.dedent(f"""
        <div class="best-hospital-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <span style="background-color: #2563EB; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: bold;">최우선 권장 병원</span>
                    <h3 style="margin: 8px 0 4px 0; color: #0F172A; font-size: 1.4rem;">{best_hospital['name']}</h3>
                    <div style="font-size: 0.9rem; color: #64748B; margin-bottom: 12px;">📞 {best_hospital['phone']}</div>
                </div>
                <a href="{map_url}" target="_blank" class="btn-kakao">📍 길찾기 ({best_hospital['distance_km']}km)</a>
            </div>
            
            <div style="margin: 12px 0;">{dept_tags}</div>
            
            <div class="bed-grid">
                <div><span style="color: #64748B;">응급실 일반</span><br><b style="color: {'#16A34A' if best_hospital['status']=='원활' else '#DC2626'}; font-size: 1.1rem;">{best_hospital['gen_curr']}/{best_hospital['gen_total']}</b><br><span style="font-size:0.75rem;">({best_hospital['status']})</span></div>
                <div><span style="color: #64748B;">응급실 소아</span><br><b style="font-size: 1.1rem;">{best_hospital['ped_curr']}/{best_hospital['ped_total']}</b><br><span style="font-size:0.75rem;">({best_hospital['ped_status']})</span></div>
                <div><span style="color: #64748B;">분만실 상태</span><br><b style="color: #059669; font-size: 1.1rem;">{best_hospital['mat_status']}</b></div>
            </div>
            
            <!-- 추천 이유 안내 -->
            <div class="recommend-reason">
                💡 <b>추천 사유:</b> 현재 계신 곳에서 {best_hospital['distance_km']}km로 가장 인접해 있으며, 일반 응급 병상 상태가 '{best_hospital['status']}' 수준을 유지하고 있어 도착 시 대기 시간을 최소화할 수 있습니다.
            </div>
        </div>
    """).strip()
    st.markdown(best_card, unsafe_allow_html=True)

    # 파일 1: 전체 병원 정보 목록화 (나머지 병원들 하단에 나열)
    for h in other_hospitals:
        tags = "".join([f'<span class="dept-tag">{d}</span>' for d in h["departments"]]) if h["departments"] else "<span style='font-size:0.8rem; color:#94A3B8;'>세부 진료과 정보 없음</span>"
        h_map = f"https://map.kakao.com/link/to/{h['name']},{h['lat']},{h['lng']}"
        gen_color = "#DC2626" if h["status"] == "혼잡" else "#16A34A" if h["status"] == "원활" else "#D97706"
        
        card_html = textwrap.dedent(f"""
            <div class="hospital-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <div style="display: flex; align-items: center;">
                        <span style="background-color: #94A3B8; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; margin-right: 8px;">{h['type']}</span>
                        <h4 style="margin: 0; color: #1E293B; font-size: 1.1rem;">{h['name']}</h4>
                    </div>
                    <a href="{h_map}" target="_blank" style="font-size: 0.85rem; color: #2563EB; text-decoration: none; font-weight: bold; background-color: #EFF6FF; padding: 4px 10px; border-radius: 6px;">거리 {h['distance_km']}km ></a>
                </div>
                
                <div style="margin: 10px 0;">{tags}</div>
                
                <div class="bed-grid" style="background-color: transparent; padding: 0; margin-top: 10px;">
                    <div><span style="color: #64748B;">응급실 일반</span><br><b style="color: {gen_color};">{h['gen_curr']}/{h['gen_total']}</b><br><span style="font-size:0.75rem;">({h['status']})</span></div>
                    <div><span style="color: #64748B;">응급실 소아</span><br><b>{h['ped_curr']}/{h['ped_total']}</b><br><span style="font-size:0.75rem;">({h['ped_status']})</span></div>
                    <div><span style="color: #64748B;">분만실 상태</span><br><b style="color: #059669;">{h['mat_status']}</b></div>
                </div>
            </div>
        """).strip()
        st.markdown(card_html, unsafe_allow_html=True)
