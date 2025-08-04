from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import json

class VectorIndexer:
    def __init__(self, model_name="all-mpnet-base-v2"):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.texts = []

    def encode_texts(self, texts):
        self.texts = texts
        embeddings = self.model.encode(texts, convert_to_tensor=False)
        return np.array(embeddings).astype("float32")

    def build_index(self, embeddings_np):
        dimension = embeddings_np.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings_np)

    def save_index(self, path_prefix):
        faiss.write_index(self.index, path_prefix + ".faiss")
        with open(path_prefix + ".json", "w", encoding="utf-8") as f:
            json.dump(self.texts, f, ensure_ascii=False, indent=2)

    def load_index(self, path_prefix):
        self.index = faiss.read_index(path_prefix)
        with open(path_prefix + ".json", "r", encoding="utf-8") as f:
            self.texts = json.load(f)

    def search(self, query_text, k=1):
        query_embedding = self.model.encode([query_text]).astype("float32")
        distances, indices = self.index.search(query_embedding, k)
        return [(self.texts[i], distances[0][idx]) for idx, i in enumerate(indices[0])]