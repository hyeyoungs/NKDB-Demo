from elasticsearch import Elasticsearch
from flask import Flask, render_template, request

app = Flask(__name__)

# Url address of Elasticsearch
#localUrl = "http://localhost:9200"
serverUrl = "http://203.252.117.201:9200"
INDEX = "nkdb"

# Elasticsearch Connection
es = Elasticsearch(serverUrl)
#es = Elasticsearch(localUrl)
app = Flask(__name__)


@app.route('/')
def index(keyword=None):
    return render_template('index.html', keyword=keyword)

@app.route('/result', methods=['POST'])
def result(keyword=None):
    total = 10
    temp_query = request.form['keyword']
    print(temp_query)
    corpus = elasticsearchGetDocs(total, temp_query)
    return render_template('result.html', docs=corpus)

# @app.route('/content', methods=['POST'])
# def content(oneDoc=None):
#     #oneDoc = request.doc
#     return render_template('content.html')

# make query to transmit to elasticsearch
# input: isFile, select size[0, infinity]
# output: es query body(object)
def transmitQuery(size, temp_query):
    doc = {}
    if size > 0:
        doc['size'] = size

    doc['query'] = {
        "query_string":{
            "fields": ["post_title", "post_body", "file_name", "file_extracted_content"],
            "query": temp_query
        }
    }

    return doc

# count num of documents according to query body
# input: es query body
# output: num of documents(int)
def elasticsearchCount(doc):
    count = es.count(index=INDEX, body=doc)
    count = count['count']
    return count


# return data
# input: es query body
# output: json format data (object)
def elasticsearchQuery(doc):
    data = es.search(index=INDEX, body=doc)
    return data

# return documents
# input: count of document to return (int)
# output: document (object array)

def nkdbContent(SIZE, temp_query):
    doc = transmitQuery(SIZE, temp_query)
    result = elasticsearchQuery(doc)
    num = len(result)
    print("전달 받은 문서의 수 : ", num)

    corpus = []

    for oneDoc in result:
        if "file_extracted_content" in oneDoc:
            corpus.append(
                            {
                                "_id" : oneDoc["_id"],
                                "post_title" : oneDoc["_source"]["post_title"],
                                "content" : oneDoc["_source"]["file_extracted_content"],
                                "file_name" : oneDoc["_source"]["file_name"],
                                "file_url" : oneDoc["_source"]["file_download_url"],
                                "post_date": oneDoc["_source"]["post_date"],
                                "post_writer": oneDoc["_source"]["post_writer"],
                                "published_institution_url": oneDoc["_source"]["published_institution_url"],
                                "top_category": oneDoc["_source"]["top_category"]
                            }
                         )
        else:
            corpus.append(
                {
                    "_id": oneDoc["_id"],
                    "post_title": oneDoc["_source"]["post_title"],
                    "content": oneDoc["_source"]["post_body"],
                    "post_date": oneDoc["_source"]["post_date"],
                    "post_writer": oneDoc["_source"]["post_writer"],
                    "published_institution_url": oneDoc["_source"]["published_institution_url"],
                    "top_category": oneDoc["_source"]["top_category"]
                }
            )
        print(corpus)
    return corpus


def elasticsearchGetDocs(total, temp_query):
    corpus = []
    data = nkdbContent(10, temp_query)
    # print(data)
    for oneDoc in data:
        corpus.append(oneDoc)
    print("응답 받아 전송한 문서의 수 : ", total)

    return corpus

if __name__ == '__main__':
    #app.run()
    app.run(host="0.0.0.0",port=5000, debug=True)

