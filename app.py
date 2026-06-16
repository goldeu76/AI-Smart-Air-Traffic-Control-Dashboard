import datetime
import math
import ssl
import json
import urllib.parse
import urllib.request
import streamlit as st
import pandas as pd
import pydeck as pdk

# Streamlit 페이지 기본 설정 (와이드 모드 및 타이틀 설정)
st.set_page_config(page_title="AI 스마트 항공 관제탑 대시보드", layout="wide")

# ---------------------------------------------------------------------------
# [사용자 설정] OpenSky Network OAuth2 API 자격 증명 정보 입력
# ---------------------------------------------------------------------------
CLIENT_ID = "parkminjun123-api-client"
CLIENT_SECRET = "A9WVkrstiZvxquEIlCI6GoTHLw8q7L28"

# ---------------------------------------------------------------------------
# [상수 설정] API 엔드포인트 및 대한민국 영공 범위 설정
# ---------------------------------------------------------------------------
TOKEN_URL = "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"
STATES_URL = "https://opensky-network.org/api/states/all"

LAMIN, LAMAX = 33.0, 39.0
LOMIN, LOMAX = 124.0, 132.0

# ---------------------------------------------------------------------------
# [백엔드 데이터 로직 함수]
# ---------------------------------------------------------------------------
@st.cache_data(ttl=15)
def get_access_token(client_id, client_secret):
    """OAuth2 Client Credentials Flow를 통해 Access Token을 발급받습니다."""
    try:
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        }
        encoded_data = urllib.parse.urlencode(data).encode("utf-8")
        req = urllib.request.Request(TOKEN_URL, data=encoded_data)
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(req, context=context) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            return res_data.get("access_token"), "성공"
    except Exception as e:
        return None, f"실패 ({str(e)})"

@st.cache_data(ttl=10)
def fetch_korea_flights(token):
    """지정한 대한민국 경위도 범위 내의 실시간 항공기 데이터를 가져옵니다."""
    if not token:
        return None
    try:
        params = {"lamin": LAMIN, "lamax": LAMAX, "lomin": LOMIN, "lomax": LOMAX}
        url_parts = urllib.parse.urlencode(params)
        full_url = f"{STATES_URL}?{url_parts}"
        req = urllib.request.Request(full_url)
        req.add_header("Authorization", f"Bearer {token}")
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(req, context=context) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        return None

def calculate_stats(vertical_rates):
    """순수 파이썬으로 평균과 표준편차를 계산합니다."""
    n = len(vertical_rates)
    if n < 2:
        return 0.0, 1.0
    mean = sum(vertical_rates) / n
    variance = sum((x - mean) ** 2 for x in vertical_rates) / n
    std_dev = math.sqrt(variance)
    if std_dev == 0:
        std_dev = 0.001
    return mean, std_dev

# ---------------------------------------------------------------------------
# [UI 및 메인 로직 시작]
# ---------------------------------------------------------------------------
st.title("🛰️ AI 스마트 항공 관제탑 대시보드 시스템")
st.markdown("본 시스템은 대한민국 영공 내 실시간 비행 데이터를 수집하여 통계적 이상 징후를 판별하는 관제 레이더 솔루션입니다.")

# 1. 좌측 사이드바 (Sidebar) 구현
st.sidebar.header("🛠️ 시스템 설정 및 관제")

# API 인증 상태 표시
token, auth_status = get_access_token(CLIENT_ID, CLIENT_SECRET)
is_authenticated = token is not None
st.sidebar.checkbox("🔒 OpenSky API 인증 상태", value=is_authenticated, disabled=True)
if is_authenticated:
    st.sidebar.success(f"🟢 API 연결 상태: {auth_status}")
else:
    st.sidebar.error(f"🔴 API 인증 실패: {auth_status}")

st.sidebar.markdown("---")

# 검색 범위 설정
st.sidebar.subheader("📍 검색 범위 설정")
region_option = st.sidebar.selectbox("지역 검색 필터", ["나가서", "대한민국 전체", "인천 FIR"])
st.sidebar.info(f"**📡 모니터링 경위도 경계 영역**\n- 위도(LAT): {LAMIN} ~ {LAMAX}\n- 경도(LON): {LOMIN} ~ {LOMAX}")

st.sidebar.markdown("---")

# 관제 세부설정
st.sidebar.subheader("🎛️ 관제 세부 설정")
auto_refresh_interval = st.sidebar.selectbox("자동 갱신 및 복구 주기", ["30초", "1분", "5분"], index=0)
z_score_threshold = st.sidebar.slider("🚨 위험 판단 기준 Z-점수", min_value=-5.00, max_value=-1.00, value=-3.00, step=0.25)

st.sidebar.markdown(" ")
if st.sidebar.button("🔄 즉각적으로 데이터 동시성 갱신", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# ---------------------------------------------------------------------------
# 데이터 가공 및 통계 처리
# ---------------------------------------------------------------------------
flight_data = fetch_korea_flights(token)
raw_states = flight_data.get("states") if flight_data else None

total_received = 0
analysis_target = 0
danger_count = 0
df = pd.DataFrame()

if raw_states:
    total_received = len(raw_states)
    
    # 유효한 수직 속도가 있는 기체 필터링 및 통계 계산
    valid_rates = [state[11] for state in raw_states if state[11] is not None]
    mean_vr, std_vr = calculate_stats(valid_rates)
    
    processed_data = []
    for idx, state in enumerate(raw_states):
        lon = state[5]
        lat = state[6]
        v_rate = state[11]
        
        if lat is None or lon is None:
            continue
            
        analysis_target += 1
        
        # Z-score 산출 및 위험 판단
        z_score = round((v_rate - mean_vr) / std_vr, 2) if v_rate is not None else 0.0
        
        is_danger = "정상"
        color = [0, 150, 255, 200]  # 네온 블루
        
        if v_rate is not None and v_rate < 0 and z_score <= z_score_threshold:
            is_danger = "위험 (급강하)"
            danger_count += 1
            color = [255, 30, 30, 240]  # 형광 레드
            
        processed_data.append({
            "number": idx + 1,
            "icao24": str(state[0]).strip(),
            "callsign": str(state[1]).strip() if state[1] else "UNKNOWN",
            "status": is_danger,
            "origin_country": str(state[2]).strip(),
            "longitude": float(lon),
            "latitude": float(lat),
            "vertical_rate": float(v_rate) if v_rate is not None else 0.0,
            "z_score": float(z_score),
            "baro_altitude": float(state[7]) * 3.28084 if state[7] is not None else 0.0,  # ft 환산
            "velocity_kts": float(state[9]) * 1.94384 if state[9] is not None else 0.0,   # kts 환산
            "color": color
        })
        
    df = pd.DataFrame(processed_data)

# 2. 메인 화면 상단 종합 지표 레이아웃 배치
st.markdown("### 📊 실시간 주요 관제 지표")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("전체 수신 항공기", f"{total_received} 대")
with col2:
    st.metric("🎯 분석대상 항공기", f"{analysis_target} 대")
with col3:
    st.metric("🚨 위험 탐지 기체", f"{danger_count} 대", delta=f"기준: {z_score_threshold}", delta_color="inverse")
with col4:
    st.metric("🗺️ 선택된 지역 범위", region_option)
with col5:
    st.metric("⏳ 시스템 갱신 주기", auto_refresh_interval)

st.caption(f"✨ **시스템 실시간 갱신 시각:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (Z-Score 임계값: {z_score_threshold})")
st.markdown("---")

# 3. 메인 레이아웃 (지도 앤 실시간 알림 종형 통합 구조)
st.subheader("🌐 실시간 영공 레이더망 (Pydeck Map)")

# 고정된 지도 중심 좌표 (대한민국 중심부 와이드 뷰 고정)
map_lat, map_lon, map_zoom = 36.1, 127.7, 6.8
view_state = pdk.ViewState(latitude=map_lat, longitude=map_lon, zoom=map_zoom, pitch=0)

if not df.empty:
    layer = pdk.Layer(
        "ScatterplotLayer",
        df,
        id="aircraft-radar-layer", 
        pickable=True,          # 커서 올려놓을 때 반응하는 툴팁 기능을 위해 활성화
        auto_highlight=True,    
        opacity=0.88,
        stroked=True,
        filled=True,
        radius_scale=1,
        radius_min_pixels=6,     
        radius_max_pixels=15,
        line_width_min_pixels=1,
        get_position="[longitude, latitude]",
        get_fill_color="color",
        get_line_color=[255, 255, 255, 250]
    )
    
    # 🎯 에러를 유발하던 on_select 이벤트와 key 인자, 우측 정보창 칼럼 레이아웃을 100% 제거
    st.pydeck_chart(
        pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
            tooltip={
                "html": "<b>편명:</b> {callsign}<br/>"
                        "<b>고도:</b> {baro_altitude:.0f} ft<br/>"
                        "<b>속도:</b> {velocity_kts:.1f} kts<br/>"
                        "<b>수직속도:</b> {vertical_rate:.1f} m/s<br/>"
                        "<b>Z-Score:</b> {z_score}",
                "style": {"backgroundColor": "#1e293b", "color": "white", "fontFamily": "Arial"}
            }
        )
    )
else:
    st.info("현재 분석 범위 내에 활성화된 항공기 트래픽 좌표 데이터가 존재하지 않습니다.")
    st.pydeck_chart(pdk.Deck(
        initial_view_state=view_state, 
        map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
    ))

st.markdown("---")

# 4. 실시간 긴급 위험 기체 모니터링 경보 피드
st.subheader("🚨 위험 징후 기체 실시간 모니터링")
if not df.empty and (df["status"] == "위험 (급강하)").any():
    danger_list = df[df["status"] == "위험 (급강하)"]
    st.error(f"⚠️ **비상 경보! 현재 위기 임계값(Z-Score {z_score_threshold})을 초과하여 이상 급강하 중인 기체가 {len(danger_list)}대 감지되었습니다.**")
    
    # 가독성을 높이기 위해 위험 기체 정보 일렬 배치
    danger_cols = st.columns(min(len(danger_list), 4))
    for i, (_, row) in enumerate(danger_list.iterrows()):
        with danger_cols[i % 4]:
            st.markdown(
                f"<div style='background-color: #7f1d1d; padding: 12px; border-radius: 6px; border: 1px solid #f87171; color: #fee2e2;'>"
                f"✈️ <b>편명: {row['callsign']}</b><br>"
                f"• 통계 Z-Score: <code style='color:#fca5a5;'>{row['z_score']}</code><br>"
                f"• 실시간 하강률: <code>{row['vertical_rate']:.1f} m/s</code><br>"
                f"• 현재 고도: {row['baro_altitude']:,.0f} ft"
                f"</div>", 
                unsafe_allow_html=True
            )
else:
    st.success("✅ **현재 대한민국 영공 내에 통계적 위험 범주(이상 하강 및 이상 기동)에 속하는 이상 징후 기체가 없습니다. 정상 상태 유지 중.**")

st.markdown("---")

# 5. 하단 통합 테이블 관제 뷰
st.subheader("📋 전체 항공기 실시간 관제 데이터 테이블")
if not df.empty:
    output_cols = ["number", "callsign", "status", "origin_country", "vertical_rate", "z_score", "baro_altitude", "velocity_kts", "latitude", "longitude"]
    st.dataframe(df[output_cols], width=1600, hide_index=True)
else:
    st.warning("표시할 수 있는 통합 데이터 시트가 존재하지 않습니다.")