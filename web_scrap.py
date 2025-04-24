import requests
from bs4 import BeautifulSoup
import csv
import time
import json
import argparse
import sqlite3

class Book:
    def __init__(self, title , price , availability, image_url):
        self.title =title 
        self.price =price 
        self.availability=availability
        self.image_url=image_url

    def to_dict(self):
        return{
            "title":self.title,
            "price":self.price,
            "availability":self.availability,
            "image_url":self.image_url
        }

class BookScraper:
    def __init__(self, base_url,pages):
        self.base_url=base_url
        self.pages=pages 
        self.books=[]# list to hold Book objects 

    def fetch_page(self, page_number):
        if page_number ==1:
            url="http://books.toscrape.com/index.html"

        else:
            url=f"{self.base_url}page-{page_number}.html"

        
        response=requests.get(url)
        if response.status_code==200:
            print(f"page {page_number}scraped successfully.")
            return response.text 
        else:
            print(f"Failed to fetch page {page_number}")
            return None
        

    def parse_books(self, html):#parse the html content and extracts the boo details 
        soup=BeautifulSoup(html, 'html.parser')
        articles =soup.find_all('article',class_='product_pod')

        for article in articles:
            #Extract title 
            title = article.h3.a['title']
            #price 
            price =article.find('p', class_='price_color').text.strip()
            availability=article.find('p',class_='instock availability').text.strip()

            image_relative =article.find('img')['src']
            image_url='http://books.toscrape.com/' + image_relative.replace('../', '')

            #create a Book object and append to list 
            book=Book(title, price, availability, image_url)
            self.books.append(book)


    def  scrape(self):
        #loops through pages , fetches and parses them .
        for page in range (1, self.pages + 1):
            html = self.fetch_page(page) 
            if html:
                self.parse_books(html)
            time.sleep(1) # im trying to be nice to the server 


    def save_to_csv(self, filename):
        with open(filename,'w',newline='',encoding='utf-8') as file:
            writer=csv.writer(file) 
            writer.writerow(['Title','Price','Availability','Image URL'])

            for book in self.books : 
                writer.writerow([book.title,book.price,book.availability,book.image_url])
            print(f"\nScraped data saved to {filename}")

    def save_to_json(self, filename):
        with open(filename,'w',encoding='utf-8') as file:
            data=[book.to_dict() for book in self.books]
            json.dump(data,file,indent=4)
        print(f"\nScraped data saved to {filename}")

    def save_to_db(self, db_name='books.db'):
        conn= sqlite3.connect(db_name)
        c=conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS books 
                   (title TEXT, price TEXT, availability TEXT,image_url TEXT)''')
        
        for book in self.books:
            c.execute ("INSERT INTO books VALUES (?,?,?,?)",
                       (book.title,book.price, book.availability, book.image_url))
        conn.commit()
        conn.close()
        print(f"\nScraped data saved to {db_name}")

     
if __name__ =="__main__":
    parser= argparse.ArgumentParser(description="scrape book data from books.toscrape.com")
    parser.add_argument("--pages",type=int, default=5 ,help="number of pages to scrap")
    parser.add_argument("--csv",type=str, help="CSV filename to save scraped data")
    parser.add_argument("--json",type=str, help="JSON filename to save scraped data")

    args=parser.parse_args()

    #instantiate the scraper with base url and the number of pages to scrape 
    base_url='http://books.toscrape.com/catalogue/'
     
    scraper = BookScraper(base_url, args.pages)
    
    scraper.scrape()
    if args.csv:
        scraper.save_to_csv(args.csv)
    if args.json:
        scraper.save_to_json(args.json)
    
    scraper.save_to_db()


    

