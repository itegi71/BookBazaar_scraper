from flask import Flask, render_template ,request,send_file
from web_scrap import BookScraper
import sqlite3
import csv 
import json
from flask import jsonify

app=Flask(__name__)

def get_books(search_query=None, in_stock_only=False):
    conn=sqlite3.connect('books.db')
    c=conn.cursor()
    query="SELECT *FROM books"
    params=[]

    if search_query:
        query += " WHERE title LIKE ?"
        params.append(f"%{search_query}%")
    if in_stock_only:
        if "WHERE" in query:
            query += " AND availability LIKE '%In stock%'"
        else:
            query += " WHERE availability LIKE '%In stock%'"
    
    c.execute(query, params)
    books=c.fetchall()
    conn.close()
    return books 


@app.route('/',methods =['GET'])
def index():
    search_query = request.args.get('search')
    in_stock = request.args.get('in_stock')=='on'
    books=get_books(search_query, in_stock)
    return render_template('index.html',books=books)

@app.route("/download/csv")
def download_csv():
    conn=sqlite3.connect('books.db')
    c= conn.cursor()
    c.execute("SELECT * FROM books")
    books=c.fetchall()
    conn.close()

    filename="books_download.csv"
    with open (filename, 'w',newline='', encoding='utf-8') as f :
        writer =csv.writer (f)
        writer.writerow(['Title','price','Availability','Image URL'])
        writer.writerows(books)

    return send_file(filename,as_attachment=True)

@app.route("/download/json")
def download_json():
    conn = sqlite3.connect('books.db')
    c = conn.cursor()
    c.execute("SELECT * FROM books")
    books = c.fetchall()
    conn.close()

    books_list = [{'title': b[0], 'price': b[1], 'availability': b[2], 'image_url': b[3]} for b in books]

    filename = "books_download.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(books_list, f, indent=4)

    return send_file(filename, as_attachment=True)




@app.route('/stats')
def stats():
    # Retrieve statistics from your database
    conn = sqlite3.connect('books.db')
    cursor = conn.cursor()

    # Query the necessary data for stats (total_books, in_stock, etc.)
    cursor.execute("SELECT COUNT(*), SUM(CASE WHEN in_stock = 'Yes' THEN 1 ELSE 0 END), AVG(price), MAX(price), MIN(price) FROM books")
    stats = cursor.fetchone()

    # Safely convert the values to float before rounding
    total_books = stats[0]
    in_stock = stats[1]
    avg_price = round(float(stats[2]), 2) if stats[2] is not None else 0
    max_price = round(float(stats[3]), 2) if stats[3] is not None else 0
    min_price = round(float(stats[4]), 2) if stats[4] is not None else 0

    # Close the database connection
    conn.close()

    # Pass stats to the stats.html page
    return render_template('stats.html', total_books=total_books, in_stock=in_stock, avg_price=avg_price, max_price=max_price, min_price=min_price)

@app.route('/api/books')
def api_books():
    conn = sqlite3.connect('books.db')
    c = conn.cursor()
    c.execute("SELECT * FROM books")
    books = c.fetchall()
    conn.close()

    books_list = [{'title': b[0], 'price': b[1], 'availability': b[2], 'image_url': b[3]} for b in books]
    return jsonify(books_list)

@app.route('/api/stats')
def api_stats():
    conn = sqlite3.connect('books.db')
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM books")
    total_books = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM books WHERE availability LIKE '%In stock%'")
    in_stock = c.fetchone()[0]

    conn.close()

    return jsonify({'total_books': total_books, 'in_stock': in_stock})

if __name__ == "__main__":
    app.run(debug=True)
