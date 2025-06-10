import faiss
import pickle
import torch

class RAG_Parser:
    def __init__(self, index_path, metadata_path, model):
        print("⏳ Step 1: Loading FAISS index...")
        self.index = faiss.read_index(index_path)
        print("✅ Step 1: FAISS index loaded.")

        print("⏳ Step 2: Loading metadata...")
        with open(metadata_path, "rb") as f:
            self.metadata = pickle.load(f)
        print("✅ Step 2: Metadata loaded.")

        print("⏳ Step 3: Integrate model...")
        self.model = model
        print("✅ Step 3: Model is ready.")
       

    def embed(self, text):
        return self.model.get_embed(text)

    def query(self, question, top_k=5):
        query_vec = self.embed(question)
        _, indices = self.index.search(query_vec, top_k)
        results = [self.metadata[i] for i in indices[0]]
        seen = set()
        unique_dicts = []

        for d in results:
            items = tuple(sorted(d.items()))
            if items not in seen:
                seen.add(items)
                unique_dicts.append(d)
        return unique_dicts

    def format_context(self, results):
        return "\n\n---\n\n".join([
            f"Model name: : {r.get('Model name: ', '')}\nSummary: {r.get('Summary:', '')}\nFaults: {r.get('Faults:', '')}\nComments: {r.get('General Comments:', '')}"
            for r in results
        ])

    def generate_prompt(self, question, top_k=5):
        results = self.query(question, top_k)
        context = self.format_context(results)
        return f"<Context>:\n{context}"