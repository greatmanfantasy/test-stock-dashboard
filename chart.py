import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_chart(df, rsi, volume, ticker):
    """차트 출력 함수"""
    open_ = df["Open"].squeeze()
    high = df["High"].squeeze()
    low = df["Low"].squeeze()
    close = df["Close"].squeeze()

    # 보조 지표 포함한 차트 그리기
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        row_heights=[0.5, 0.25, 0.25],
        vertical_spacing=0.02,
        subplot_titles=("가격 캔들차트", "거래량", "RSI")
    )

    fig.add_trace(go.Candlestick(
        x=df.index,
        open=open_,
        high=high,
        low=low,
        close=close,
        name="Candlestick"
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        x=df.index,
        y=volume,
        name="Volume",
        marker_color="lightblue"
    ), row=2, col=1)

    fig.add_trace(go.Scatter(
        x=df.index,
        y=rsi,
        name="RSI",
        line=dict(color="orange", width=2, dash="dot")
    ), row=3, col=1)

    fig.update_layout(
        height=700,
        xaxis_rangeslider_visible=False,
        xaxis=dict(type='category'),
        showlegend=False
    )

    return fig
