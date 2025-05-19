from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer, DataCollatorForLanguageModeling
import torch

full_dataset = load_dataset("HuggingFaceTB/everyday-conversations-llama3.1-2k", split="train")

dataset = full_dataset.train_test_split(test_size=0.1)
train_dataset = dataset["train"]
eval_dataset = dataset["test"]

model_name = "MODEL_NAME"  
tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)
model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.bfloat16, device_map="auto")

def format_example(example):
    prompt = example["prompt"]
    response = example["completion"]
    formatted = f"<System prompt>:\n{prompt}\n<Generation>\n{response}"
    return {"text": formatted}

train_dataset = train_dataset.map(format_example)
eval_dataset = eval_dataset.map(format_example)

def tokenize(example):
    return tokenizer(example["text"], truncation=True, padding="max_length", max_length=512)

train_dataset = train_dataset.map(tokenize, batched=True, remove_columns=train_dataset.column_names)
eval_dataset = eval_dataset.map(tokenize, batched=True, remove_columns=eval_dataset.column_names)

data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

training_args = TrainingArguments(
    output_dir="./model_conversation_tune",
    evaluation_strategy="epoch", 
    num_train_epochs=10,
    report_to="none",
    eval_steps=None,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    tokenizer=tokenizer,
    data_collator=data_collator,
)

trainer.train()

trainer.save_model(model_name)