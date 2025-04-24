import yfinance as yf

def get_index_data(ticker, interval="1d"):
    """주어진 티커와 인터벌로 데이터를 가져오는 함수"""
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
