from langchain_ollama import OllamaLLM
import re

class ClassifierAgent:
    def __init__(self):
        self.model = OllamaLLM(model="deepseek-r1:7b")

    def classify_data(self, prompt):
        return strip_think_tags(self.model.invoke(f"""
You specialize in classifying code work with the data you're given.
Classify the data you're given into 1 of 4 types of work: maintenance, QA, code review, and licence.
The confidence is a value between 0 and 1 with 0 being no confidence and 1 being full confidence that you classified the data correctly.
Respond in this exact format without any explanation: Classification Confidence

Data to classify:
{prompt}
"""))

def strip_think_tags(response: str) -> str:
    return re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL)