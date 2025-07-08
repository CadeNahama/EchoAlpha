import os
import yaml
import requests
import pandas as pd
import argparse
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime

# Load secrets
with open('config/secrets.yaml', 'r') as f:
    secrets = yaml.safe_load(f)
newsapi_key = secrets['newsapi']['api_key']

def fetch_newsapi(query, limit=100):
    url = (
        f'https://newsapi.org/v2/everything?'
        f'q={query}&'
        f'pageSize={limit}&'
        f'apiKey={newsapi_key}'
    )
    response = requests.get(url)
    articles = response.json().get('articles', [])
    analyzer = SentimentIntensityAnalyzer()
    data = []
    for article in articles:
        text = (article['title'] or '') + ' ' + (article.get('description') or '')
        sentiment = analyzer.polarity_scores(text)['compound']
        # Try to extract tickers/entities from the query (simple version)
        entities = [query.upper()]
        data.append({
            'timestamp': article['publishedAt'],
            'source': 'newsapi',
            'sentiment_score': sentiment,
            'entities': entities,
            'text': text,
            'url': article['url'],
            'title': article['title'],
            'description': article['description'],
            'news_source': article['source']['name']
        })
    return pd.DataFrame(data)

def main():
    parser = argparse.ArgumentParser(description='Collect NewsAPI articles for a symbol or query.')
    parser.add_argument('query', type=str, help='Ticker symbol or search query (e.g., AAPL or "Apple stock")')
    parser.add_argument('--limit', type=int, default=100, help='Max articles to fetch')
    parser.add_argument('--out', type=str, default=None, help='Output CSV file')
    args = parser.parse_args()

    df = fetch_newsapi(args.query, args.limit)
    # Ensure output directory exists
    os.makedirs('data/raw/alternative', exist_ok=True)
    if args.out is None:
        today = datetime.utcnow().strftime('%Y-%m-%d')
        args.out = f'data/raw/alternative/newsapi_{args.query}_{today}.csv'
    df.to_csv(args.out, index=False)
    print(f"Saved {len(df)} news articles to {args.out}")

if __name__ == "__main__":
    main() 