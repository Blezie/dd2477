# DD2477

## Project 6: Book recommendation engine 

Compiling a reading list can be quite challenging given the number of new books that are published every year. Recommending new books automatically is an interesting, but non-trivial task requiring matching the genre a person likes, comparing the abstract of the book to the books previously read, checking what other users with similar preferences have read, etc. 

In this project the task is to: 

- Scrape the GoodReads website, and store information about some books and their reviews in Elasticsearch, [https://github.com/elastic/elasticsearch](https://github.com/elastic/elasticsearch)
- Get information from the user about her previously read books. 
- When given a query, e.g., “romance”, “adventure”, or “dragons and trolls”, generate recommendations for new books, using the query + the information about the user, the books, and their reviews. 
- Provide recommendations with short descriptions of the books.

## Scraper

#### Scraper for GoodReads (locally)
##### How to run:
```bash
cd ./scraper
```
```bash
pip install requests beautifulsoup4 
```
```bash
python oldscraper.py
```

#### Scraper for GoodReads (elasticsearch)
##### How to run:
```bash
cd ./scraper
```
```bash
pip install requests python-dotenv beautifulsoup4 elasticsearch
```
```bash
python scraper.py --store <option> #option: local | elastic
```

## Frontend

##### How to run:
```bash
cd ./frontend
```
```bash
pip install Flask python-dotenv elasticsearch 
```
```bash
python app.py
```

The frontend can now be viewed at: [http://127.0.0.1:5000](http://127.0.0.1:5000)