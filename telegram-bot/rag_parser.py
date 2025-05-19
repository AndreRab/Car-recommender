import faiss
import pickle
import torch
from transformers import AutoTokenizer, AutoModel

class RAG_Parser:
    def __init__(self, index_path, metadata_path, model_name):
        self.index = faiss.read_index(index_path)
        with open(metadata_path, "rb") as f:
            self.metadata = pickle.load(f)

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()

    def embed(self, text):
        inputs = self.tokenizer(text, return_tensors='pt', truncation=True, padding=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1)
        return embedding[0].numpy().reshape(1, -1)

    def query(self, question, top_k=5):
        query_vec = self.embed(question)
        distances, indices = self.index.search(query_vec, top_k)
        results = [self.metadata[i] for i in indices[0]]
        return results

    def format_context(self, results):
        return "\n\n---\n\n".join([
            f"Summary: {r.get('Summary:', '')}\nFaults: {r.get('Faults:', '')}\nComments: {r.get('General Comments:', '')}"
            for r in results
        ])

    def generate_prompt(self, question, top_k=5):
        results = self.query(question, top_k)
        context = self.format_context(results)
        return f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"