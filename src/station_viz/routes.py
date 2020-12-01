from fastapi.routing import APIRoute
from fastapi.responses import HTMLResponse
from views.index import Home 
from views.map import Map
from config import Settings

from sqlalchemy import create_engine

config = Settings()
engine = create_engine(config.db_dsn) # database connection

# This is the file to use for defining routes and which methods are tied to them.
# I like this method for larger to medium sized apps because it's easier to understand which files
# and which methods are tied directly to the routes themselves without having to scan a large file.

home     = Home(dbh = engine) # all view objects should connect to the database if needed.  Check out the Home class for an example.
json_map = Map(dbh = engine)

routes = [
    APIRoute("/station/{id}", home.get,  methods=['GET'], response_class=HTMLResponse),
    APIRoute("/station/{id}/map", json_map.get,  methods=['GET']), 
    # APIRoute("/station/{id}/coords", json_map.get,  methods=['GET']), 
]