from flask import Flask, redirect, render_template, request
import string
import redis
import random
import logging
from logging.handlers import RotatingFileHandler
from models import *

app = Flask(__name__)
app.config.from_pyfile('config/app.cfg')

db.init_app(app)

@app.teardown_request
def shutdown_session(exception=None):
    db.session.remove()

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        
        originurl = request.form['originurl']
        shorturi = ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(5))
        
        shorturl_row = ShortUrl(shorturi,originurl)
        
        db.session.add(shorturl_row)
        db.session.commit()
        
        short_url = request.scheme+'://'+request.headers['Host']+'/'+ shorturi 
        
        app.logger.info('Created Shorturl "%s","%s"' , shorturi,originurl)
        return  render_template('index.html', short_url = short_url)
     
    return render_template('index.html')

@app.route('/<short_url>')
def redirect_shorturl(short_url):
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    
    cachedurl = r.get(short_url)
    
    if cachedurl:
        redirect_url = cachedurl
        app.logger.info('Redirect url from cache "%s"', short_url)
    else:  
        row = ShortUrl.query.filter_by(short_url=short_url).first()
        
        if row:
            redirect_url = row.origin_url
            app.logger.info('Redirect url from db "%s"' , row.origin_url)
            r.set(short_url,row.origin_url)
        else:
            app.logger.warning('Redirect Failed - ShortUrl not found "%s"', short_url)
            redirect_url = "/"
          
    return redirect(redirect_url)

@app.route("/getlist", methods=['GET', 'POST'])
def get_list():
        
    if request.method == 'POST':
        del_shorturl = request.form['delete']
        delete_url = ShortUrl.query.filter_by(short_url=del_shorturl).first()
        if delete_url is None:
            app.logger.error('ShortUrl Delete Failed - ShortUrl not found : "%s"', del_shorturl )
            pass
        else:
            db.session.delete(delete_url)
            db.session.commit()
            app.logger.info('ShortUrl Deleted : "%s","%s"' , del_shorturl, delete_url.origin_url)

    rows = ShortUrl.query.all()
    
    return render_template('list2.html', rows=rows)
    
if __name__ == "__main__":
    
    log_fomatter = logging.Formatter('[%(levelname)s|%(filename)s:%(lineno)s,%(funcName)s] %(asctime)s > %(message)s')
    
    applog_handler = RotatingFileHandler(app.config["APP_LOGFILE"], maxBytes=app.config["APP_LOGSIZE"], backupCount=app.config["APP_LOGBACKUPCOUNT"])
    applog_handler.setFormatter(log_fomatter)
    app.logger.setLevel(logging.DEBUG)
    app.logger.addHandler(applog_handler)
    
    access_logger = logging.getLogger('werkzeug')
    access_handler = RotatingFileHandler(app.config["ACCESS_LOGFILE"], maxBytes=app.config["ACCESS_LOGSIZE"], backupCount=app.config["ACCESS_LOGBACKUPCOUNT"])
    access_logger.addHandler(access_handler)
    
    app.run(host = app.config["HOST"],port = app.config["PORT"])

