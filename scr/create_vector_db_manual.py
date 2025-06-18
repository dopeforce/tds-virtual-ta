#!/usr/bin/env python3
import os
import faiss
import json
import tiktoken

import numpy as np
import markdown as md

from pathlib import Path
from typing import List, Dict
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

EMBED_DIM = 384
BATCH_SIZE = 16
CHUNK_SIZE = 300
CHUNK_OVERLAP = 50

index = faiss.IndexFlatIP(EMBED_DIM)
metadata: List[Dict] = []
print("Loading embedding model...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
print("Embedding model loaded successfully!")

ENC = tiktoken.encoding_for_model("text-embedding-3-small")

def chunk_by_tokens(text: str, max_tokens: int, overlap: int) -> List[str]:
    text = text.replace("\n", " ")
    tokens = ENC.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + max_tokens, len(tokens))
        chunk_toks = tokens[start:end]
        chunk = ENC.decode(chunk_toks)
        chunks.append(chunk)
        start += max_tokens - overlap
    return chunks

def chunk_text(text: str, size: int, overlap: int) -> List[str]:
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += size - overlap
    return chunks

def embed_text(text: str) -> list:
    """
    Create embeddings using sentence-transformers (completely free)
    Maintains the same interface as the original function
    """
    try:
        text = text.replace("\n", " ")
        embedding = embedding_model.encode(text, convert_to_tensor=False)
        embedding = np.array(embedding, dtype=np.float32)
        normalized_embedding = embedding / np.linalg.norm(embedding)
        return normalized_embedding.tolist()
    except Exception as e:
        print(f"Error creating embedding: {e}")
        return None

def safe_embed(text: str) -> list:
    """
    Safe embedding with fallback for long texts
    Updated to work with sentence-transformers
    """
    try:
        return embed_text(text)
    except Exception as e:
        if len(text) > 5000:
            mid = len(text) // 2
            left = safe_embed(text[:mid])
            right = safe_embed(text[mid:])
            if left and right:
                return ((np.array(left) + np.array(right)) / 2).tolist()
        print(f"Error in safe_embed: {e}")
        return None

def load_file(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    raw = open(path, encoding="utf-8").read()
    if ext == ".html":
        return BeautifulSoup(raw, "html.parser").get_text("\n")
    elif ext == ".md":
        html = md.markdown(raw)
        return BeautifulSoup(html, "html.parser").get_text("\n")
    else:
        return raw

def get_source(file: str) -> str:
    p = Path(file)
    if str(p.parent).endswith("discourse_content"):
        return f"https://tds.s-anand.net/#/{p.name.replace('.md', '')}"
    elif str(p.parent).endswith("discourse_posts"):
        json_path = os.path.join("res", "discourse_threads", p.name.replace(".txt", ".json"))
        try:
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)
            return f"https://discourse.onlinedegree.iitm.ac.in/t/{data['slug']}/{data['id']}"
        except (FileNotFoundError, KeyError) as e:
            print(f"Warning: Could not load JSON for {file}: {e}")
            return file
    return file

def ingest_dir(root_dir: str):
    if not os.path.exists(root_dir):
        raise FileNotFoundError(f"Directory {root_dir} does not exist")
    batch_texts, batch_meta = [], []
    for dirpath, _, files in os.walk(root_dir):
        for fname in files:
            if not fname.lower().endswith((".txt", ".html", ".md")):
                continue
            full = os.path.join(dirpath, fname)
            text = load_file(full)
            print(f"Loaded {full} ({len(text)} chars): {len(text.split())} words)")
            chunks = chunk_by_tokens(text, max_tokens=8000, overlap=200)
            for idx, chunk in enumerate(chunks):
                meta = {"source": get_source(full), "chunk_id": idx}
                batch_texts.append(chunk)
                batch_meta.append(meta)
                if len(batch_texts) >= BATCH_SIZE:
                    index_batch(batch_texts, batch_meta)
                    batch_texts, batch_meta = [], []
    if batch_texts:
        index_batch(batch_texts, batch_meta)

def index_batch(texts: List[str], metas: List[Dict]):
    embs = []
    valid_texts = []
    valid_metas = []
    for i, text in enumerate(texts):
        embedding = safe_embed(text)
        if embedding is not None:
            embs.append(embedding)
            valid_texts.append(text)
            valid_metas.append(metas[i])
        else:
            print(f"Warning: Failed to embed text chunk {i}")
    if embs:
        arr = np.array(embs, dtype=np.float32)
        index.add(arr)
        metadata.extend([{"text": t, **m} for t, m in zip(valid_texts, valid_metas)])
        print(f"Indexed {len(embs)} chunks; total is now {index.ntotal}")
    else:
        print("Warning: No valid embeddings in this batch")

def install_dependencies():
    """Install sentence-transformers if not available"""
    try:
        import sentence_transformers
        return True
    except ImportError:
        print("Installing sentence-transformers...")
        import subprocess
        try:
            subprocess.check_call(["pip", "install", "sentence-transformers"])
            print("sentence-transformers installed successfully!")
            return True
        except subprocess.CalledProcessError:
            print("Failed to install sentence-transformers. Please install manually:")
            print("pip install sentence-transformers")
            return False

if __name__ == "__main__":
    if not install_dependencies():
        exit(1)
    root = "res/"
    print(f"Starting vector database creation...")
    print(f"Configuration:")
    print(f"   - Embedding model: all-MiniLM-L6-v2 (free)")
    print(f"   - Embedding dimension: {EMBED_DIM}")
    print(f"   - Batch size: {BATCH_SIZE}")
    print(f"   - Chunk max tokens: 8000")
    print(f"   - Chunk overlap: 200")
    print()
    
    ingest_dir(root)
    
    os.makedirs("res/model/", exist_ok=True)
    faiss.write_index(index, "res/model/virtual-ta.faiss")
    with open("res/model/metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)
    print()
    print(f"Ingestion complete!")
    print(f"Final Statistics:")
    print(f"   - Total vectors in index: {index.ntotal}")
    print(f"   - Metadata entries: {len(metadata)}")
    print(f"   - FAISS index saved to: res/model/virtual-ta.faiss")
    print(f"   - Metadata saved to: res/model/metadata.json")
    print()
    print("Vector database creation successful!")
    print("No API keys were used - completely free local embeddings!")