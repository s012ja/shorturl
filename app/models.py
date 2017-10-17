from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ShortUrl(db.Model):
    __tablename__ = 'shorturl'
    __table_args__ = {'mysql_collate': 'utf8_bin'}

    short_url = db.Column(db.String(5), primary_key=True)
    origin_url = db.Column(db.String(255), unique=True)

    def __init__(self, short_url=None, origin_url=None):
        self.short_url = short_url
        self.origin_url = origin_url

