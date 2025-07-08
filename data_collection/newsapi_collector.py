import requests
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import argparse
from datetime import datetime
import os


def fetch_newsapi(symbol, api_key, max_articles=100):
    url = f'https://newsapi.org/v2/everything?q={symbol}&apiKey={api_key}'
    resp = requests.get(url)
    data = resp.json()
    analyzer = SentimentIntensityAnalyzer()
    rows = []
    for article in data.get('articles', [])[:max_articles]:
        text = article['title'] + ' ' + (article.get('description') or '')
        timestamp = article['publishedAt']
        sentiment = analyzer.polarity_scores(text)['compound']
        rows.append({
            'timestamp': timestamp,
            'source': 'newsapi',
            'sentiment_score': sentiment,
            'entities': [symbol],
            'text': text
        })
    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(description='Collect NewsAPI articles for a symbol.')
    parser.add_argument('symbol', type=str, help='Ticker symbol (e.g., AAPL)')
    parser.add_argument('--max', type=int, default=100, help='Max articles to fetch')
    parser.add_argument('--out', type=str, default=None, help='Output CSV file')
    parser.add_argument('--api_key', type=str, default=None, help='NewsAPI API key (or set NEWSAPI_KEY env var)')
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get('NEWSAPI_KEY')
    if not api_key:
        raise ValueError('NewsAPI API key must be provided via --api_key or NEWSAPI_KEY env var')

    df = fetch_newsapi(args.symbol, api_key, args.max)
    if args.out is None:
        today = datetime.utcnow().strftime('%Y-%m-%d')
        args.out = f"../data/raw/alternative/newsapi_{args.symbol}_{today}.csv"
    df.to_csv(args.out, index=False)
    print(f"Saved {len(df)} NewsAPI articles to {args.out}")

if __name__ == "__main__":
    main() 