from flask import Flask, request, render_template
from elasticsearch import Elasticsearch, NotFoundError
from dotenv import load_dotenv
import os
import sys
sys.path.append("../")
from ml.model_handler import ModelHandler

load_dotenv()

app = Flask(__name__)

ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY")
ELASTIC_URL = os.getenv("ELASTIC_URL")

client = Elasticsearch(ELASTIC_URL, api_key=ELASTIC_API_KEY, ca_certs="../http_ca.crt")

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
    model_type = request.form.get('model').lower()

    if (model_type == 'model1'):
        model_type = 'XGB'
    elif (model_type == 'model2'):
        model_type = 'RF'
    elif (model_type == 'model3'):
        model_type = 'LR'

    model = ModelHandler(model_type)

    if (option == 'option1'):
        body = option1(query, previously_read_books)
    elif (option == 'option2'):
        body = option2(query, previously_read_books)
    elif (option == 'option3'):
        body = option3(query, previously_read_books)

    response = client.search(index="books", body=body)
    results = [hit["_source"] for hit in response['hits']['hits']]
    
    if (option == 'option2'):
        results = sortby_relevance_score(model, results)

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
    if previously_read_books:
        excluded_books = previously_read_books.split(",")
        must_not_clause = {"ids": {"values": excluded_books}}
    else:
        must_not_clause = {"match_none": {}}

    body = {
        "query": {
            "bool": { # Boolean query combining various conditions
                "should": [ # "Should" clause for conditions that increase relevancy score if matched
                    {"multi_match": { # Searches across multiple fields
                        "query": query, # The user's search term(s)
                        "fields": ["genres^2", "description"], # Fields to search in, with boost factor of 2 for genres
                        "type": "best_fields", # Use the best matching field to calculate the document score
                        "fuzziness": "AUTO" # Allow for automatic fuzziness based on the length of the term
                    }},
                ],
                "must_not": must_not_clause, # Clause to exclude documents (e.g., previously read books)
                "minimum_should_match": 1, # Require at least one "should" clause to match
            }
        },
        "size": 5000,  # Return up to x results
    }
    return body

def option2(query, previously_read_books):
    if previously_read_books:
        excluded_books = previously_read_books.split(",")
        must_not_clause = {"ids": {"values": excluded_books}}
    else:
        must_not_clause = {"match_none": {}}

    body = {
        "query": {
            "bool": { # Boolean query combining various conditions
                "should": [ # "Should" clause for conditions that increase relevancy score if matched
                    {"multi_match": { # Searches across multiple fields
                        "query": query, # The user's search term(s)
                        "fields": ["genres^2", "description"], # Fields to search in, with boost factor of 2 for genres
                        "type": "best_fields", # Use the best matching field to calculate the document score
                        "fuzziness": "AUTO" # Allow for automatic fuzziness based on the length of the term
                    }},
                ],
                "must_not": must_not_clause, # Clause to exclude documents (e.g., previously read books)
                "minimum_should_match": 1, # Require at least one "should" clause to match
            }
        },
        "size": 5000,  # Return up to x results
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

def sortby_relevance_score(model, books):
    results, nan_indices = model_handler.predict_rating(books)
    if len(results) == 0:
        return books
   
    # print("nan_indices", nan_indices)
    res_ind = 0
    for i in range(len(books)):
        if i in nan_indices:
            books[i]["relevance_score"] = 0
            continue
        books[i]["relevance_score"] = results[res_ind]
        res_ind += 1

    
    books.sort(key=lambda x: x["relevance_score"], reverse=True)
    return books


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
