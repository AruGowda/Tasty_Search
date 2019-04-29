import SimpleHTTPServer
import SocketServer
from urlparse import urlparse, parse_qs

PORT = 8001
RANDOM_REVIEWS_TO_PICK = 50000
TOP_20 = 20
pre_processed_food_review_data = []


TEMPLATE = """
<h4 style="margin:0">Food Review{index}</h4>
----------------------------
<p style="margin:0"><strong>product/productId:</strong> {product/productId}</p>
<p style="margin:0"><strong>review/userId:</strong> {review/userId}</p>
<p style="margin:0"><strong>review/profileName:</strong> {review/profileName}</p>
<p style="margin:0"><strong>review/helpfulness:</strong> {review/helpfulness}</p>
<p style="margin:0"><strong>review/score:</strong> {review/score}</p>
<p style="margin:0"><strong>review/time:</strong> {review/time}</p>
<p style="margin:0"><strong>review/summary:</strong> {review/summary}</p>
<p style="margin:0"><strong>review/text:</strong> {review/text}</p>
<p style="margin:0"><strong>score(D, Q):</strong> {score}</p>
<br><br>
"""


def pre_process_food_review_data():
    """
    reads raw text file and generates dict of food reviews
    """
    each_food_review_document = {}
    with open('foods.txt') as f:
        for each_line in f:
            try:
                each_line = each_line.strip()
                if each_line:
                    if each_line.startswith('product/productId'):
                        if each_food_review_document:
                            pre_processed_food_review_data.append(each_food_review_document)

                        each_food_review_document = {}
                        product_info = each_line.split(':')
                        each_food_review_document[product_info[0]] = product_info[1]
                    else:
                        food_review_info = each_line.split(':')
                        each_food_review_document[food_review_info[0]] = food_review_info[1]
            except Exception:
                print each_line


def generate_score_for_each_food_review(query):
    """
    process each food review and add score for each food review
    """
    query_length = len(query)
    for each_food_review in random_food_reviews:
        text_score = query_length - len(
            query - {each_review_text.lower() for each_review_text in each_food_review['review/text'].split(" ")})
        summary_score = query_length - len(query - {each_review_summary.lower() for each_review_summary in
                                                    each_food_review['review/summary'].split(" ")})
        score = text_score if text_score > summary_score else summary_score
        each_food_review['score'] = float(score) / query_length


class HTTPRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        if not query:
            # return index page
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
        else:
            # return top 20 food reviews
            query = {item.lower() for item in query['query'][0].split(" ")}
            generate_score_for_each_food_review(query)
            random_food_reviews.sort(key=lambda x: x['score'], reverse=True)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            rendered_template = ""
            for index, each_review in enumerate(random_food_reviews[:TOP_20], start=1):
                rendered_template += TEMPLATE.format(index=index, **each_review)
            self.wfile.write(rendered_template)


if __name__ == "__main__":
    pre_process_food_review_data()
    random_food_reviews = pre_processed_food_review_data[:RANDOM_REVIEWS_TO_PICK]
    Handler = HTTPRequestHandler
    httpd = SocketServer.TCPServer(("", PORT), Handler)
    print "Running on http://localhost:{}/".format(PORT)
    httpd.serve_forever()
