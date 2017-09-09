import logging
from flask import Flask, redirect, render_template, request
import string
import random
import pymysql

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        
        originurl = request.form['originurl']
        shorturi = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(5))
        
        conn = pymysql.connect(host='localhost',port=3306, user='root', password='test1234', db='shorturl')
        try:
            with conn.cursor() as curs:
                sql = 'insert into shorturl (short_url,origin_url) values (%s, %s)'
                curs.execute(sql,(shorturi,originurl))
            conn.commit()
        finally:
            conn.close()
        
        short_url = request.scheme+'://'+request.headers['Host']+'/'+ shorturi 
        
        return  render_template('index.html', short_url = short_url)
     
    return render_template('index.html')

@app.route('/<short_url>')
def redirect_shorturl(short_url):
    conn = pymysql.connect(host='localhost',port=3306, user='root', password='test1234', db='shorturl')
    try:
        with conn.cursor() as curs:
            sql = 'select origin_url from shorturl where short_url = %s'
            curs.execute(sql,(short_url))
            result = curs.fetchone()
            if result is not None:
                for row in result:
                    redirect_url = row
            else:
                redirect_url = "/"
    
    finally:
        conn.close()
        
    return redirect(redirect_url)

@app.route("/getlist", methods=['GET', 'POST'])
def get_list():
    conn = pymysql.connect(host='localhost',port=3306, user='root', password='test1234', db='shorturl')
    try:
        if request.method == 'POST':
            with conn.cursor() as curs:
                sql = 'delete from shorturl where short_url = %s'
                curs.execute(sql,request.form['delete'])
            conn.commit()
        
        with conn.cursor() as curs:
            sql = 'select short_url,origin_url from shorturl'
            curs.execute(sql)
            rows = curs.fetchall()
    
    finally:
        conn.close()
        
    return render_template('list.html', rows=rows)
    

if __name__ == "__main__":
    logger = logging.getLogger('werkzeug')
    handler = logging.FileHandler('access.log')
    logger.addHandler(handler)
    app.logger.addHandler(handler)
    app.run(host='0.0.0.0', port = '80')
