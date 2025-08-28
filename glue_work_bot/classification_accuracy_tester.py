from sentence_bert_vectorizer import VectorIndexer
import ollama

class BinaryAccuracyTester:
    def llm_classify(self, text):
        response = ollama.generate(model="deepseek-r1:7b", prompt=self.get_mentoring_prompt(text))
        return response

    def get_mentoring_prompt(self, text):
        return f"""
You specialize in classifying mentoring and support data.

Text to classify:
{text}

Answer with only Y for mentoring and support, or N for not mentoring and support.
Answer with only Y or N. Nothing else and no explanation.
"""

    def test_accuracy(self):
        Exception("Not implemented")
        # Loop through test data with rag from training data

if __name__ == "__main__":
    test_indexer = VectorIndexer()
    training_indexer = VectorIndexer()
    test_indexer.store_mentoring_test_data()
    training_indexer.store_mentoring_training_test_data()

# Use RAG with the 80 to test for the 20
# Get the confusion matrix, precision, recall, and f1