from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
import json
import faiss
import pickle 

def get_embedding(text, tokenizer, model):
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    embeddings = outputs.last_hidden_state.mean(dim=1)
    return embeddings[0].numpy()

def build_embedding_text(data):
    parts = []

    if "Summary:" in data:
        parts.append(f"Summary: {data['Summary:']}")
    if "Faults:" in data:
        parts.append(f"Faults: {data['Faults:']}")
    if "General Comments:" in data:
        parts.append(f"Comments: {data['General Comments:']}")

    return "\n".join(parts)


model_name = "our_model_name"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

review_path = 'model_training/data/reviews_carsurvej.json'

with open(review_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

vectors = []
metadata = []
for review in data:
    text = build_embedding_text(review)
    embedding = get_embedding(text, tokenizer, model)
    vectors.append(embedding)
    metadata.append(review)

vectors = np.array(vectors).astype('float32')

d = vectors.shape[1]
nlist = 100
m = 32
nbits = 8

quantizer = faiss.IndexFlatL2(d)
index = faiss.IndexIVFPQ(quantizer, d, nlist, m, nbits)

print("Training FAISS index...")
index.train(vectors)  
print("Adding vectors...")
index.add(vectors)

index.nprobe = 10

faiss.write_index(index, "model_training/data/review_index.ivfpq")

with open("model_training/data/review_metadata.pkl", "wb") as f:
    pickle.dump(metadata, f)