import os
import yaml
import requests
import pandas as pd

# Load secrets
with open('config/secrets.yaml', 'r') as f:
    secrets = yaml.safe_load(f)

newsapi_key = secrets['newsapi']['api_key']

# Parameters
QUERY = 'stocks'
LIMIT = 100

url = (
    f'https://newsapi.org/v2/everything?'
    f'q={QUERY}&'
    f'pageSize={LIMIT}&'
    f'apiKey={newsapi_key}'
)

response = requests.get(url)
articles = response.json().get('articles', [])

data = []
for article in articles:
    data.append({
        'source': article['source']['name'],
        'author': article['author'],
        'title': article['title'],
        'description': article['description'],
        'url': article['url'],
        'publishedAt': article['publishedAt'],
        'content': article['content']
    })

# Ensure output directory exists
os.makedirs('data/raw', exist_ok=True)

# Save to CSV
out_path = f'data/raw/news_{QUERY}_recent.csv'
pd.DataFrame(data).to_csv(out_path, index=False)
print(f"Saved {len(data)} news articles to {out_path}") 