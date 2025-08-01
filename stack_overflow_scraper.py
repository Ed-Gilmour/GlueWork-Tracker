import requests
from collections import Counter

def find_top_posters(tag, pages=2):
    question_counter = Counter()
    answer_counter = Counter()

    for page in range(1, pages + 1):
        url = "https://api.stackexchange.com/2.3/search"
        params = {
            "order": "desc",
            "sort": "activity",
            "tagged": tag,
            "site": "stackoverflow",
            "pagesize": 50,
            "page": page
        }
        headers = {"User-Agent": "stackoverflow_scraper/0.1"}

        response = requests.get(url, params=params, headers=headers)

        if(response.status_code != 200):
            print("error code: ", response.status_code)
            return

        data = response.json()

        for item in data.get("items", []):
            owner = item.get("owner", {})
            top_answer_user = get_top_answer_user(item["question_id"])
            if top_answer_user != None:
                answer_counter[top_answer_user] += 1
            question_counter[owner["display_name"]] += 1

    print(f"Top posters for tag '{tag}':\n")
    for i, (user, count) in enumerate(answer_counter.most_common(10), 1):
        print(f"{i}. {user}: {count} answers, {question_counter.get(user)} questions")

def get_top_answer_user(question_id):
    url = f"https://api.stackexchange.com/2.3/questions/{question_id}/answers"
    params = {
        "order": "desc",
        "sort": "votes",
        "site": "stackoverflow",
        "filter": "withbody"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if(len(data.get("items", [])) == 0):
        return

    return data["items"][0]["owner"]["display_name"]

find_top_posters("flutter")