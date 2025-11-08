# sentiment/vader.py
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('vader_lexicon', quiet=True)
sia = SentimentIntensityAnalyzer()

def analyze_vader(news_list):
    pos = neg = 0
    for text in news_list:
        scores = sia.polarity_scores(text)
        if scores['compound'] >= 0.05:
            pos += 1
        elif scores['compound'] <= -0.05:
            neg += 1
    return pos, neg
