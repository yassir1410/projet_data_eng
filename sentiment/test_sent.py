from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Initialiser l'analyseur
analyzer = SentimentIntensityAnalyzer()

# Exemple d'avis clients (en anglais)
reviews = [
    "The bank staff were very helpful and friendly.",
    "Waiting time is horrible. I hate this service.",
    "The app is okay, but sometimes it crashes.",
    "Excellent experience with customer service!",
    "Worst banking experience ever!"
]

# Analyse des sentiments
for review in reviews:
    score = analyzer.polarity_scores(review)
    sentiment = "neutral"
    if score["compound"] >= 0.05:
        sentiment = "positive"
    elif score["compound"] <= -0.05:
        sentiment = "negative"
    
    print(f"Review: {review}")
    print(f"Compound Score: {score['compound']}, Sentiment: {sentiment}")
    print("---")