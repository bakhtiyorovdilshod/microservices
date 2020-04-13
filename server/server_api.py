from starlette.applications import Starlette
from starlette.responses import JSONResponse,Response
from starlette.routing import Route
from hypercorn.config import Config
import asyncio
from grpclib.client import Channel
from book_grpc import BookServiceStub
from hypercorn.asyncio import serve
from starlette.requests import Request
from starlette.endpoints import HTTPEndpoint 
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from book_pb2 import Book,BookDetailRequest,BookDeleteRequest,BookUpdateRequest,BookListRequest



class CustomerHeaderMiddleware(BaseHTTPMiddleware):

	def __init__(self, app, channel=None):
		super().__init__(app)
		self.channel = channel


	async def dispatch(self,request,call_next):
		request.scope['channel'] = self.channel
		response = await call_next(request)
		return response


def connect():
	channel = Channel('127.0.0.1', 50051)
	book = BookServiceStub(channel)
	return book

def test():
	config = Config()
	config.bind = ["localhost:8080"]
	return config

def convert_to_json(book_data):
	convert = {
		"id":book_data.id,
		"name":book_data.name,
		"author_id":book_data.author_id,
		"year":book_data.year
	}
	return convert

async def book_list():
	reply = await connect().BookList(BookListRequest())
	query = []
	for i in reply.books:
		query.append(convert_to_json(i))
	return query
	


class BookCreate(HTTPEndpoint):
	async def post(self, request):
			data = await request.json()
			channel = request.scope['channel']
			book = BookServiceStub(channel)
			name = data["name"]
			author_id = data["author_id"]
			year = data["year"]
			x = await mmm(channel, name, year, author_id)
			# reply = await mmm(channel).BookCreate(Book(name=name,year=year,author_id=author_id))
			return JSONResponse({'code':"404"})

async def mmm(channel, name,year,author_id):
	book = BookServiceStub(channel)
	loop = asyncio.new_event_loop()
	reply = loop.create_task(book.BookCreate(Book(name=name,year=year,author_id=author_id)))
	loop.run_until_complete(asyncio.wait(asyncio.get_event_loop()))
	return reply


class BookDetail(HTTPEndpoint):
	async def get(self,request):
			book_id = request.path_params['book_id']
			reply = await connect().BookDetail(BookDetailRequest(id=int(book_id)))
			print(reply)
			json_data = convert_to_json(reply)
			return JSONResponse(json_data)

class BookDelete(HTTPEndpoint):
	async def get(self,request):
			book_id = request.path_params['book_id']
			reply = await connect().BookDelete(BookDeleteRequest(id=int(book_id)))
			return JSONResponse({'book':'is deleted'})


class BookUpdate(HTTPEndpoint):
	async def put(self,request): 
		data = await request.json()
		name = data["name"]
		author_id = data["author_id"]
		year = data["year"]
		book_id = data["id"]
		reply = await connect().BookUpdate(BookUpdateRequest(id=book_id,name=name,author_id=author_id,year=year))
		json_data = convert_to_json(reply)
		return JSONResponse(json_data)

class BookList(HTTPEndpoint):
	async def get(self,request):
		query = await book_list()
		return JSONResponse(query)






routes = [
	Route("/create/book", BookCreate),
	Route("/book/detail/{book_id}", BookDetail),
	Route("/book/delete/{book_id}", BookDelete),
	Route("/book/edit/{book_id}", BookUpdate),
	Route("/book/list", BookList)

]


channel =Channel('127.0.0.1', 50051)
book = BookServiceStub(channel)

middleware = [
	Middleware(CustomerHeaderMiddleware, channel=channel)

]

async def main():
	while True:
		await serve(app, test())


app = Starlette(debug=True, routes=routes, middleware=middleware)
asyncio.run(main())
asyncio.run(mmm())