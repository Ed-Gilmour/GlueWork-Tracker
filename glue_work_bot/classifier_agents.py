from langchain_ollama import OllamaLLM
import re

class CodeAgent:
    def __init__(self):
        self.model = OllamaLLM(model="deepseek-r1:7b", base_url="http://localhost:11434")

    def classify_data(self, prompt):
        print("Start data classification")
        return strip_think_tags(self.model.invoke(prompt))

    def get_issue_prompt(self, issue):
        print("Get prompt for: " + issue["title"])
        return f"""
You are given a GitHub issue.
You specialize in classifying whether this issue is maintenance or quality assurance.
Respond with only the classification of the issue.

Issue Title:
{issue["title"]}

Issue Body:
{issue["body"]}
"""

def strip_think_tags(response: str) -> str:
    return re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL)