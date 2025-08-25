from enum import Enum
import ollama
import re

class GlueWorkType(Enum):
    UNKNOWN = -1
    MAINTENANCE = 0
    QUALITY_ASSURANCE = 1
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
        self.aggregator = aggregator

    def classify_data(self, prompt):
        return self.get_classifications_from_response(
            self.strip_think_tags(
                ollama.generate(
                    model="deepseek-r1:7b", prompt=prompt
                )["response"]
            )
        )

    def get_classifications_from_response(self, response):
        numbers = re.findall(r"-?\d+", response)
        results = []
        for num_str in numbers:
            try:
                number = int(num_str)
                results.append(GlueWorkType(number))
            except ValueError:
                results.append(GlueWorkType.UNKNOWN)
        return results

    def strip_think_tags(self, text):
        return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

class CodeAgent(ClassifierAgent):
    def get_issue_prompt(self, issues):
        prompt = f"""
Classify the following GitHub issues as:
-1 = Unknown
0 = Maintenance
1 = Quality Assurance
If you are unable to classify into any of those given categories classify as -1.
Respond with the classifications to all the GitHub issues top to bottom.
Answer with only the numbers, no words, no explanation.

"""
        for i in range(len(issues)):
            prompt += f"""

Issue {i} Title:
{issues[i]["title"]}

Issue {i} Body:
{issues[i]["body"]}

"""
        return prompt

    def get_pull_request_prompt(self, pull_requests):
        prompt = f"""
Classify the following GitHub pull requests as:
-1 = Unknown
0 = Maintenance
1 = Quality Assurance
If you are unable to classify into any of those given categories classify as -1.
Respond with the classifications to all the GitHub pull requests top to bottom.
Answer with only the numbers, no words, no explanation.

"""
        for i in range(len(pull_requests)):
            prompt += f"""

Pull Request {i} Title:
{pull_requests[i]["title"]}

Pull Request {i} Body:
{pull_requests[i]["body"]}

"""
        return prompt

    def get_commit_prompt(self, commits):
        prompt = f"""
Classify the following GitHub commits as:
-1 = Unknown
0 = Maintenance
1 = Quality Assurance
If you are unable to classify into any of those given categories classify as -1.
Respond with the classifications to all the GitHub commits top to bottom.
Answer with only the numbers, no words, no explanation.

"""
        for i in range(len(commits)):
            prompt += f"""

Commit {i} Message:
{commits[i]["message"]}

"""
        return prompt