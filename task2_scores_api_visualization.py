"""
Assumptions:
- Uses DummyJSON public HTTPS API.
- Scores are mapped from 'rating' field for demonstration.
- Output chart is saved locally.
"""

import logging
import requests
import statistics
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

API_URL = "https://dummyjson.com/products"
OUTPUT_FILE = "student_scores.png"


def fetch_scores():
    resp = requests.get(API_URL, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    scores = {}
    for item in data.get("products", []):
        name = item.get("title")
        rating = item.get("rating")

        if name and isinstance(rating, (int, float)):
            scores[name[:15]] = rating

    return scores


def plot_scores(scores):
    avg_score = statistics.mean(scores.values())
    logging.info("Average score: %.2f", avg_score)

    plt.figure(figsize=(10, 5))
    plt.bar(scores.keys(), scores.values())
    plt.xticks(rotation=45, ha="right")
    plt.title("Student Test Scores")
    plt.tight_layout()
    plt.savefig(OUTPUT_FILE)
    plt.close()


def main():
    scores = fetch_scores()
    if not scores:
        logging.warning("No scores fetched")
        return

    plot_scores(scores)


if __name__ == "__main__":
    main()
