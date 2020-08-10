from collections import Counter
from datetime import datetime, timedelta
from typing import Optional

from slack import WebClient

from helper import get_books_from_notion
from settings import settings


slack_token: Optional[str] = settings.slack_api_token
slack_client = WebClient(token=slack_token)


def get_books_posted_in_last_month():
    yesterday = datetime.today() - timedelta(days=1)
    start_date = datetime(yesterday.year, yesterday.month, 1)
    end_date = datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)

    books = get_books_from_notion()

    return [b for b in books if start_date <= b.created_at <= end_date]


def get_stat_message(books):
    book_titles = [b.title for b in books]
    message = [f"📖 지난 한달 동안 북크북크에 {len(book_titles)}권의 책이 모였어요 📖"]
    message.extend(book_titles)
    return "\n".join(message)


def get_best_recommenders_message(books):
    recommenders = [b.recommender for b in books]

    counter = Counter(recommenders)
    most = max(list(counter.values()))
    bests = [c for c in counter if counter[c] == most]

    for i in range(len(bests)):
        bests[i] = f"🎉🌟 {bests[i]} 🌟🎉 ({counter[bests[i]]}권)"

    message = [f"👑 {(datetime.today() - timedelta(days=1)).month}월의 독서왕 👑"]
    message.extend(bests)

    return "\n".join(message)


def post_message_to_slack_channel():
    books = get_books_from_notion()
    stat_msg = get_stat_message(books)
    best_recommender_msg = get_best_recommenders_message(books)

    print(stat_msg)
    print(best_recommender_msg)


post_message_to_slack_channel()
