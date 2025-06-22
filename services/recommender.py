from sentence_transformers import SentenceTransformer
from utils.faiss_manager import faiss_manager
import numpy as np
import logging

logger = logging.getLogger(__name__)
model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_text(text: str):
    return model.encode(text)

def is_similar(embedding, index, threshold=0.8):
    if index.ntotal == 0:
        return False
    D, _ = index.search(np.array([embedding]).astype('float32'), 1)
    return D[0][0] >= threshold

def recommend_similar(embedding, index, top_k=5):
    if index.ntotal == 0:
        return [], []
    D, I = index.search(np.array([embedding], dtype=np.float32), top_k)
    return I[0].tolist(), D[0].tolist()
