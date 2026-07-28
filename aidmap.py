import streamlit as st
import textwrap

# ----------------------------------------------------
# 1. 페이지 설정 및 통합 커스텀 CSS
# ----------------------------------------------------
st.set_page_config(page_title="내 손안의 응급실", page_icon="🚑", layout="wide")

st.markdown("""
<style>
    * { word-break: keep-all !important; font-family: 'Pretendard', sans-serif; }
    .main { background-color: #F8FAFC; }
    
    .nemc-top-bar {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%);
        color: white !important; padding: 20px 24px; border-radius: 12px; margin-bottom: 20px;
    }
    
    .guide-box {
        background-color: #FFFFFF; border-left: 4px solid #10B981; padding: 16px; 
        border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    .first-aid-box {
        background-color: #FEF2F2; border-left: 4px solid #EF4444; padding: 16px; 
        border-radius: 8px; margin-top: 10px;
    }

    .best-hospital-card {
        background-color: #F0F9FF; border: 2px solid #3B82F6; border-radius: 12px;
        padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
    }
    
    .hospital-card {
        background-color: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 10px;
        padding: 16px; margin-bottom: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }
    
    .recommend-reason {
        background-color: #DBEAFE; color: #1E3A8A; padding: 10px 14px;
        border-radius: 8px; font-size: 0.9rem; font-weight: bold; margin-bottom: 12px;
    }

    .bed-grid { 
        display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; 
        background-color: #F1F5F9; padding: 10px; border-radius: 6px; 
        margin: 10px 0; font-size: 0.8rem; text-align: center;
    }
    .dept-tag { 
        display: inline-block; background-color: #E2E8F0; color: #334155; 
        padding: 3px 8px; border-radius: 4px; font-size: 0.75rem; 
        margin-right: 4px; margin-bottom: 4px; border: 1px solid #CBD5E1;
    }
    .btn-action { 
        display: inline-block; padding: 7px 12px; border-radius: 6px; 
        font-size: 0.82rem; font-weight: bold; text-decoration: none !important; margin-right: 6px; 
    }
    .btn-call { background-color: #2563EB; color: #FFFFFF !important; }
    .btn-kakao { background-color: #FEE500; color: #000000 !important; }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 2. 스크린샷 100% 반영 데이터베이스 (제주 지역)
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
        "mat_status": "가능/1", "distance_km": 0.1,
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
# 3. 내부 추천 로직 (UI 비노출)
# ----------------------------------------------------
def calculate_hospital_score(hospital):
    score = 100
    score -= (hospital["distance_km"] * 1.5)
    if hospital["status"] == "혼잡" or hospital["gen_curr"] == "0":
        score -= 40
    elif hospital["status"] == "원활":
        score += 20
    return score

FACILITY_DB.sort(key=calculate_hospital_score, reverse=True)
best_hospital = FACILITY_DB[0]
other_hospitals = FACILITY_DB[1:]

# ----------------------------------------------------
# 4. 화면 UI 렌더링
# ----------------------------------------------------
st.markdown('<div class="nemc-top-bar"><h2>🚑 내 손안의 응급실</h2><p>현재 위치 기반 실시간 병상 조회 및 응급 가이드</p></div>', unsafe_allow_html=True)

# 💡 사이트 사용 방법 안내 (추가됨)
st.markdown("""
<div class="guide-box">
    <h4 style="margin: 0 0 8px 0; color: #065F46;">💡 사이트 이용 가이드</h4>
    <ol style="margin: 0; padding-left: 20px; font-size: 0.9rem; color: #334155; line-height: 1.6;">
        <li>좌측에서 <b>환자의 현재 증상</b>과 <b>연령대</b>를 정확히 선택해 주세요.</li>
        <li>화면 좌측 하단에 나타나는 <b>상황별 맞춤 응급처치</b>를 먼저 실시하며 구급차를 기다리거나 이동을 준비하세요.</li>
        <li>우측 상단에 AI가 <b>현재 위치(거리)와 실시간 병상 혼잡도</b>를 분석하여 가장 적합한 병원을 1순위로 추천합니다.</li>
        <li>'길찾기' 버튼을 누르면 즉시 내비게이션으로 연결됩니다.</li>
    </ol>
</div>
""", unsafe_allow_html=True)

col_left, col_right = st.columns([1.0, 1.2], gap="large")

with col_left:
    st.subheader("🩺 환자 상태 입력 및 응급처치")
    
    symptoms = ["🦴 골절 의심 / 출혈성 외상", "🫀 심한 흉통 및 호흡곤란", "👶 소아 39도 이상 고열", "🤒 단순 발열 및 약 처방"]
    selected_symptom = st.selectbox("환자의 대표 증상을 선택하세요:", symptoms)
    age = st.radio("환자 연령대:", ["영유아", "어린이", "성인", "노년층"], index=1, horizontal=True)

    # 💡 구체적인 응급처치 가이드 로직 (추가됨)
    first_aid_guide = ""
    if "골절" in selected_symptom:
        first_aid_guide = "<b>1. 지혈 및 고정:</b> 출혈이 있다면 깨끗한 천으로 압박하세요.<br><b>2. 움직임 최소화:</b> 부러진 뼈를 억지로 맞추려 하지 말고, 부목이나 두꺼운 잡지 등으로 다친 부위를 고정한 상태로 이동하세요."
    elif "흉통" in selected_symptom:
        first_aid_guide = "<b>1. 호흡 확보:</b> 환자를 편안한 곳에 눕히고 넥타이나 벨트, 단추를 풀어 호흡을 편하게 해 주세요.<br><b>2. 심폐소생술 준비:</b> 환자의 의식이 없고 호흡이 불규칙하다면 즉시 119에 신고 후 가슴 압박을 시작하세요."
    elif "소아 39도" in selected_symptom:
        first_aid_guide = f"<b>1. 체온 조절:</b> 미지근한 물을 적신 수건으로 <b>{age}</b>의 이마와 목, 겨드랑이를 가볍게 닦아주세요.<br><b>2. 해열제:</b> 아세트아미노펜 계열 해열제를 먼저 먹이고, 열이 안 떨어지면 교차 복용을 준비해 병원으로 이동하세요."
    else:
        first_aid_guide = "<b>1. 수분 섭취:</b> 탈수 방지를 위해 미지근한 물을 자주 마시게 하세요.<br><b>2. 경과 관찰:</b> 당장 응급실에 가기보다 안정을 취하며 인근 의원 방문을 권장합니다."

    st.markdown(f"""
    <div class="first-aid-box">
        <h4 style="margin: 0 0 10px 0; color: #991B1B;">🚨 즉각적인 응급처치 가이드</h4>
        <p style="margin: 0; font-size: 0.9rem; color: #7F1D1D; line-height: 1.6;">{first_aid_guide}</p>
    </div>
    """, unsafe_allow_html=True)


with col_right:
    st.subheader(f"🏥 응급실 가용 병상 조회 (총 {len(FACILITY_DB)}건)")
    st.caption("가용병상수/전체병상수, *대기환자")
    
    # 1. 최우선 추천 병원
    dept_tags = "".join([f'<span class="dept-tag">{d}</span>' for d in best_hospital["departments"]])
    map_url = f"https://map.kakao.com/link/to/{best_hospital['name']},{best_hospital['lat']},{best_hospital['lng']}"
    
    best_card = textwrap.dedent(f"""
        <div class="best-hospital-card">
            <div class="recommend-reason">
                💡 <b>AI 최적 추천:</b> 현재 위치에서 {best_hospital['distance_km']}km로 가장 가깝고, 일반 응급 병상이 '{best_hospital['status']}' 상태여서 신속한 진료가 가능할 확률이 높습니다.
            </div>
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                <span style="background-color: #DC2626; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; margin-right: 6px;">{best_hospital['type']}</span>
                <h3 style="margin: 0; color: #0F172A; font-size: 1.2rem;">{best_hospital['name']}</h3>
            </div>
            
            <div style="margin: 8px 0;">{dept_tags}</div>
            
            <div class="bed-grid">
                <div><span style="color: #64748B;">응급실일반</span><br><b style="color: {'#16A34A' if best_hospital['status']=='원활' else '#DC2626'};">{best_hospital['gen_curr']}/{best_hospital['gen_total']}</b><br><span style="font-size:0.7rem;">({best_hospital['status']})</span></div>
                <div><span style="color: #64748B;">응급실소아</span><br><b>{best_hospital['ped_curr']}/{best_hospital['ped_total']}</b><br><span style="font-size:0.7rem;">({best_hospital['ped_status']})</span></div>
                <div><span style="color: #64748B;">분만실</span><br><b style="color: #059669;">{best_hospital['mat_status']}</b></div>
            </div>
            
            <div style="margin-top: 12px;">
                <a href="{map_url}" target="_blank" class="btn-action btn-kakao">📍 <b>길찾기</b></a>
                <a href="tel:{best_hospital['phone']}" class="btn-action btn-call">📞 {best_hospital['phone']}</a>
            </div>
        </div>
    """).strip()
    st.markdown(best_card, unsafe_allow_html=True)

    # 2. 나머지 전체 병원 목록
    for h in other_hospitals:
        tags = "".join([f'<span class="dept-tag">{d}</span>' for d in h["departments"]]) if h["departments"] else "<span style='font-size:0.8rem; color:#94A3B8;'>세부 진료과 정보 없음</span>"
        h_map = f"https://map.kakao.com/link/to/{h['name']},{h['lat']},{h['lng']}"
        gen_color = "#DC2626" if h["status"] == "혼잡" else "#16A34A" if h["status"] == "원활" else "#D97706"
        
        card_html = textwrap.dedent(f"""
            <div class="hospital-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <div style="display: flex; align-items: center;">
                        <span style="background-color: #64748B; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; margin-right: 6px;">{h['type']}</span>
                        <h4 style="margin: 0; color: #334155; font-size: 1.05rem;">{h['name']}</h4>
                    </div>
                    <a href="{h_map}" target="_blank" style="font-size: 0.8rem; color: #2563EB; text-decoration: none; font-weight: bold;">길찾기 ></a>
                </div>
                
                <div style="margin: 8px 0;">{tags}</div>
                
                <div class="bed-grid" style="background-color: transparent; padding: 0;">
                    <div><span style="color: #64748B;">응급실일반</span><br><b style="color: {gen_color};">{h['gen_curr']}/{h['gen_total']}</b><br><span style="font-size:0.7rem;">({h['status']})</span></div>
                    <div><span style="color: #64748B;">응급실소아</span><br><b>{h['ped_curr']}/{h['ped_total']}</b><br><span style="font-size:0.7rem;">({h['ped_status']})</span></div>
                    <div><span style="color: #64748B;">분만실</span><br><b style="color: #059669;">{h['mat_status']}</b></div>
                </div>
            </div>
        """).strip()
        st.markdown(card_html, unsafe_allow_html=True)
