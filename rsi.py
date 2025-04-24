import ta

def calculate_rsi(df, rsi_period):
    """RSI 계산"""
    close = df['Close'].squeeze()
    rsi = ta.momentum.RSIIndicator(close, window=rsi_period).rsi()
    return rsi
