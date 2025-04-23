import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import json
import os
import ssl

ssl._create_default_https_context = ssl._create_unverified_context
FAVORITES_FILE = "favorites.json"

def load_favorites():
    if os.path.exists(FAVORITES_FILE):
        with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_favorites(favorites):
    with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
        json.dump(favorites, f, ensure_ascii=False, indent=2)

def get_stock_name(ticker):
    try:
        return yf.Ticker(ticker).info.get("shortName", "Unknown")
    except:
        return "Unknown"

st.set_page_config(page_title="벨포트의 즐겨찾기 대시보드", layout="wide")
st.title("⭐ 벨포트의 종목 즐겨찾기 + RSI 조건 필터링")

favorites = load_favorites()

# 종목 추가
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

st.divider()
st.subheader("📊 RSI 조건 필터링")

# 👉 사용자 설정
rsi_period = st.slider("RSI 계산 기준일 (기간)", min_value=1, max_value=30, value=14)
rsi_range = st.slider("RSI 값 범위", min_value=0, max_value=100, value=(0, 30))
st.write(f"📌 조건: RSI({rsi_period}) 값이 {rsi_range[0]} ~ {rsi_range[1]} 사이")

results = []

for ticker in favorites:
    try:
        df = yf.download(ticker, period="30d", interval="1d")
        if df.empty:
            st.warning(f"{ticker}: 데이터 없음")
            continue

        close = df['Close']
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]

        rsi = ta.momentum.RSIIndicator(close, window=rsi_period).rsi()
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
