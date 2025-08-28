from sentence_bert_vectorizer import VectorIndexer
from classifier_agents import ClassifierAgent
import ollama

class BinaryAccuracyTester:
    def __init__(self, training_indexer, test_indexer):
        self.training_indexer = training_indexer
        self.test_indexer = test_indexer

    def llm_classify(self, prompt):
        response = ClassifierAgent.strip_think_tags(text=ollama.generate(model="deepseek-r1:7b", prompt=prompt)["response"])
        if "Y" in response.lower():
            return "Y"
        else:
            return "N"

    def get_mentoring_prompt(self, text):
        return f"""
Classify the following as either mentoring and support or not mentoring and support.

Data to classify:
{text}

Use the following examples of mentoring and support classifications to help classify the data:
{self.get_rag_data(text)}

Answer with only Y for mentoring and support, or N for not mentoring and support. Nothing else and no explanation.
"""

    def get_rag_data(self, query, k=3):
        responses = self.training_indexer.search(query, k)
        data = ""
        for text, distance in responses:
            classification = self.training_indexer.data[text]
            if classification == "Y":
                classification = "Yes"
            else:
                classification = "No"
            data += f"Comment:\n{text}\nClassification for mentoring and support: {classification}\n"
        return data

    def test_accuracy(self):
        i = 0
        for text, actual in self.test_indexer.data.items():
            predicted = self.llm_classify(self.get_mentoring_prompt(text))
            print(f"{i}.\nText: {text}\nActual: {actual}, Predicted: {predicted}\n")
            i += 1

if __name__ == "__main__":
    test_indexer = VectorIndexer()
    training_indexer = VectorIndexer()
    training_indexer.load_mentoring_training_test_data()
    test_indexer.load_mentoring_test_data()
    accuracy_tester = BinaryAccuracyTester(training_indexer, test_indexer)
    accuracy_tester.test_accuracy()

# Fix responding with N to everything by using data from the paper to give it more information on what is mentoring
# Get the confusion matrix, precision, recall, and f1-score