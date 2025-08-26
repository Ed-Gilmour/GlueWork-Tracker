from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd
import faiss
import json

class VectorIndexer:
    def __init__(self, model_name="all-mpnet-base-v2"):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.data = {}

    def encode_texts(self):
        embeddings = self.model.encode(list(self.data.keys()), convert_to_tensor=False)
        return np.array(embeddings).astype("float32")

    def build_index(self, embeddings_np):
        dimension = embeddings_np.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings_np)

    def save_index(self, index_path):
        faiss.write_index(self.index, index_path + ".faiss")

    def load_index(self, index_path):
        self.index = faiss.read_index(index_path + ".faiss")

    def search(self, query_text, k=1):
        query_embedding = self.model.encode([query_text]).astype("float32")
        distances, indices = self.index.search(query_embedding, k)
        return [(list(self.data.keys())[i], distances[0][idx]) for idx, i in enumerate(indices[0])]

    def save_csv_data(self, csv_path, key_name, value_name, data_path):
        df = pd.read_csv(csv_path + ".csv")
        self.data = dict(zip(df[key_name], df[value_name]))
        with open(data_path + ".json", "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def load_csv_data(self, data_path):
        with open(data_path + ".json", "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def store_mentoring_data(self):
        self.save_csv_data("glue_work_bot/training_data/mentoring_training_dataset", "comments", "mentoring", "glue_work_bot/cached_data/mentoring_data")
        self.build_index(self.encode_texts())
        self.save_index("glue_work_bot/cached_data/mentoring_index")

    def load_mentoring_data(self):
        self.load_csv_data("glue_work_bot/cached_data/mentoring_data")
        self.load_index("glue_work_bot/cached_data/mentoring_index")

if __name__ == "__main__":
    vectorizer = VectorIndexer()
    vectorizer.load_mentoring_data()
    s_data = vectorizer.search("""
After looking into the code this is not needed, so if a root is no longer a root without the entirely tree to be build from scratch, it must be keep alive by a globalkey.

The globalkey reparent will cause the activate to be called in the entire subtree, which will causes didChangeDependencies and markNeedsBuild(if it has any dependencies) of the entire to be called.

I will add a test to ensure this behavior""",
                    3)
    for text, distance in s_data:
        print(f"\nTEXT: {text}\nDISTANCE: {distance}\n")
        print("\nCLASSIFICATION: " + vectorizer.data[text] + "\n\n")