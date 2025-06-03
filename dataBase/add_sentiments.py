from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from connection import get_db_connection  # import your connection function

def get_sentiment(compound_score):
    if compound_score >= 0.05:
        return "positive"
    elif compound_score <= -0.05:
        return "negative"
    else:
        return "neutral"

def analyze_and_store_sentiment():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        analyzer = SentimentIntensityAnalyzer()

        cursor.execute("SELECT review_id, review_text FROM review;")
        reviews = cursor.fetchall()

        for review_id, review_text in reviews:
            score = analyzer.polarity_scores(review_text)
            compound_score = score["compound"]
            sentiment = get_sentiment(compound_score)

            cursor.execute(
                """
                INSERT INTO sentiments (review_id, compound_score, sentiment)
                VALUES (%s, %s, %s)
                """,
                (review_id, compound_score, sentiment)
            )

        conn.commit()
        print(f"Sentiment analysis complete. {len(reviews)} records inserted into sentiments table.")

    except Exception as e:
        print(f"Error during sentiment analysis and storage: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    analyze_and_store_sentiment()
