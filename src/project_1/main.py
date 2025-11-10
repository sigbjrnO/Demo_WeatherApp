from aiohttp import web
import routes
import database


app = web.Application()
app.add_routes(routes.routes)

app.on_startup.append(database.start_engine)
app.on_cleanup.append(database.stop_engine)

web.run_app(app)