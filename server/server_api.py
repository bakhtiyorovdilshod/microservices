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
from book_pb2 import Book,BookDetailRequest,BookDeleteRequest,BookUpdateRequest,BookListRequest



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
			name = data["name"]
			author_id = data["author_id"]
			year = data["year"]
			reply:Book = await connect().BookCreate(Book(name=name,year=year,author_id=author_id))
			json_data = convert_to_json(reply)
			return JSONResponse(json_data)

class BookDetail(HTTPEndpoint):
	async def get(self,request):
			book_id = request.path_params['book_id']
			reply = await connect().BookDetail(BookDetailRequest(id=int(book_id)))
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
app = Starlette(routes=routes)
asyncio.run(serve(app, test()))