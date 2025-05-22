import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
from textblob import TextBlob

# ========== Configuration ==========
ALPHA_VANTAGE_KEY = st.secrets.get("ALPHA_VANTAGE_API_KEY", None)
BASE_URL = "https://www.alphavantage.co/query"

SYMBOLS = {
    'NASDAQ Composite': '^IXIC',
    'NASDAQ 100': '^NDX',
    'QQQ ETF': 'QQQ',
    'NASDAQ Futures': 'NQ=F'
}

# ========== Helper Functions ==========

def fetch_market_data(symbol):
    if not ALPHA_VANTAGE_KEY:
        return None
    params = {
        'function': 'GLOBAL_QUOTE',
        'symbol': symbol,
        'apikey': ALPHA_VANTAGE_KEY
    }
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json().get('Global Quote', {})
        return {
            'price': float(data['05. price']),
            'change_percent': float(data['10. change percent'].strip('%')),
            'volume': int(data['06. volume'])
        }
    except Exception:
        return None

def fetch_historical_data(symbol):
    if not ALPHA_VANTAGE_KEY:
        return pd.DataFrame()
    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': symbol,
        'outputsize': 'compact',
        'apikey': ALPHA_VANTAGE_KEY
    }
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json().get('Time Series (Daily)', {})
        df = pd.DataFrame.from_dict(data, orient='index', dtype=float)
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        df.rename(columns={
            '1. open': 'Open', '2. high': 'High',
            '3. low': 'Low', '4. close': 'Close',
            '5. volume': 'Volume'
        }, inplace=True)
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
        df = calculate_rsi(df)
        return df
    except Exception:
        return pd.DataFrame()

def calculate_rsi(df, window=14):
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=window).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=window).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

def mock_news():
    headlines = [
        "Tech stocks rally as AI optimism boosts NASDAQ",
        "Fed rate hike concerns weigh on tech sector",
        "Microsoft announces breakthrough in quantum computing",
        "Inflation data comes in hotter than expected",
        "Apple unveils new AI features at WWDC"
    ]
    data = []
    for h in headlines:
        sentiment = TextBlob(h).sentiment.polarity
        label = 'Bullish' if sentiment > 0.1 else 'Bearish' if sentiment < -0.1 else 'Neutral'
        data.append({"headline": h, "sentiment": label, "score": sentiment})
    return pd.DataFrame(data)

# ========== Streamlit UI ==========

st.set_page_config(page_title="NASDAQ Analyzer", layout="centered")
st.title("NASDAQ Market Analyzer")

# Market Overview
st.header("Market Overview")
columns = st.columns(len(SYMBOLS))
market_data = {}
for i, (name, symbol) in enumerate(SYMBOLS.items()):
    data = fetch_market_data(symbol)
    if data:
        market_data[name] = data
        with columns[i]:
            st.metric(label=name, value=f"${data['price']:.2f}", delta=f"{data['change_percent']:.2f}%")

# News Sentiment
st.header("News Sentiment Analysis")
news_df = mock_news()
for _, row in news_df.iterrows():
    color = "green" if row.sentiment == "Bullish" else "red" if row.sentiment == "Bearish" else "gray"
    st.markdown(f"**{row.headline}**")
    st.markdown(f"Sentiment: :{color}[{row.sentiment}] (Score: {row.score:.2f})")
    st.markdown("---")

# Technical Analysis for QQQ
st.header("Technical Chart - QQQ")
df = fetch_historical_data("QQQ")
if not df.empty:
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df.index[-30:], df['Close'][-30:], label='Close Price')
    ax.set_title("QQQ - 30 Day Performance")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price ($)")
    ax.legend()
    st.pyplot(fig)

    st.subheader("RSI Indicator")
    rsi = df['RSI'].iloc[-1]
    st.write(f"Current RSI: {rsi:.2f}")
else:
    st.warning("Unable to fetch QQQ data. Please check API or connection.")
