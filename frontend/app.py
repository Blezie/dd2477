from flask import Flask, request, render_template
from elasticsearch import Elasticsearch, NotFoundError
from dotenv import load_dotenv
import os

import sys
sys.path.append("..")
from ml.model_handler import *

load_dotenv()

app = Flask(__name__)

ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY")
ELASTIC_URL = os.getenv("ELASTIC_URL")

client = Elasticsearch(ELASTIC_URL, api_key=ELASTIC_API_KEY, ca_certs="../http_ca.crt")

# Can make more flexible by passing in the model type as a parameter
model_handler = ModelHandler("XGB")


@app.route('/')
def home():
    num_books = client.count(index='books')['count']

    return render_template('search.html', num_books=num_books)

@app.route('/view', methods=['POST'])
def view():
    book_id = request.form.get('book_id')
    
    try:
        response = client.get(index="books", id=book_id)
        book = response['_source']
    except NotFoundError:
        book = None
        
    return render_template('view.html', book=book)

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    previously_read_books = request.form.get('previously_read_books')
    option = request.form.get('option').lower()

    if (option == 'option1'):
        body = option1(query, previously_read_books)
    elif (option == 'option2'):
        body = option2(query, previously_read_books)
    elif (option == 'option3'):
        body = option3(query, previously_read_books)

    response = client.search(index="books", body=body)
    results = [hit["_source"] for hit in response['hits']['hits']]
    sortby_relevance_score(results)
    num_results = len(results)

    # Debug - print book results in the console
    # for book in results:
    #     print(f"Book ID: {book['legacyId']}")
    #     print(f"Title: {book['title']}")
    #     print(
    #         f"Description: {book.get('description', 'No description available')[:150]}..."
    #     )
    #     print(f"Genres: {', '.join(book.get('genres', []))}")
    #     print(f"Average Rating: {book.get('averageRating', 'N/A')}")
    #     print("-" * 40)

    return render_template('results.html', query=query, previously_read_books=previously_read_books, option=option, results=results, num_results=num_results)


def option1(query, previously_read_books):
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
        "size": 100,
    }
    return body
def option2(query, previously_read_books):
    body = {
        "query": {
            "match_all": {}
        },
        "size": 10
    }
    return body
def option3(query, previously_read_books):
    body = {
        "query": {
            "match_all": {}
        },
        "size": 100
    }
    return body

def sortby_relevance_score(books):
    results, nan_indices = model_handler.predict_rating(books)

    i = 0
    inc = 0
    while i < len(results):
        if i in nan_indices:
            books[i + inc]["relevance_score"] = 0
            inc += 1
        books[i+inc]["relevance_score"] = results[i]
        i += 1
    books.sort(key=lambda x: x["relevance_score"], reverse=True)
    return books



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
