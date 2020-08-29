from collections import Counter
from datetime import datetime, timedelta
import logging
from typing import Optional

from slack import WebClient
from slack.web.slack_response import SlackResponse

from helper import get_books_from_notion
from settings import settings


logger = logging.getLogger()

slack_token: Optional[str] = settings.slack_api_token
slack_client = WebClient(token=slack_token)


BOOK_EMOJI = ":bookkbookk:"
MAX_RANK = 3


def get_books_posted_in_last_month():
    yesterday = datetime.today() - timedelta(days=1)
    start_date = datetime(yesterday.year, yesterday.month, 1)
    end_date = datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)

    books = get_books_from_notion()

    return [b for b in books if start_date <= b.created_at <= end_date]


def get_stat_message(books):
    book_titles = [b.title for b in books]
    yesterday = datetime.today() - timedelta(days=1)
    message = [
        f"{BOOK_EMOJI} 북크북크 집계 ({yesterday.month}/{1} ~ {yesterday.month}/{yesterday.day}) {BOOK_EMOJI}",
        f"추천된 책의 수 : {len(book_titles)}권",
        f"추천한 회원 수 : {len(set(b.recommender for b in books))}명\n",
        f"{BOOK_EMOJI} 도서목록 {BOOK_EMOJI}",
    ]
    message.extend(book_titles)
    return "\n".join(message)


def get_best_recommenders_message(books):
    recommenders = [b.recommender for b in books]
    counter = Counter(recommenders)

    uniq_cv = set(counter.values())

    top_book_counts = sorted(uniq_cv, reverse=True)
    if len(top_book_counts) > MAX_RANK:
        top_book_counts = top_book_counts[:MAX_RANK]

    rankers = {r: [] for r in top_book_counts}
    for user in counter:
        if counter[user] in top_book_counts:
            rankers[counter[user]].append(user)

    messages = []
    for i, cnt in enumerate(rankers):
        if len(rankers[cnt]) > 1:
            rank_text = f"공동{i+1}위"
        else:
            rank_text = f"{i+1}위"
        messages.append(f"👑 {rank_text} {', '.join(rankers[cnt])} ({cnt}권) 👑")

    message = [f"{BOOK_EMOJI} {(datetime.today() - timedelta(days=1)).month}월의 독서왕 {BOOK_EMOJI}"]
    message.extend(messages)

    return "\n".join(message)


def post_message_to_slack_channel():
    books = get_books_from_notion()
    stat_msg = get_stat_message(books)
    best_recommender_msg = get_best_recommenders_message(books)

    final_msg = "\n".join([stat_msg, best_recommender_msg])

    post_message_res: SlackResponse = slack_client.chat_postMessage(  # type: ignore
        channel=settings.books_channel, text=final_msg,
    )
    if not post_message_res["ok"]:
        logger.error(f"######## failed to post monthly-stat message: {post_message_res['error']} #######")


today = datetime.today()
if today.day == 1:
    post_message_to_slack_channel()
