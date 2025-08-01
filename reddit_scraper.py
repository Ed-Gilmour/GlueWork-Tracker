import requests

def fetch_reddit_posts(subreddit, limit=10):
    headers = {'User-Agent': 'reddit_scraper/0.1 by anon'}
    url = f'https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}'

    response = requests.get(url, headers=headers)
    data = response.json()
    posts = data["data"]["children"]

    for i, post in enumerate(posts):
        title = post["data"]["title"]
        author = post["data"]["author"]
        score = post["data"]["score"]
        permalink = post["data"]["permalink"]
        print(f"{i+1}. {title} | name: {author} | score: {score}")
        print(f"https://reddit.com{permalink}\n")

fetch_reddit_posts("learnprogramming", limit=5)