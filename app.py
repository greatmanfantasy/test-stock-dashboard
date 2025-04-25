import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import json
import os
import ssl
from datetime import datetime, timedelta
from pycoingecko import CoinGeckoAPI
import pytz

# 한국 표준시(KST)로 시간 변환
kst = pytz.timezone('Asia/Seoul')
current_time = datetime.now(kst).strftime("%Y-%m-%d %H:%M:%S")  # KST로 현재 시간 가져오기

# Streamlit에서 스타일 설정 (글씨 크기 줄이기)
st.markdown("""
    <style>
        .main {
            max-width: 90%;
            margin: auto;
        }
        .block-container {
            padding: 1rem;
        }
        h1 {
            font-size: 20px;
        }
        .stMetric {
            font-size: 14px;
        }
    </style>
""", unsafe_allow_html=True)

# 시장 정보를 가져오는 함수
def get_index_data(ticker, interval="1d"):
    try:
        data = yf.download(ticker, period="2d", interval=interval, progress=False)
        if data.empty or len(data) < 2:
            return None, None, None
        latest_close = data['Close'].iloc[-1]  # 가장 최근 값 추출
        previous_close = data['Close'].iloc[-2]  # 이전 값
        change = latest_close - previous_close
        percent_change = (change / previous_close) * 100
        return float(latest_close), float(change), float(percent_change)  # float로 변환하여 반환
    except Exception as e:
        return None, None, None

# 비트코인 시세를 가져오는 함수
def get_bitcoin_price():
    cg = CoinGeckoAPI()
    data = cg.get_price(ids='bitcoin', vs_currencies='usd')
    return data['bitcoin']['usd']  # 비트코인 가격(USD)

# 환율 정보 (KRW/USD)
usd_krw_price, usd_krw_change, usd_krw_percent = get_index_data("KRW=X")
# 공포지수 (VIX)
vix_price, vix_change, vix_percent = get_index_data("^VIX")
# 주요 지수
nasdaq_price, nasdaq_change, nasdaq_percent = get_index_data("^IXIC")
sp500_price, sp500_change, sp500_percent = get_index_data("^GSPC")
kospi_price, kospi_change, kospi_percent = get_index_data("^KS11")
kosdaq_price, kosdaq_change, kosdaq_percent = get_index_data("^KQ11")
# 비트코인 시세 (USDT 기준)
btc_price = get_bitcoin_price()

# Streamlit 앱 상단에 정보 표시
st.markdown(f"### 📊 시장 요약 정보 (업데이트: {current_time})")

# 첫 번째 줄: 환율과 공포지수
col1, col2 = st.columns(2)

with col1:
    if usd_krw_price is not None:
        st.metric(label="🇺🇸 USD/KRW 환율", value=f"{usd_krw_price:,.2f}", delta=f"{usd_krw_change:+.2f} ({usd_krw_percent:+.2f}%)")
    else:
        st.warning("USD/KRW 환율 정보를 가져올 수 없습니다.")
    
with col2:
    if vix_price is not None:
        st.metric(label="😨 공포지수 (VIX)", value=f"{vix_price:,.2f}", delta=f"{vix_change:+.2f} ({vix_percent:+.2f}%)")
    else:
        st.warning("공포지수 정보를 가져올 수 없습니다.")

# 두 번째 줄: S&P 500과 나스닥
col3, col4 = st.columns(2)

with col3:
    if sp500_price is not None:
        st.metric(label="📈 S&P 500", value=f"{sp500_price:,.2f}", delta=f"{sp500_change:+.2f} ({sp500_percent:+.2f}%)")
    else:
        st.warning("S&P 500 정보를 가져올 수 없습니다.")
    
with col4:
    if nasdaq_price is not None:
        st.metric(label="📈 나스닥", value=f"{nasdaq_price:,.2f}", delta=f"{nasdaq_change:+.2f} ({nasdaq_percent:+.2f}%)")
    else:
        st.warning("나스닥 정보를 가져올 수 없습니다.")

# 세 번째 줄: 코스피와 코스닥
col5, col6 = st.columns(2)

with col5:
    if kospi_price is not None:
        st.metric(label="📉 코스피", value=f"{kospi_price:,.2f}", delta=f"{kospi_change:+.2f} ({kospi_percent:+.2f}%)")
    else:
        st.warning("코스피 정보를 가져올 수 없습니다.")
    
with col6:
    if kosdaq_price is not None:
        st.metric(label="📉 코스닥", value=f"{kosdaq_price:,.2f}", delta=f"{kosdaq_change:+.2f} ({kosdaq_percent:+.2f}%)")
    else:
        st.warning("코스닥 정보를 가져올 수 없습니다.")

# 네 번째 줄: 비트코인
col7 = st.columns(1)

with col7[0]:
    if btc_price is not None:
        st.metric(label="💰 비트코인 (BTC/USD)", value=f"{btc_price:,.2f}")
    else:
        st.warning("비트코인 시세 정보를 가져올 수 없습니다.")

# 즐겨찾기 처리
FAVORITES_FILE = "favorites.json"
def load_favorites():
    """즐겨찾기 파일에서 종목 목록 로드"""
    if os.path.exists(FAVORITES_FILE):
        with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_favorites(favorites):
    """즐겨찾기 목록을 파일에 저장"""
    with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
        json.dump(favorites, f, ensure_ascii=False, indent=2)

# 즐겨찾기 기능
favorites = load_favorites()
new_code = st.text_input("➕ 추가할 종목 코드 입력 (예: AAPL, 005930.KS)")
if st.button("추가"):
    if new_code and new_code not in favorites:
        favorites.append(new_code)
        save_favorites(favorites)
        st.success(f"{new_code} 추가 완료!")
    elif new_code in favorites:
        st.warning(f"{new_code}은 이미 등록되어 있어요.")
    else:
        st.warning("종목 코드를 입력해주세요.")

if st.button("🔁 즐겨찾기 초기화"):
    favorites = []
    save_favorites(favorites)
    st.warning("즐겨찾기를 초기화했습니다.")

# 즐겨찾기 테이블
if favorites:
    st.subheader("📌 현재 즐겨찾기 종목")
    display_data = [{"종목 코드": code, "종목명": get_stock_name(code)} for code in favorites]
    st.dataframe(pd.DataFrame(display_data))

    st.download_button(
        label="⬇ 즐겨찾기 다운로드",
        data=json.dumps(favorites, ensure_ascii=False, indent=2),
        file_name="favorites.json",
        mime="application/json"
    )
else:
    st.info("즐겨찾기한 종목이 없습니다.")

# 업로드
uploaded_file = st.file_uploader("📂 즐겨찾기 JSON 업로드", type="json")
if uploaded_file is not None:
    try:
        uploaded_favorites = json.load(uploaded_file)
        if isinstance(uploaded_favorites, list):
            favorites = uploaded_favorites
            save_favorites(favorites)
            st.success("업로드된 즐겨찾기를 성공적으로 불러왔습니다.")
        else:
            st.error("올바른 JSON 형식이 아닙니다.")
    except Exception as e:
        st.error(f"업로드 실패: {e}")

# RSI 필터링 설정
st.divider()
st.subheader("📈 RSI 조건 필터링")

rsi_period = st.slider("RSI 계산 기준일 (기간)", 1, 30, 14)
rsi_range = st.slider("RSI 값 범위", 0, 100, (0, 30))
st.write(f"📌 조건: RSI({rsi_period}) 값이 {rsi_range[0]} ~ {rsi_range[1]} 사이")

results = []

for ticker in favorites:
    try:
        df = yf.download(ticker, period="30d", interval="1d")
        if df.empty:
            st.warning(f"{ticker}: 데이터 없음")
            continue

        rsi = calculate_rsi(df, rsi_period)
        if rsi.isna().all():
            st.warning(f"{ticker}: RSI 계산 불가")
            continue

        latest_rsi = round(rsi.iloc[-1], 2)
        st.write(f"{ticker} RSI: {latest_rsi}")

        if rsi_range[0] <= latest_rsi <= rsi_range[1]:
            results.append((ticker, get_stock_name(ticker), latest_rsi))

    except Exception as e:
        st.error(f"{ticker} 처리 중 오류: {e}")

# 출력
if results:
    df_result = pd.DataFrame(results, columns=["종목 코드", "종목명", "RSI"])
    st.success(f"✅ 조건을 만족한 종목 {len(df_result)}개 발견!")
    st.dataframe(df_result)
else:
    st.warning("📭 조건을 만족한 종목이 없습니다.")
