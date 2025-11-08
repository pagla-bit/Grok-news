# sentiment/finbert.py
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

tokenizer = AutoTokenizer.from_pretrained("yiyanghkust/finbert-tone")
model = AutoModelForSequenceClassification.from_pretrained("yiyanghkust/finbert-tone")

def analyze_finbert(news_list, limit=10):
    news_list = news_list[:limit]
    inputs = tokenizer(news_list, padding=True, truncation=True, max_length=512, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
    labels = ['neutral', 'positive', 'negative']
    pos = int((probs[:, 1] > 0.5).sum().item())
    neg = int((probs[:, 2] > 0.5).sum().item())
    return pos, neg
