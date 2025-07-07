import os
import yaml
import pandas as pd
import tweepy

# Load secrets
with open('config/secrets.yaml', 'r') as f:
    secrets = yaml.safe_load(f)

twitter_secrets = secrets['twitter']

# Initialize Twitter API
client = tweepy.Client(
    bearer_token=twitter_secrets.get('bearer_token'),
    consumer_key=twitter_secrets.get('api_key'),
    consumer_secret=twitter_secrets.get('api_secret'),
)

# Parameters
QUERY = 'stocks'
LIMIT = 100

tweets = client.search_recent_tweets(query=QUERY, max_results=min(LIMIT, 100), tweet_fields=['id','text','created_at','author_id','public_metrics'])

data = []
for tweet in tweets.data or []:
    data.append({
        'id': tweet.id,
        'text': tweet.text,
        'created_at': tweet.created_at,
        'author_id': tweet.author_id,
        'retweet_count': tweet.public_metrics.get('retweet_count'),
        'reply_count': tweet.public_metrics.get('reply_count'),
        'like_count': tweet.public_metrics.get('like_count'),
        'quote_count': tweet.public_metrics.get('quote_count'),
    })

# Ensure output directory exists
os.makedirs('data/raw', exist_ok=True)

# Save to CSV
out_path = f'data/raw/twitter_{QUERY}_recent.csv'
pd.DataFrame(data).to_csv(out_path, index=False)
print(f"Saved {len(data)} tweets to {out_path}") 