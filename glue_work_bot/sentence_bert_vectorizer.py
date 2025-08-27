from sentence_transformers import SentenceTransformer
import numpy as np
import pandas as pd
import faiss
import json

class VectorIndexer:
    MENTORING_TRAINING_PATH = "gluework_repo/glue_work_bot/training_data/mentoring_training_dataset.csv"
    MENTORING_DATA_PATH = "gluework_repo/glue_work_bot/cached_data/mentoring_data.json"
    MENTORING_INDEX_PATH = "gluework_repo/glue_work_bot/cached_data/mentoring_index.faiss"

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
        faiss.write_index(self.index, index_path)

    def load_index(self, index_path):
        self.index = faiss.read_index(index_path)

    def search(self, query_text, k=1):
        query_embedding = self.model.encode([query_text]).astype("float32")
        distances, indices = self.index.search(query_embedding, k)
        return [(list(self.data.keys())[i], distances[0][idx]) for idx, i in enumerate(indices[0])]

    def save_csv_data(self, csv_path, key_name, value_name, data_path):
        df = pd.read_csv(csv_path)
        self.data = dict(zip(df[key_name], df[value_name]))
        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def load_csv_data(self, data_path):
        with open(data_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def store_mentoring_data(self):
        self.save_csv_data(self.MENTORING_TRAINING_PATH, "comments", "mentoring", self.MENTORING_DATA_PATH)
        self.build_index(self.encode_texts())
        self.save_index(self.MENTORING_INDEX_PATH)

    def load_mentoring_data(self):
        self.load_csv_data(self.MENTORING_DATA_PATH)
        self.load_index(self.MENTORING_INDEX_PATH)