import requests

def fetch_stack_overflow_posts(tag):
    url = "https://api.stackexchange.com/2.3/search"
    params = {
        "order": "desc",
        "sort": "activity",
        "tagged": tag,
        "site": "stackoverflow",
        "pagesize": 5
    }

    response = requests.get(url, params=params)
    data = response.json()

    for i, item in enumerate(data.get("items", [])):
        print(f"{i+1}. {item['title']} | name: {item['owner']['display_name']}")
        print(f"{item['link']}\n")

fetch_stack_overflow_posts("flutter")