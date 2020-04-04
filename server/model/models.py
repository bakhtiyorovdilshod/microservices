from gino import Gino
db = Gino()

class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer(), primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    country = db.Column(db.String)


class BookList(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String)
    year = db.Column(db.Integer())
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))