import asyncio


from starlette.applications import Starlette
from starlette.responses import JSONResponse,Response
from starlette.routing import Route
from hypercorn.config import Config
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

async def book_list(book):
	reply = await book.BookList(BookListRequest())
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
			reply = await book.BookCreate(Book(name=name,year=year,author_id=author_id))
			json_data = convert_to_json(reply)
			return JSONResponse(json_data)


class BookDetail(HTTPEndpoint):
	async def get(self,request):
			book_id = request.path_params['book_id']
			channel = request.scope['channel']
			book = BookServiceStub(channel)
			reply = await book.BookDetail(BookDetailRequest(id=int(book_id)))
			json_data = convert_to_json(reply)
			return JSONResponse(json_data)

class BookDelete(HTTPEndpoint):
	async def get(self,request):
			book_id = request.path_params['book_id']
			channel = request.scope['channel']
			book = BookServiceStub(channel)
			reply = await book.BookDelete(BookDeleteRequest(id=int(book_id)))
			return JSONResponse({'book':'is deleted'})


class BookUpdate(HTTPEndpoint):
	async def put(self,request): 
		data = await request.json()
		name = data["name"]
		author_id = data["author_id"]
		year = data["year"]
		book_id = data["id"]
		channel = request.scope['channel']
		book = BookServiceStub(channel)
		reply = await book.BookUpdate(BookUpdateRequest(id=book_id,name=name,author_id=author_id,year=year))
		json_data = convert_to_json(reply)
		return JSONResponse(json_data)

class BookList(HTTPEndpoint):
	async def get(self,request):
		channel = request.scope['channel']
		book = BookServiceStub(channel)
		query = await book_list(book)
		return JSONResponse(query)


routes = [
	Route("/create/book", BookCreate),
	Route("/book/detail/{book_id}", BookDetail),
	Route("/book/delete/{book_id}", BookDelete),
	Route("/book/edit/{book_id}", BookUpdate),
	Route("/book/list", BookList)

]


async def main():
	channel = Channel('127.0.0.1', 50051)
	middleware = [
	Middleware(CustomerHeaderMiddleware, channel=channel)

	]
	app = Starlette(debug=True, routes=routes, middleware=middleware)
	app = await serve(app,test())
	return app 

asyncio.run(main())
