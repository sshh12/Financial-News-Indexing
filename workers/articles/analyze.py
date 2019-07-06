from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pickle
import os


vader_sia = SentimentIntensityAnalyzer()
with open(os.path.join('models', 'vader_lexicon.pkl'), 'rb') as lex_file:
    vader_sia.lexicon = pickle.load(lex_file)


def score_vader(text):
    return vader_sia.polarity_scores(text)['compound']