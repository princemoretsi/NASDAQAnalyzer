# NASDAQAnalyzer Streamlit App

## Overview  
This app provides market data, technical indicators (RSI), and news sentiment analysis for NASDAQ indices and ETFs using Alpha Vantage API and TextBlob sentiment analysis. It is mobile-friendly and deployable via Streamlit Cloud.

## Files  
- app.py: Main app code  
- requirements.txt: Python dependencies  
- .streamlit/secrets.toml: Store your Alpha Vantage API key securely

## Setup Instructions

1. Clone the repository  
2. Add your Alpha Vantage API key in .streamlit/secrets.toml  
3. Install dependencies with `pip install -r requirements.txt`  
4. Run locally with `streamlit run app.py`  
5. Or deploy on Streamlit Cloud by pushing repo and adding API key in Secrets  
6. Add to home screen on mobile for app-like experience

## Notes  
- News sentiment is mocked for now.  
- Keep API key secure and monitor Alpha Vantage usage limits.

