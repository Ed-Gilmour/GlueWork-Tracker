from dotenv import load_dotenv
from sentence_bert_vectorizer import VectorIndexer
from google import genai
from enum import Enum
import re
import os

class GlueWorkType(Enum):
    UNKNOWN = -1
    MENTORING = 0

    def get_label(self):
        labels = {
            GlueWorkType.UNKNOWN: "Unknown",
            GlueWorkType.MENTORING: "Mentoring and Support"
        }
        return labels[self]

class ClassifierAgent:
    def __init__(self, aggregator):
        load_dotenv()
        self.aggregator = aggregator
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    def classify_data(self, prompt):
        return self.get_classification_from_response(
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            ).text
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

class MentoringAgent(ClassifierAgent):
    def __init__(self, aggregator):
        super().__init__(aggregator)
        self.vectorizer = VectorIndexer("mentoring")
        self.vectorizer.load_classification_data()

    def get_comment_prompt(self, comment):
        return f"""
Classify the following GitHub comment as:
-1 = Unknown
0 = Mentoring and Support
If you are unable to classify into any of those given categories classify as -1.

Comment Body:
{comment["body"]}

Answer with only the number, no words, no explanation.
"""

    # Use the following examples to help classify the comment:
    # {self.get_rag_data(comment["body"])}

    # def get_rag_data(self, query):
    #     responses = self.vectorizer.search(query, k=3)
    #     data = ""
    #     for text, distance in responses:
    #         classification = self.vectorizer.data[text]
    #         if classification == "Y":
    #             classification = "Yes"
    #         else:
    #             classification = "No"
    #         data += f"\nComment:\n{text}\nClassification for mentoring and support: {classification}\n"
    #     return data