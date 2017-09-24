from flask import Flask, redirect, render_template, request
import string
import random
from models import *

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:test1234@localhost/shorturl?charset=utf8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app_config = {
    'host': '0.0.0.0',
    'port': 8080
    }

db.init_app(app)

@app.teardown_request
def shutdown_session(exception=None):
    db.session.remove()

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        
        originurl = request.form['originurl']
        shorturi = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(5))
        
        shorturl_row = shorturl(shorturi,originurl)
        
        db.session.add(shorturl_row)
        db.session.commit()
        
        short_url = request.scheme+'://'+request.headers['Host']+'/'+ shorturi 
        
        return  render_template('index.html', short_url = short_url)
     
    return render_template('index.html')

@app.route('/<short_url>')
def redirect_shorturl(short_url):
    
    row = shorturl.query.filter_by(short_url=short_url).first()
    
    if row is not None:
        redirect_url = row.origin_url
    else:
        redirect_url = "/"
          
    return redirect(redirect_url)

@app.route("/getlist", methods=['GET', 'POST'])
def get_list():
        
    if request.method == 'POST':
        del_shorturl = request.form['delete']
        
        delete_url = shorturl.query.filter_by(short_url=del_shorturl).first()
        if delete_url is None:
            pass
        else:
            db.session.delete(delete_url)
            db.session.commit()
            
    rows = shorturl.query.all()
    
    return render_template('list2.html', rows=rows)
    
if __name__ == "__main__":
    app.run(**app_config)

