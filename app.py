import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import json
import os
import ssl

# SSL 인증서 검증 우회 (회사망 등에서 필요)
ssl._create_default_https_context = ssl._create_unverified_context

# 즐겨찾기 파일 경로
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

# Streamlit 설정
st.set_page_config(page_title="즐겨찾기 + RSI 필터링", layout="wide")
st.title("⭐ 즐겨찾기 종목 + RSI 조건 필터링 대시보드")

# 즐겨찾기 불러오기
favorites = load_favorites()

# 즐겨찾기 종목 추가
new_code = st.text_input("➕ 추가할 종목 코드 입력 (예: AAPL, 005930.KS)")
if st.button("추가"):
    if new_code and new_code not in favorites:
        favorites.append(new_code)
        save_favorites(favorites)
        st.success(f"{new_code} 추가 완료!")
    elif new_code in favorites:
        st.warning(f"{new_code}은 이미 추가된 종목입니다.")
    else:
        st.warning("종목 코드를 입력해주세요.")

# 즐겨찾기 초기화
if st.button("🔁 즐겨찾기 초기화"):
    favorites = []
    save_favorites(favorites)
    st.warning("즐겨찾기 목록이 초기화되었습니다.")

# 즐겨찾기 목록 출력
if favorites:
    st.subheader("📌 현재 즐겨찾기 종목")
    st.dataframe(pd.DataFrame(favorites, columns=["종목 코드"]))

    # 다운로드 버튼
    st.download_button(
        label="⬇ 즐겨찾기 다운로드",
        data=json.dumps(favorites, ensure_ascii=False, indent=2),
        file_name="favorites.json",
        mime="application/json"
    )
else:
    st.info("즐겨찾기한 종목이 없습니다.")

# 업로드 기능
uploaded_file = st.file_uploader("📂 즐겨찾기 JSON 업로드", type="json")
if uploaded_file is not None:
    try:
        uploaded_favorites = json.load(uploaded_file)
        if isinstance(uploaded_favorites, list):
            favorites = uploaded_favorites
            save_favorites(favorites)
            st.success("업로드된 즐겨찾기를 성공적으로 불러왔습니다.")
        else:
            st.error("올바른 형식의 JSON 파일이 아닙니다.")
    except Exception as e:
        st.error(f"업로드 실패: {e}")

st.divider()
st.subheader("📊 RSI 조건 필터링")

# RSI 기준 슬라이더
rsi_limit = st.slider("RSI 값 이하 필터링", min_value=10, max_value=50, value=30, step=5)
st.write(f"📌 조건: RSI(14) < {rsi_limit}")

# RSI 필터링 실행
results = []
for ticker in favorites:
    try:
        st.write(f"🔄 {ticker} 데이터 다운로드 중...")
        df = yf.download(ticker, period="30d", interval="1d")

        if df.empty:
            st.warning(f"{ticker}: 데이터 없음")
            continue

        close = df['Close']
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]  # 첫 열만 가져오기

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
