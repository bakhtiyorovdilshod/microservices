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

    
async def create_book(name,author_id,year):
	book = await BookList.create(name=name,author_id=author_id,year=year)
	pk = book.id
	return pk 


async def detail_book(book_id):
	get_book = await BookList.get(book_id)
	return get_book


async def delete_book(book_id):
	await BookList.delete.where(BookList.id == book_id).gino.status()
	return None


async def update_book(book_id,name,author_id,year):
	get_book = await BookList.get(book_id)
	await get_book.update(name=name,author_id=author_id,year=year).apply()
	return get_book.id 


async def list_book():
	books = await BookList.query.gino.all()
	book_list = []
	for book in books:
		book_list.append({
		'id':book.id,
		'name':book.name,
		'author_id':book.author_id,
		'year':book.year
		})
	return book_list