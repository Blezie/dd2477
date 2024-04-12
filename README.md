# DD2477

## Project 6: Book recommendation engine 

Compiling a reading list can be quite challenging given the number of new books that are published every year. Recommending new books automatically is an interesting, but non-trivial task requiring matching the genre a person likes, comparing the abstract of the book to the books previously read, checking what other users with similar preferences have read, etc. 

In this project the task is to: 

- Scrape the GoodReads website, and store information about some books and their reviews in Elasticsearch, [https://github.com/elastic/elasticsearch](https://github.com/elastic/elasticsearch)
- Get information from the user about her previously read books. 
- When given a query, e.g., “romance”, “adventure”, or “dragons and trolls”, generate recommendations for new books, using the query + the information about the user, the books, and their reviews. 
- Provide recommendations with short descriptions of the books.

## Setup Elasticsearch and Kibana
Docker:
- https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html#docker-compose-file

Normal:
- https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html
- https://www.elastic.co/guide/en/kibana/current/install.html

#### Create API index in Kibana for books:
##### Create API Index:
* Go to http://localhost:5601/app/enterprise_search/overview in your web browser.
* Click on "Create API index".
* Set the index name to "books".
* Choose the language analyzer as "Universal".
* Click on "Create index" to create the API index for books.
##### Generate and Save API Key:
* After creating the index, find the option to generate an API key.
* Enter a name for the API key.
* Remember to save the generated API key.
* Create ".env" file in the root folder.
* Update it with the API key you saved from the previous step.
```bash
ELASTIC_API_KEY=your_generated_api_key
ELASTIC_URL=https://localhost:9200
```
##### Configure TLS/SSL:
* Copy the http_ca.crt certificate file located in \elasticsearch-8.13.0\config\certs\. 
* Place the copied certificate in the root folder, alongside your .env file.


## Scraper

#### Scraper for GoodReads
##### How to run:
```bash
cd ./scraper
```
```bash
pip install requests python-dotenv beautifulsoup4 elasticsearch
```
```bash
python scraper.py --store <option> # option: local | elastic
```

## Machine learning

##### How to run:
```bash
cd ./frontend
```
```bash
pip install xgboost scikit-learn pandas

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