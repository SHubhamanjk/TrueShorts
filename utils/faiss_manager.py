import faiss
import numpy as np
import os
from config import Config
from functools import lru_cache
import threading

class FAISSManager:
    def __init__(self):
        self._indices = {}
        self._lock = threading.Lock()
    
    def get_index(self, path: str):
        with self._lock:
            if path not in self._indices:
                full_path = os.path.join(Config.FAISS_INDEX_DIR, path)
                if os.path.exists(full_path):
                    self._indices[path] = faiss.read_index(full_path)
                else:
                    index = faiss.IndexHNSWFlat(384, 32)
                    index.hnsw.efSearch = 64
                    self._indices[path] = faiss.IndexIDMap(index)
            return self._indices[path]
    
    def save_index(self, path: str, index):
        full_path = os.path.join(Config.FAISS_INDEX_DIR, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        faiss.write_index(index, full_path)

faiss_manager = FAISSManager()
