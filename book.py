# from flask import Flask, request, jsonify, render_template
# import requests

# app = Flask(__name__)
# GUTENDEX_API = "https://gutendex.com/books/"

# @app.route('/book')
# def book():
#     return render_template("books_dashboard.html")

# @app.route('/search')
# def search_books():
#     query = request.args.get('q')
#     if not query:
#         return jsonify([])

#     response = requests.get(GUTENDEX_API, params={'search': query})
#     if response.status_code != 200:
#         return jsonify([])

#     data = response.json()
#     books = []
#     for book in data['results']:
#         formats = book['formats']
#         books.append({
#             "title": book['title'],
#             "author": book['authors'][0]['name'] if book['authors'] else "Unknown",
#             "download_links": {
#                 "text": formats.get("text/plain; charset=utf-8"),
#                 "pdf": formats.get("application/pdf"),
#                 "epub": formats.get("application/epub+zip"),
#                 "kindle": formats.get("application/x-mobipocket-ebook")
#             }
#         })

#     return jsonify(books)

# if __name__ == '__main__':
#     app.run(debug=True)
