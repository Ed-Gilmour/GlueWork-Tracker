from langchain_ollama import OllamaLLM
from enum import Enum
import re

class GlueWorkType(Enum):
    UNKNOWN = -1,
    MAINTENANCE = 0,
    QUALITY_ASSURANCE = 1,
    CODE_REVIEW = 2

    def get_label(self):
        labels = {
            GlueWorkType.UNKNOWN: "Unknown",
            GlueWorkType.MAINTENANCE: "Maintenance",
            GlueWorkType.QUALITY_ASSURANCE: "Quality Assurance",
            GlueWorkType.CODE_REVIEW: "Code Review",
        }
        return labels[self]

class ClassifierAgent:
    def __init__(self, aggregator):
        self.model = OllamaLLM(model="deepseek-r1:7b", base_url="http://localhost:11434")
        self.aggregator = aggregator

    def classify_data(self, prompt):
        return self.get_classification_from_response(self.strip_think_tags(self.model.invoke(prompt)))

    def get_classification_from_response(self, response):
        match = re.search(r"\d+", response)
        if match:
            number = int(match.group())
            try:
                return GlueWorkType(number)
            except ValueError:
                return GlueWorkType.UNKNOWN
        else:
            return GlueWorkType.UNKNOWN

    def strip_think_tags(self, text):
        return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

class CodeAgent(ClassifierAgent):
    def get_issue_prompt(self, issue):
        return f"""
Classify the following GitHub issue as:
-1 = Unknown
0 = Maintenance
1 = Quality Assurance

Issue Title:
{issue["title"]}

Issue Body:
{issue["body"]}

Answer with only the number, no words, no explanation.
"""

    def get_pull_request_prompt(self, pull_request):
        return f"""
Classify the following GitHub pull request as:
-1 = Unknown
0 = Maintenance
1 = Quality Assurance

Pull Request Title:
{pull_request["title"]}

Pull Request Body:
{pull_request["body"]}

Answer with only the number, no words, no explanation.
"""

    def get_commit_prompt(self, commit):
        return f"""
Classify the following GitHub commit as:
-1 = Unknown
0 = Maintenance
1 = Quality Assurance

Commit Message:
{commit["message"]}

Answer with only the number, no words, no explanation.
"""