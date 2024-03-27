import requests
import json
import os
import time
from bs4 import BeautifulSoup

SCRAPE_URL = "https://www.goodreads.com/book/show/"
NDJSON_FILE_PATH = "./books/books.ndjson"

def check_legacy_id_in_ndjson(legacy_id, NDJSON_FILE_PATH):
    with open(NDJSON_FILE_PATH, "r", encoding="utf-8") as file:
        for line in file:
            book = json.loads(line)
            if str(book.get("legacyId")) == str(legacy_id):
                return True
    return False

def scrape_goodreads_book(legacy_id):
    url = f"{SCRAPE_URL}{legacy_id}"
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            script_tag = soup.find("script", id="__NEXT_DATA__")
            if script_tag:
                data = json.loads(script_tag.string)

                apollo_state = (
                    data.get("props", {}).get("pageProps", {}).get("apolloState", {})
                )
                legacy_query = f'getBookByLegacyId({{"legacyId":"{legacy_id}"}})'
                book_ref = (
                    apollo_state.get("ROOT_QUERY", {})
                    .get(legacy_query, {})
                    .get("__ref")
                )
                book_details = apollo_state.get(book_ref, {})

                contributor_ref = (
                    book_details.get("primaryContributorEdge", {})
                    .get("node", {})
                    .get("__ref", {})
                )
                author_details = apollo_state.get(contributor_ref, {})
                work_ref = book_details.get("work", {}).get("__ref", {})

                if book_ref:
                    id = book_details.get("id", {})
                    typename = book_details.get("__typename", {})
                    legacyId = book_details.get("legacyId", {})
                    webUrl = book_details.get("webUrl", {})
                    title = book_details.get("title", {})
                    titleComplete = book_details.get("titleComplete", {})
                    description = book_details.get("description", {})
                    author_name = author_details.get("name", {})
                    bookGenres = book_details.get("bookGenres", {})
                    genres = []
                    for genre in bookGenres:
                        genre_name = genre.get("genre", {}).get("name", {})
                        genres.append(genre_name)
                    details = book_details.get("details", {})
                    book_language = details.get("language", {}).get("name", {})
                    num_pages = details.get("numPages", {})
                    averageRating = (
                        apollo_state.get(work_ref, {})
                        .get("stats", {})
                        .get("averageRating", {})
                    )
                    ratingsCount = (
                        apollo_state.get(work_ref, {})
                        .get("stats", {})
                        .get("ratingsCount", {})
                    )
                    ratingsCountDist = (
                        apollo_state.get(work_ref, {})
                        .get("stats", {})
                        .get("ratingsCountDist", {})
                    )
                    textReviewsCount = (
                        apollo_state.get(work_ref, {})
                        .get("stats", {})
                        .get("textReviewsCount", {})
                    )

                    book_info = {
                        "id": id,
                        "type": typename,
                        "legacyId": legacyId,
                        "webUrl": webUrl,
                        "title": title,
                        "titleComplete": titleComplete,
                        "description": description,
                        "author": author_name,
                        "genres": genres,
                        "language": book_language,
                        "numPages": num_pages,
                        "averageRating": averageRating,
                        "ratingsCount": ratingsCount,
                        "ratingsCountDist": ratingsCountDist,
                        "textReviewsCount": textReviewsCount,
                    }

                    if not os.path.exists("./books"):
                        os.makedirs("./books")

                    with open("./books/books.ndjson", "a", encoding="utf-8") as file:
                        file.write(json.dumps(book_info, ensure_ascii=False) + "\n")


                    return book_info
                else:
                    print(f"Reference to book details not found for Legacy ID {legacy_id}.")
                    return None
            else:
                print(f"JSON data not found for Legacy ID {legacy_id}.")
                return None
        else:
            print(
                f"Failed to retrieve book page for Legacy ID {legacy_id} with status code {response.status_code}"
            )
            return None
    except requests.exceptions.Timeout:
        print(f"Request timed out for Legacy ID {legacy_id}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

for legacy_id in range(1, int(1e6)):
    if not check_legacy_id_in_ndjson(legacy_id, NDJSON_FILE_PATH):
        print(f"Scraping Legacy ID {legacy_id}...")
        book_info = scrape_goodreads_book(legacy_id)
        if book_info:
            print(f"Successfully scraped Legacy ID {legacy_id}")
            wait_time_sec = 2
            print(f"Waiting {wait_time_sec} seconds before the next request...")
            time.sleep(wait_time_sec)
    else:
        print(f"Legacy ID {legacy_id} already scraped. Skipping...")
