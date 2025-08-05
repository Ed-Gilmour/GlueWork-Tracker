from langchain_ollama import OllamaLLM

class ClassifierAgent:
    def __init__(self):
        self.model = OllamaLLM(model="deepseek-r1:7b")

    def classify_data(self, data):
        return self.model.invoke(f"{data}")