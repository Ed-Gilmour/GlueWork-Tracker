from sentence_bert_vectorizer import VectorIndexer
from enum import Enum
import ollama
import re

class GlueWorkType(Enum):
    UNKNOWN = -1
    MAINTENANCE = 0
    QUALITY_ASSURANCE = 1
    CODE_REVIEW = 2
    MENTORING = 3

    def get_label(self):
        labels = {
            GlueWorkType.UNKNOWN: "Unknown",
            GlueWorkType.MAINTENANCE: "Maintenance",
            GlueWorkType.QUALITY_ASSURANCE: "Quality Assurance",
            GlueWorkType.CODE_REVIEW: "Code Review",
            GlueWorkType.MENTORING: "Mentoring and Support"
        }
        return labels[self]

class ClassifierAgent:
    def __init__(self, aggregator):
        self.aggregator = aggregator

    def classify_data(self, prompt):
        return self.get_classification_from_response(
            self.strip_think_tags(
                ollama.generate(
                    model="deepseek-r1:7b", prompt=prompt
                )["response"]
            )
        )

    def get_classification_from_response(self, response):
        match = re.search(r"-?\d+", response)
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
If you are unable to classify into any of those given categories classify as -1.

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
If you are unable to classify into any of those given categories classify as -1.

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
If you are unable to classify into any of those given categories classify as -1.

Commit Message:
{commit["message"]}

Answer with only the number, no words, no explanation.
"""

class MentoringAgent(ClassifierAgent):
    RAG_COUNT = 3

    def __init__(self, aggregator):
        super().__init__(aggregator)
        self.vectorizer = VectorIndexer()
        self.vectorizer.load_mentoring_data()

    def get_comment_prompt(self, comment):
        return f"""
Classify the following GitHub comment as:
-1 = Unknown
3 = Mentoring and Support
If you are unable to classify into any of those given categories classify as -1.

Comment Body:
{comment["body"]}

Use the following examples to help classify the comment:
{self.get_rag_data(comment["body"])}

Answer with only the number, no words, no explanation.
"""

    def get_rag_data(self, query):
        responses = self.vectorizer.search(query, self.RAG_COUNT)
        data = ""
        for text, distance in responses:
            classification = self.vectorizer.data[text]
            if classification == "Y":
                classification = "Yes"
            else:
                classification = "No"
            data += f"\nComment:\n{text}\nClassification for mentoring and support: {classification}\n"
        return data