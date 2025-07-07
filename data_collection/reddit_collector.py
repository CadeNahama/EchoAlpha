import os
import yaml
import praw
import pandas as pd

# Load secrets
with open('config/secrets.yaml', 'r') as f:
    secrets = yaml.safe_load(f)

reddit_secrets = secrets['reddit']

# Initialize Reddit API
reddit = praw.Reddit(
    client_id=reddit_secrets['client_id'],
    client_secret=reddit_secrets['client_secret'],
    user_agent=reddit_secrets['user_agent'],
    username=reddit_secrets.get('username'),
    password=reddit_secrets.get('password')
)

# Parameters
SUBREDDIT = 'stocks'
LIMIT = 100

# Fetch posts
data = []
for submission in reddit.subreddit(SUBREDDIT).hot(limit=LIMIT):
    data.append({
        'id': submission.id,
        'title': submission.title,
        'score': submission.score,
        'url': submission.url,
        'num_comments': submission.num_comments,
        'created_utc': submission.created_utc,
        'selftext': submission.selftext
    })

# Ensure output directory exists
os.makedirs('data/raw', exist_ok=True)

# Save to CSV
out_path = f'data/raw/reddit_{SUBREDDIT}_hot.csv'
pd.DataFrame(data).to_csv(out_path, index=False)
print(f"Saved {len(data)} posts to {out_path}") 