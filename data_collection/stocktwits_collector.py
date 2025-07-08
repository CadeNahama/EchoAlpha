import requests
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import argparse
from datetime import datetime


def fetch_stocktwits(symbol, max_msgs=100):
    url = f"https://api.stocktwits.com/api/2/streams/symbol/{symbol}.json"
    resp = requests.get(url)
    data = resp.json()
    analyzer = SentimentIntensityAnalyzer()
    rows = []
    for msg in data.get('messages', [])[:max_msgs]:
        text = msg['body']
        timestamp = msg['created_at']
        sentiment = analyzer.polarity_scores(text)['compound']
        rows.append({
            'timestamp': timestamp,
            'source': 'stocktwits',
            'sentiment_score': sentiment,
            'entities': [symbol],
            'text': text
        })
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(description='Collect StockTwits messages for a symbol.')
    parser.add_argument('symbol', type=str, help='Ticker symbol (e.g., AAPL)')
    parser.add_argument('--max', type=int, default=100, help='Max messages to fetch')
    parser.add_argument('--out', type=str, default=None, help='Output CSV file')
    args = parser.parse_args()

    df = fetch_stocktwits(args.symbol, args.max)
    if args.out is None:
        today = datetime.utcnow().strftime('%Y-%m-%d')
        args.out = f"../data/raw/alternative/stocktwits_{args.symbol}_{today}.csv"
    df.to_csv(args.out, index=False)
    print(f"Saved {len(df)} StockTwits messages to {args.out}")

if __name__ == "__main__":
    main() 