from transformers import AutoTokenizer, AutoModelForCausalLM, AutoModel
import torch

class LLM:
    def __init__(self, model_name):
        print("⏳ Step 1: Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        print("✅ Step 1: Tokenizer loaded.")

        print("⏳ Step 2: Loading model for generation...")
        self.generator = AutoModelForCausalLM.from_pretrained(model_name)
        self.generator.eval()
        print("✅ Generator model ready.")

        print("⏳ Step 3: Loading model for embeddings...")
        self.embedder = AutoModel.from_pretrained(model_name)
        self.embedder.eval()
        print("✅ Embedder model ready.")

    def __call__(self, prompt):
        inputs = self.tokenizer(prompt, return_tensors="pt")
        with torch.no_grad():
            output = self.generator.generate(
                **inputs,
                pad_token_id=self.tokenizer.eos_token_id 
        )

        full_output = self.tokenizer.decode(output[0], skip_special_tokens=True)
        generated_part = full_output[len(prompt):].strip()
        first_sentence = generated_part.split('.')[0].strip() + '.'
        return first_sentence
    
    def get_embed(self, text):
        inputs = self.tokenizer(text, return_tensors='pt', truncation=True, padding=True)
        with torch.no_grad():
            outputs = self.embedder(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1)
        return embedding[0].numpy().reshape(1, -1)