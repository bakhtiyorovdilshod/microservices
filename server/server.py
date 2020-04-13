import asyncio
from gino import Gino
from grpclib.utils import graceful_exit
from grpclib.server import Server
from book_grpc import BookServiceBase
from book_pb2 import Book,BookListResponse
import book_pb2
from google.protobuf import empty_pb2
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


class BookService(BookServiceBase):

	async def BookCreate(self, stream):
			request = await stream.recv_message()
			print(request)
			name = request.name
			author_id = request.author_id
			year = request.year
			pk = await create_book(name,author_id,year)
			response = Book(id=pk,name=name,author_id=author_id,year=year)
			await stream.send_message(response)



	async def BookDetail(self,stream):
			request = await stream.recv_message()
			book_id = request.id
			get_book = await detail_book(book_id)
			name = get_book.name
			year = get_book.year
			author_id = await Author.get(get_book.author_id)
			pk = author_id.id 
			response = Book(id=book_id,name=name,author_id=pk,year=year)

			await stream.send_message(response)


	async def BookDelete(self,stream):
		request = await stream.recv_message()
		book_id = request.id
		await delete_book(book_id)
		await stream.send_message(empty_pb2.Empty())


	async def BookUpdate(self,stream):
		request = await stream.recv_message()
		book_id = request.id
		name = request.name 
		author_id = request.author_id
		year = request.year
		book_id = await update_book(book_id,name,author_id,year)
		await stream.send_message(Book(id=book_id,name=name,author_id=author_id,year=year))


	async def BookList(self,stream):
		book_list = await list_book()
		await stream.send_message(BookListResponse(books=book_list))

     
async def main(*, host='127.0.0.1', port=50051):
    await db.set_bind('postgresql://root:123@localhost/book_shop')
    await db.gino.create_all()
    server = Server([BookService()])
    with graceful_exit([server]):
        await server.start(host, port)
        print(f'Serving on {host}:{port}')
        await server.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())