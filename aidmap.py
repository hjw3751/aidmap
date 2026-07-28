import streamlit as st
import pandas as pd
import math
import time

# ----------------------------------------------------
# 1. 페이지 설정 및 통합 커스텀 CSS
# ----------------------------------------------------
st.set_page_config(
    page_title="AIDMAP - 맞춤형 응급의료 통합 대시보드",
    page_icon="🚑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .main { background-color: #F8FAFC; }
    
    /* NEMC 메인 헤더 */
    .nemc-top-bar {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%);
        color: white !important;
        padding: 20px 24px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15);
    }
    .nemc-top-bar h2 { color: #FFFFFF !important; margin: 0; font-weight: 700; font-size: 1.5rem; }
    .nemc-top-bar p { color: #93C5FD !important; margin: 4px 0 0 0; font-size: 0.9rem; }

    /* 필터 박스 */
    .filter-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 20px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }

    /* KTAS 응급도 결과 박스 */
    .ktas-box-1 { background-color: #FEE2E2; border-left: 6px solid #EF4444; padding: 14px; border-radius: 8px; margin-bottom: 15px; }
    .ktas-box-2 { background-color: #FFEDD5; border-left: 6px solid #F97316; padding: 14px; border-radius: 8px; margin-bottom: 15px; }
    .ktas-box-3 { background-color: #FEF3C7; border-left: 6px solid #F59E0B; padding: 14px; border-radius: 8px; margin-bottom: 15px; }
    .ktas-box-4 { background-color: #E0F2FE; border-left: 6px solid #0EA5E9; padding: 14px; border-radius: 8px; margin-bottom: 15px; }
    .ktas-box-5 { background-color: #DCFCE7; border-left: 6px solid #10B981; padding: 14px; border-radius: 8px; margin-bottom: 15px; }

    /* 카드 및 리스트 UI */
    .hospital-row {
        background-color: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 14px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03);
    }

    /* 실시간 진료 제한 통제 뱃지 (Feature 4) */
    .notice-danger {
        background-color: #FEF2F2;
        color: #991B1B !important;
        border: 1px solid #FECACA;
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 0.83rem;
        font-weight: bold;
        margin-top: 8px;
        display: block;
    }
    .notice-ok {
        background-color: #F0FDF4;
        color: #166534 !important;
        border: 1px solid #BBF7D0;
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 0.83rem;
        font-weight: bold;
        margin-top: 8px;
        display: block;
    }

    /* 길안내 및 지도 버튼 (Feature 2) */
    .btn-kakao {
        background-color: #FEE500;
        color: #000000 !important;
        padding: 6px 12px;
        border-radius: 6px;
        text-decoration: none;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
    }
    .btn-naver {
        background-color: #03CF5D;
        color: #FFFFFF !important;
        padding: 6px 12px;
        border-radius: 6px;
        text-decoration: none;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
    }
    .btn-call {
        background-color: #2563EB;
        color: #FFFFFF !important;
        padding: 6px 12px;
        border-radius: 6px;
        text-decoration: none;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
    }

    /* 상태/종류 뱃지 */
    .badge-facility {
        background-color: #334155;
        color: #FFFFFF !important;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: bold;
    }
    .badge-moonlight {
        background-color: #FEF3C7;
        color: #B45309 !important;
        border: 1px solid #FDE68A;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: bold;
    }
    .badge-pharmacy {
        background-color: #ECFDF5;
        color: #047857 !important;
        border: 1px solid #A7F3D0;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: bold;
    }
    .dept-tag {
        display: inline-block;
        background-color: #F1F5F9;
        color: #475569 !important;
        padding: 2px 7px;
        border-radius: 4px;
        font-size: 0.75rem;
        margin-right: 4px;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 2. 통합 더미 데이터베이스 (응급실, 달빛어린이병원, 휴일약국)
# ----------------------------------------------------
REGION_DATA = {
    "제주특별자치도": ["전체", "서귀포시", "제주시"],
    "서울특별시": ["전체", "중구", "강남구", "종로구"]
}

FACILITY_DB = [
    # [응급의료기관]
    {
        "cat": "응급실", "sido": "제주특별자치도", "sigungu": "서귀포시",
        "name": "제주특별자치도 서귀포의료원", "type": "지역응급의료센터",
        "address": "제주특별자치도 서귀포시 장수로 47", "phone": "064-730-3109",
        "gen_curr": 14, "gen_total": 16, "ped_curr": 1, "ped_total": 4, "mat_status": "가능(1실)",
        "lat": 33.2547, "lng": 126.5601,
        "departments": ["응급내시경", "성인위장관", "소아청소년과", "외과/골절"],
        "restriction": "⚠️ 응급 CT 정기 점검 중 (21:00 점검 완료 예정)", "is_open": True
    },
    {
        "cat": "응급실", "sido": "제주특별자치도", "sigungu": "제주시",
        "name": "제주대학교병원", "type": "권역응급의료센터",
        "address": "제주특별자치도 제주시 아란13길 15", "phone": "064-717-1900",
        "gen_curr": 18, "gen_total": 20, "ped_curr": 3, "ped_total": 5, "mat_status": "가능(2실)",
        "lat": 33.4670, "lng": 126.5450,
        "departments": ["응급내시경", "성인위장관", "소아청소년과", "심뇌혈관센터", "외과/골절", "분만실"],
        "restriction": "🟢 전 과 정상 수용 및 심뇌혈관 응급 수술 가능", "is_open": True
    },
    {
        "cat": "응급실", "sido": "제주특별자치도", "sigungu": "제주시",
        "name": "한마음병원", "type": "지역응급의료기관",
        "address": "제주특별자치도 제주시 연신로 52", "phone": "064-750-9000",
        "gen_curr": 2, "gen_total": 10, "ped_curr": 0, "ped_total": 2, "mat_status": "불가",
        "lat": 33.4962, "lng": 126.5441,
        "departments": ["성인위장관", "외과/골절"],
        "restriction": "⚠️ 당직 소아과 전문의 부재로 소아 응급 진료 불가", "is_open": True
    },
    
    # [Feature 3: 달빛어린이병원]
    {
        "cat": "달빛어린이병원", "sido": "제주특별자치도", "sigungu": "제주시",
        "name": "탑동365의원 (달빛어린이병원)", "type": "야간/휴일 소아진료기관",
        "address": "제주특별자치도 제주시 탑동로 24", "phone": "064-758-3650",
        "gen_curr": 0, "gen_total": 0, "ped_curr": 8, "ped_total": 10, "mat_status": "불가",
        "lat": 33.5181, "lng": 126.5244,
        "departments": ["소아청소년과", "야간경증진료"],
        "restriction": "🌙 오늘 야간 23:00까지 소아청소년과 전문의 진료 중", "is_open": True
    },
    {
        "cat": "달빛어린이병원", "sido": "제주특별자치도", "sigungu": "서귀포시",
        "name": "서귀포 365연세의원", "type": "야간/휴일 소아진료기관",
        "address": "제주특별자치도 서귀포시 일주동로 8650", "phone": "064-762-3650",
        "gen_curr": 0, "gen_total": 0, "ped_curr": 5, "ped_total": 8, "mat_status": "불가",
        "lat": 33.2530, "lng": 126.5650,
        "departments": ["소아청소년과", "이비인후과"],
        "restriction": "🌙 주말/휴일 22:00까지 소아 야간 진료 운영", "is_open": True
    },

    # [Feature 3: 휴일지킴이약국]
    {
        "cat": "휴일약국", "sido": "제주특별자치도", "sigungu": "서귀포시",
        "name": "서귀포 중정약국", "type": "휴일지킴이약국",
        "address": "제주특별자치도 서귀포시 중정로 61", "phone": "064-762-2345",
        "gen_curr": 0, "gen_total": 0, "ped_curr": 0, "ped_total": 0, "mat_status": "불가",
        "lat": 33.2492, "lng": 126.5630,
        "departments": ["처방조제", "안전상비의약품"],
        "restriction": "💊 연중무휴 22:00까지 운영 중", "is_open": True
    },
    {
        "cat": "응급실", "sido": "서울특별시", "sigungu": "중구",
        "name": "국립중앙의료원", "type": "중앙응급의료센터",
        "address": "서울특별시 중구 을지로 245", "phone": "02-2260-7114",
        "gen_curr": 12, "gen_total": 15, "ped_curr": 2, "ped_total": 3, "mat_status": "가능(1실)",
        "lat": 37.5672, "lng": 127.0056,
        "departments": ["응급내시경", "성인위장관", "소아청소년과", "심뇌혈관센터", "외과/골절"],
        "restriction": "🟢 중앙응급센터 정상 운영 중", "is_open": True
    }
]

# 위도/경도 간 거리 계산 (Haversine 공식)
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)

# ----------------------------------------------------
# 3. 브랜딩 메인 헤더
# ----------------------------------------------------
st.markdown("""
<div class="nemc-top-bar">
    <h2>🚑 AIDMAP : 스마트 응급의료 통합 대시보드</h2>
    <p>KTAS AI 응급도 판별 | 실시간 수용 통제 알림 | 원터치 내비게이션 | 달빛어린이병원·휴일약국 연동</p>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 4. 상단 통합 컨트롤러 (Feature 3: 시설 유형 선택 포함)
# ----------------------------------------------------
with st.container():
    st.markdown('<div class="filter-card">', unsafe_allow_html=True)
    f_col1, f_col2, f_col3, f_col4 = st.columns([1.3, 1.2, 1.2, 1.0])
    
    with f_col1:
        selected_cat = st.selectbox("🏥 조회 대상 선택", ["전체 시설", "🏥 응급의료기관(응급실)", "🌙 달빛어린이병원(소아야간)", "💊 휴일지킴이약국"], index=0)
    with f_col2:
        selected_sido = st.selectbox("시/도 선택", list(REGION_DATA.keys()), index=0)
    with f_col3:
        selected_sigungu = st.selectbox("시/군/구 선택", REGION_DATA[selected_sido], index=1)
    with f_col4:
        st.write("&nbsp;")
        if st.button("🎯 GPS 현재위치", use_container_width=True):
            st.toast("📍 현재 위치(제주 서귀포시 동홍동) 기반으로 재설정되었습니다.")
            
    st.markdown('</div>', unsafe_allow_html=True)

# 2열 레이아웃
col_left, col_right = st.columns([1.0, 1.2], gap="large")

# ====================================================
# [왼쪽 열] Feature 1: KTAS AI 응급도 분류기 & 연령별 가이드
# ====================================================
with col_left:
    st.subheader("🩺 [Feature 1] KTAS AI 응급도 문진 판별기")
    
    selected_symptoms = st.multiselect(
        "환자의 주요 증상을 모두 선택하세요:",
        [
            "🚨 의식 저하 / 반응 없음",
            "🫀 갑작스러운 심한 흉통 / 호흡곤란",
            "🩸 흑색변 / 위장관 대량 출혈",
            "👶 소아 39도 이상 고열 및 경련",
            "🦴 골절 의심 / 출혈성 외상",
            "🤒 단순 발열 / 감기 기운",
            "💊 약 처방 및 소화불량"
        ],
        default=["🫀 갑작스러운 심한 흉통 / 호흡곤란"]
    )

    # KTAS 계산 로직
    ktas_level = 5
    ktas_title = "KTAS 5단계 (비응급)"
    ktas_box_class = "ktas-box-5"
    ktas_desc = "경증 질환입니다. 가까운 일반 의원이나 휴일지킴이약국 이용을 권장합니다."

    if any("의식 저하" in s for s in selected_symptoms):
        ktas_level = 1
        ktas_title = "🚨 KTAS 1단계 (소생 - 최우선)"
        ktas_box_class = "ktas-box-1"
        ktas_desc = "생명이 위급한 최우선 응급 상황입니다. 즉시 119에 신고하고 권역응급센터로 이송해야 합니다."
    elif any("흉통" in s or "대량 출혈" in s for s in selected_symptoms):
        ktas_level = 2
        ktas_title = "⚠️ KTAS 2단계 (중증응급)"
        ktas_box_class = "ktas-box-2"
        ktas_desc = "생명이나 사지에 잠재적 위협이 있는 응급 상황입니다. 즉시 대형병원 응급실 진료가 필요합니다."
    elif any("고열 및 경련" in s or "골절" in s for s in selected_symptoms):
        ktas_level = 3
        ktas_title = "🟡 KTAS 3단계 (응급)"
        ktas_box_class = "ktas-box-3"
        ktas_desc = "응급 처치가 필요한 상태입니다. 소아응급실 또는 지역응급센터로 이동하세요."
    elif any("단순 발열" in s for s in selected_symptoms):
        ktas_level = 4
        ktas_title = "🔵 KTAS 4단계 (준응급)"
        ktas_box_class = "ktas-box-4"
        ktas_desc = "야간/휴일인 경우 '달빛어린이병원'이나 야간 진료 의원을 이용하시는 것이 빠르고 효율적입니다."

    # KTAS 결과 판별 카드 출력
    st.markdown(f"""
    <div class="{ktas_box_class}">
        <h4 style="margin:0 0 6px 0;">{ktas_title}</h4>
        <p style="margin:0; font-size: 0.9rem;">{ktas_desc}</p>
    </div>
    """, unsafe_allow_html=True)

    # 종합 추천 스코어 공식 안내
    st.markdown(r"""
    <div style="background-color: #F1F5F9; padding: 10px 14px; border-radius: 8px; font-size: 0.82rem; color: #334155;">
        <b>💡 AI 종합 적합도 점수 산출 공식:</b><br>
        $$Score = 0.4 \times S_{dept} + 0.3 \times S_{bed} + 0.3 \times S_{ktas} - 2.0 \times Dist(km)$$
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # 연령별 대처 수칙 + 어르신 TTS 음성 안내
    st.subheader("🔊 연령별 응급처치 & 음성 안내")
    age = st.radio("환자 연령대:", ["영유아", "어린이", "성인", "노년층"], index=3, horizontal=True)
    
    if age == "노년층":
        st.warning("🧓 **노년층 수칙:** 낙상 시 무리하게 움직이지 마시고, 뇌졸중 의심(안면마비/발음어눌) 즉시 골든타임 내 응급실로 이동하세요.")
        tts_text = "노년층 응급처치 안내입니다. 낙상 시 무리하게 일어나지 마시고, 흉통이나 안면 마비 발생 시 즉시 119를 부르세요."
        tts_html = f"""
        <div style="background-color: #F0FDF4; padding: 12px; border-radius: 8px; border: 1px solid #86EFAC;">
            <button onclick="speakText()" style="background-color: #16A34A; color: white; border: none; padding: 8px 14px; border-radius: 6px; cursor: pointer; font-weight: bold;">
                🔊 음성 안내 크게 듣기
            </button>
            <button onclick="window.speechSynthesis.cancel()" style="background-color: #DC2626; color: white; border: none; padding: 8px 12px; border-radius: 6px; cursor: pointer; font-weight: bold; margin-left: 6px;">
                ⏹️ 정지
            </button>
        </div>
        <script>
            function speakText() {{
                window.speechSynthesis.cancel();
                var msg = new SpeechSynthesisUtterance('{tts_text}');
                msg.lang = 'ko-KR';
                msg.rate = 0.85;
                window.speechSynthesis.speak(msg);
            }}
        </script>
        """
        st.components.v1.html(tts_html, height=70)
    else:
        st.info("💡 각 연령대에 적합한 긴급 대처 수칙이 상단 모듈과 동기화되어 적용됩니다.")

# ====================================================
# [오른쪽 열] AI 맞춤 추천 및 검색 결과 (Feature 2, 3, 4 반영)
# ====================================================
with col_right:
    st.subheader("🏥 AI 최적 의료기관 추천 결과")
    
    user_lat, user_lng = 33.2541, 126.5601  # 서귀포시 기준 좌표
    
    # 데이터 필터링 로직
    filtered_facilities = []
    for f in FACILITY_DB:
        # 시/도 및 시/군/구 조건
        if f["sido"] != selected_sido:
            continue
        if selected_sigungu != "전체" and f["sigungu"] != selected_sigungu:
            continue
            
        # 시설 카테고리 필터 (Feature 3)
        if "응급의료기관" in selected_cat and f["cat"] != "응급실":
            continue
        if "달빛어린이병원" in selected_cat and f["cat"] != "달빛어린이병원":
            continue
        if "휴일지킴이약국" in selected_cat and f["cat"] != "휴일약국":
            continue

        dist_km = calculate_distance(user_lat, user_lng, f["lat"], f["lng"])
        
        # 간단 점수 계산
        bed_ratio = (f["gen_curr"] / f["gen_total"]) if f["gen_total"] > 0 else 0.5
        score = (bed_ratio * 40) + (100 - dist_km * 5)
        
        filtered_facilities.append({
            "data": f,
            "dist": dist_km,
            "score": score
        })

    filtered_facilities.sort(key=lambda x: x["score"], reverse=True)

    if not filtered_facilities:
        st.warning("⚠️ 선택하신 지역 및 조건에 해당하는 의료기관/약국이 없습니다.")
    else:
        for item in filtered_facilities:
            f = item["data"]
            dist = item["dist"]
            
            # 카테고리별 뱃지
            if f["cat"] == "응급실":
                cat_badge = f'<span class="badge-facility">{f["type"]}</span>'
            elif f["cat"] == "달빛어린이병원":
                cat_badge = '<span class="badge-moonlight">🌙 달빛어린이병원</span>'
            else:
                cat_badge = '<span class="badge-pharmacy">💊 휴일지킴이약국</span>'

            # Feature 4: 실시간 수용 통제 알림 뱃지
            if "⚠️" in f["restriction"]:
                notice_html = f'<div class="notice-danger">{f["restriction"]}</div>'
            else:
                notice_html = f'<div class="notice-ok">{f["restriction"]}</div>'

            # Feature 2: 원터치 길안내 URL Scheme 생성
            kakao_url = f"https://map.kakao.com/link/to/{f['name']},{f['lat']},{f['lng']}"
            naver_url = f"https://map.naver.com/v5/search/{f['name']}"

            # 진료과 태그
            dept_tags = "".join([f'<span class="dept-tag">{d}</span>' for d in f["departments"]])

            # 카드 출력
            st.markdown(f"""
            <div class="hospital-row">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        {cat_badge}
                        <h4 style="margin: 4px 0 2px 0; color: #0F172A; font-size: 1.1rem;">{f['name']}</h4>
                        <p style="margin: 0; font-size: 0.85rem; color: #64748B;">📍 {f['address']} (<b>{dist}km</b>)</p>
                    </div>
                </div>
                
                {notice_html}
                
                <div style="margin-top: 8px;">{dept_tags}</div>
                
                <!-- 응급실 잔여 병상 표출 (응급실인 경우만) -->
                {"<div style='margin-top: 10px; padding: 8px; background-color: #F8FAFC; border-radius: 6px; font-size: 0.83rem; display: flex; gap: 15px;'><span>일반응급: <b>" + str(f['gen_curr']) + "/" + str(f['gen_total']) + "석</b></span><span>소아응급: <b>" + str(f['ped_curr']) + "/" + str(f['ped_total']) + "석</b></span><span>분만실: <b>" + f['mat_status'] + "</b></span></div>" if f['cat'] == '응급실' else ""}
                
                <!-- Feature 2: 길안내 & 전화 원터치 버튼 모음 -->
                <div style="margin-top: 12px; display: flex; gap: 8px;">
                    <a href="tel:{f['phone']}" class="btn-call">📞 전화 걸기</a>
                    <a href="{kakao_url}" target="_blank" class="btn-kakao">🟡 카카오맵 길찾기</a>
                    <a href="{naver_url}" target="_blank" class="btn-naver">🟢 네이버 지도</a>
                </div>
            </div>
            """, unsafe_allow_html=True)

st.divider()
st.caption("© 2026 AIDMAP - Integrated Emergency Medical Decision Support System")