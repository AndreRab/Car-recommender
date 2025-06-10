from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
import json
import faiss
import pickle 
from tqdm import tqdm
import multiprocessing as mp

mp.set_start_method("spawn", force=True)

def get_embedding(text, tokenizer, model):
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    embeddings = outputs.last_hidden_state.mean(dim=1)
    return embeddings[0].numpy()

def build_embedding_text(data):
    parts = []

    if "Model name: " in data:
        parts.append(f"Model name:  {data['Model name: ']}")
    if "Summary:" in data:
        parts.append(f"Summary: {data['Summary:']}")
    if "Faults:" in data:
        parts.append(f"Faults: {data['Faults:']}")
    if "General Comments:" in data:
        parts.append(f"Comments: {data['General Comments:']}")

    return "\n".join(parts)


model_name = "AndreiRabau/gpt-car-recommender-NEW"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

review_path = 'model-training/data/reviews_carsurvej.json'

with open(review_path, 'r', encoding='utf-8') as f:
    data = json.load(f)
    data = [json.loads(entry) for entry in data]

vectors = []
metadata = []
for review in tqdm(data): 
    text = build_embedding_text(review)
    embedding = get_embedding(text, tokenizer, model)
    vectors.append(embedding)
    metadata.append(review)

vectors = np.array(vectors).astype('float32')
d = vectors.shape[1]

print("Building FAISS IndexFlatL2...")
index = faiss.IndexFlatL2(d)
index.add(vectors)

faiss.write_index(index, "telegram-bot/data/review_index.flatl2")
with open("telegram-bot/data/review_metadata.pkl", "wb") as f:
    pickle.dump(metadata, f)

print("Index and metadata saved successfully.")