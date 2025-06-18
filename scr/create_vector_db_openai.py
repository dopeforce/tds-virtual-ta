#!/usr/bin/env python3
import os
import openai
import faiss
import json
import tiktoken

import numpy as np
import markdown as md

from pathlib import Path
from typing import List, Dict
from bs4 import BeautifulSoup
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

EMBED_DIM = 1536
BATCH_SIZE = 16  
CHUNK_SIZE = 300  
CHUNK_OVERLAP = 50

index = faiss.IndexFlatIP(EMBED_DIM)
metadata: List[Dict] = []

client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL,
)

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
    text = text.replace("\n", " ")
    resp = client.embeddings.create(
        model="text-embedding-3-small", input=[text], dimensions=EMBED_DIM
    )
    embedding = np.array(resp.data[0].embedding, dtype=np.float32)
    normalized_embedding = embedding / np.linalg.norm(embedding)
    return normalized_embedding.tolist()

def safe_embed(text):
    try:
        return embed_text(text)
    except openai.BadRequestError as e:
        if "maximum context length" in str(e):
            mid = len(text) // 2
            left = safe_embed(text[:mid])
            right = safe_embed(text[mid:])
            return ((np.array(left) + np.array(right)) / 2).tolist()
        raise

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
        data = json.load(open(os.path.join("res", "discourse_threads", p.name.replace(".txt", ".json"))))
        return (f"https://discourse.onlinedegree.iitm.ac.in/t/{data['slug']}/{data['id']}")
    return file

def ingest_dir(root_dir: str):
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
    embs = [embed_text(t) for t in texts]
    arr = np.array(embs, dtype=np.float32)
    index.add(arr)  
    metadata.extend([{"text": t, **m} for t, m in zip(texts, metas)])
    print(f"Indexed {len(texts)} chunks; total is now {index.ntotal}")

if __name__ == "__main__":
    root = "res/"
    ingest_dir(root)
    os.makedirs("res/model/", exist_ok=True)
    faiss.write_index(index, "res/model/virtual-ta.faiss")
    with open("res/model/metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)
    print("Ingestion complete. FAISS index and metadata.json are on disk.")