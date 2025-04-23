import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import json
import os
import ssl

# SSL 인증서 문제 회피 (회사망 대응용)
ssl._create_default_https_context = ssl._create_unverified_context

# 파일 경로
FAVORITES_FILE = "favorites.json"

# 즐겨찾기 불러오기
def load_favorites():
    if os.path.exists(FAVORITES_FILE):
        with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# 즐겨찾기 저장
def save_favorites(favorites):
    with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
        json.dump(favorites, f, ensure_ascii=False, indent=2)

# 기본 설정
st.set_page_config(page_title="즐겨찾기 + RSI 필터링", layout="wide")
st.title("⭐ 즐겨찾기 종목 + RSI 조건 필터링 대시보드")

# 즐겨찾기 불러오기
favorites = load_favorites()

# 사용자 입력
new_code = st.text_input("추가할 종목 코드 입력 (예: AAPL, 005930.KS)")
if st.button("즐겨찾기에 추가"):
    if new_code and new_code not in favorites:
        favorites.append(new_code)
        save_favorites(favorites)
        st.success(f"{new_code} 추가 완료!")
    elif new_code in favorites:
        st.warning(f"{new_code}은 이미 등록되어 있어요.")
    else:
        st.warning("종목 코드를 입력해주세요.")

if st.button("즐겨찾기 초기화"):
    favorites = []
    save_favorites(favorites)
    st.warning("즐겨찾기를 초기화했습니다.")

# 즐겨찾기 표시
if favorites:
    st.subheader("📌 현재 즐겨찾기 종목")
    st.dataframe(pd.DataFrame(favorites, columns=["종목 코드"]))
else:
    st.info("아직 즐겨찾기한 종목이 없어요.")

# RSI 필터링 시작
st.divider()
st.subheader("📊 RSI 조건 필터링 결과")
rsi_limit = st.slider("RSI 값 이하 필터링", min_value=10, max_value=50, value=30, step=5)
st.write(f"📌 조건: RSI(14) < {rsi_limit}")

results = []

for ticker in favorites:
    try:
        df = yf.download(ticker, period="30d", interval="1d")

        if df.empty:
            st.warning(f"{ticker}: 데이터 없음")
            continue

        close = df['Close']
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]  # 첫 번째 열만 가져오기

        rsi = ta.momentum.RSIIndicator(close).rsi()

        if rsi.isna().all():
            st.warning(f"{ticker}: RSI 계산 불가")
            continue

        latest_rsi = round(rsi.iloc[-1], 2)
        st.write(f"{ticker} RSI: {latest_rsi}")

        if latest_rsi < rsi_limit:
            results.append((ticker, latest_rsi))

    except Exception as e:
        st.error(f"{ticker} 처리 중 오류: {e}")

# 결과 출력
if results:
    df_result = pd.DataFrame(results, columns=["종목", "RSI"])
    st.success(f"✅ 조건을 만족한 종목 {len(df_result)}개 발견!")
    st.dataframe(df_result)
else:
    st.warning("📭 조건을 만족한 종목이 없습니다.")
