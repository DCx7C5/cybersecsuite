

async def asgi_server(app, scope, receive, send):
	await app(scope, receive, send)
