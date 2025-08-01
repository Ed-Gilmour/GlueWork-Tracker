from collections import Counter
import requests

def fetch_reddit_posts(subreddit, limit=10):
    headers = {'User-Agent': 'reddit_scraper/0.1 by anon'}
    url = f'https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}'

    response = requests.get(url, headers=headers)
    data = response.json()

    if(response.status_code != 200):
        print("error code: ", response.status_code)
        return

    post_counter = Counter()
    reply_counter = Counter()

    posts = data["data"]["children"]

    for i, post in enumerate(posts):
        post_counter[post["data"]["author"]] += 1
        top_reply_user = get_top_reply_user(subreddit=subreddit, id=post["data"]["id"])
        if top_reply_user != None:
            reply_counter[top_reply_user] += 1
    for i, (user, posts) in enumerate(post_counter.most_common(10)):
        print(f"{i+1}. {user} | posts: {posts} | replies: {reply_counter.get(user)}")

def get_top_reply_user(subreddit, id):
    headers = {'User-Agent': 'MyRedditScraper/1.0'}
    url = f"https://www.reddit.com/r/{subreddit}/comments/{id}.json?sort=top&limit=1"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Error:", response.status_code)
        return

    data = response.json()
    comments = data[1]["data"]["children"]

    if len(comments) == 0:
        return None

    comment = data[1]["data"]["children"][0]
    return comment["data"]["author"]

fetch_reddit_posts("FlutterDev", limit=50)