from flask import Flask, request, render_template
from elasticsearch import Elasticsearch, NotFoundError
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY")
ELASTIC_URL = os.getenv("ELASTIC_URL")

client = Elasticsearch(ELASTIC_URL, api_key=ELASTIC_API_KEY, ca_certs="../http_ca.crt")


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
    previously_viewed_books = request.form.get('previously_viewed_books')
    option = request.form.get('option').lower()

    if (option == 'option1'):
        body = option1(query, previously_viewed_books)
    elif (option == 'option2'):
        body = option2(query, previously_viewed_books)
    elif (option == 'option3'):
        body = option3(query, previously_viewed_books)

    response = client.search(index="books", body=body)
    results = [hit["_source"] for hit in response['hits']['hits']]
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

    return render_template('results.html', query=query, previously_viewed_books=previously_viewed_books, option=option, results=results, num_results=num_results)


def option1(query, previously_viewed_books):
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
def option2(query, previously_viewed_books):
    body = {
        "query": {
            "match_all": {}
        },
        "size": 10
    }
    return body
def option3(query, previously_viewed_books):
    body = {
        "query": {
            "match_all": {}
        },
        "size": 100
    }
    return body


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
