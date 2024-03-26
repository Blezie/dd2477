# DD2477

## Project 6: Book recommendation engine 

Compiling a reading list can be quite challenging given the number of new books that are published every year. Recommending new books automatically is an interesting, but non-trivial task requiring matching the genre a person likes, comparing the abstract of the book to the books previously read, checking what other users with similar preferences have read, etc. 

In this project the task is to: 

- Scrape the GoodReads website, and store information about some books and their reviews in Elasticsearch, [https://github.com/elastic/elasticsearch](https://github.com/elastic/elasticsearch)
- Get information from the user about her previously read books. 
- When given a query, e.g., “romance”, “adventure”, or “dragons and trolls”, generate recommendations for new books, using the query + the information about the user, the books, and their reviews. 
- Provide recommendations with short descriptions of the books.

# Scraper for GoodReads
```js
pip install requests beautifulsoup4 
```

python main.py
