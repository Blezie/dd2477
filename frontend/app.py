from flask import Flask, request, render_template
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY")
ELASTIC_URL = os.getenv("ELASTIC_URL")

es_client = Elasticsearch(ELASTIC_URL, api_key=ELASTIC_API_KEY, verify_certs=False)


@app.route('/')
def home():
    return render_template('search.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    option = request.form.get('option').lower()

    if (option == 'option1'):
        body = option1(query)
    elif (option == 'option2'):
        body = option2(query)
    elif (option == 'option3'):
        body = option3(query)

    response = es_client.search(index="books", body=body)
    results = [hit["_source"] for hit in response['hits']['hits']]

    # for book in results:
    #     print(f"Book ID: {book['legacyId']}")
    #     print(f"Title: {book['title']}")
    #     print(
    #         f"Description: {book.get('description', 'No description available')[:150]}..."
    #     )
    #     print(f"Genres: {', '.join(book.get('genres', []))}")
    #     print(f"Average Rating: {book.get('averageRating', 'N/A')}")
    #     print("-" * 40)

    return render_template('results.html', query=query, option=option, results=results)


def option1(query):
    body = {
        "query": {
            "bool": {
                "should": [
                    {"match": {"genres": query}}, 
                    {
                        "match": {"description": query}
                    },
                ],
                "minimum_should_match": 1,
            }
        },
        "size": 10,
    }
    return body
def option2(query):
    body = {
        "query": {
            "match_all": {}
        },
        "size": 10
    }
    return body
def option3(query):
    body = {
        "query": {
            "match_all": {}
        },
        "size": 10
    }
    return body


if __name__ == '__main__':
    app.run(debug=True, port=5000)
