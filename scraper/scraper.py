import argparse
import requests
import json
import os
import time
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch

SCRAPE_URL = "https://www.goodreads.com/book/show/"
ELASTIC_API_KEY = "SmtaMWZZNEIzTENBN1NSbFV4MnI6QWpDZTgwUzVUcU9YSGlVZzU5Q18zZw=="
ELASTIC_URL = "https://localhost:9200"
ELASTIC_CERTS = "./http_ca.crt"  # Path to the CA certificate from Elasicsearch
WAIT_BETWEEN_REQUESTS = 2

client = Elasticsearch(ELASTIC_URL, api_key=ELASTIC_API_KEY, ca_certs=ELASTIC_CERTS)

try:
    client.info()
except Exception as e:
    print(f"Failed to connect to Elasticsearch: {e}")
    exit(1)


def book_exists_in_ndjson(legacy_id):
    with open("./books/books.ndjson", "r", encoding="utf-8") as file:
        for line in file:
            book = json.loads(line)
            if str(book.get("legacyId")) == str(legacy_id):
                return True
    return False


def book_exists_in_elasticsearch(legacy_id):
    try:
        ans = client.exists(index="books", id=str(legacy_id))
        print(ans)
        return ans
    except Exception as e:
        print(f"Error checking book existence in Elasticsearch: {e}")
        return False


def index_book_in_elasticsearch(book_info):
    try:
        response = client.index(
            index="books", id=str(book_info["legacyId"]), body=book_info
        )
        print(f"Book indexed with response: {response}")
    except Exception as e:
        print(f"Error indexing book: {e}")


def scrape_goodreads_book(legacy_id, store="local"):
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

                    if store == "elastic":
                        # Index book in Elasticsearch
                        index_book_in_elasticsearch(book_info)
                    elif store == "local":
                        # Save book info to NDJSON file
                        if not os.path.exists("./books"):
                            os.makedirs("./books")
                        with open(
                            "./books/books.ndjson", "a", encoding="utf-8"
                        ) as file:
                            file.write(json.dumps(book_info, ensure_ascii=False) + "\n")

                    return book_info
                else:
                    print(
                        f"Reference to book details not found for Legacy ID {legacy_id}."
                    )
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


def main(store):
    for legacy_id in range(1, int(1e6)):
        exists_local = book_exists_in_ndjson(legacy_id)
        exists_elastic = book_exists_in_elasticsearch(legacy_id)

        if store == "local" and not exists_local:
            print(f"Scraping Legacy ID {legacy_id} to local...")
            book_info = scrape_goodreads_book(legacy_id, store="local")
            if book_info:
                print(f"Successfully scraped Legacy ID {legacy_id} locally.")
        elif store == "elastic" and not exists_elastic:
            print(f"Scraping Legacy ID {legacy_id} to Elasticsearch...")
            book_info = scrape_goodreads_book(legacy_id, store="elastic")
            if book_info:
                print(f"Successfully scraped Legacy ID {legacy_id} to Elasticsearch.")
        else:
            print(f"Legacy ID {legacy_id} already exists in {store}. Skipping...")
            continue

        print(f"Waiting {WAIT_BETWEEN_REQUESTS} seconds before the next request...")
        time.sleep(WAIT_BETWEEN_REQUESTS)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Scrape book data to local or Elasticsearch."
    )
    parser.add_argument(
        "--store",
        type=str,
        choices=["local", "elastic"],
        help="Where to store the scraped data. Options: local, elastic.",
    )
    args = parser.parse_args()

    if args.store:
        main(args.store)
    else:
        print(
            "No --store option was provided. Use --store local, --store elastic to specify where to store the scraped data."
        )
