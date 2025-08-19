from langchain_ollama import OllamaLLM
import re

class CodeAgent:
    def __init__(self):
        self.model = OllamaLLM(model="deepseek-r1:7b", base_url="http://localhost:11434")

    def classify_data(self, prompt):
        return self.strip_think_tags(self.model.invoke(prompt))

    def get_issue_prompt(self, issue):
        return f"""
You are given a GitHub issue.
You specialize in classifying whether this issue is maintenance, quality assurance, if it's anything else respond with unknown.
Respond with only the classification of the issue.

Issue Title:
{issue["title"]}

Issue Body:
{issue["body"]}
"""

    def get_pull_request_prompt(self, pull_request):
        return f"""
You are given a GitHub pull request.
You specialize in classifying whether this pull request is maintenance, quality assurance, if it's anything else respond with unknown.
Respond with only the classification of the pull request.

Pull Request Title:
{pull_request["title"]}

Pull Request Body:
{pull_request["body"]}
"""

    def get_commit_prompt(self, commit):
        return f"""
You are given a GitHub commit.
You specialize in classifying whether this commit is maintenance, quality assurance, if it's anything else respond with unknown.
Respond with only the classification of the commit.

Commit Message:
{commit["message"]}
"""

    def strip_think_tags(self, text):
        return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)