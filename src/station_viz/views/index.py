from fastapi import Request
from fastapi.templating import Jinja2Templates
from types import SimpleNamespace
import logging
import sqlalchemy

logger    = logging.getLogger("uvicorn")
templates = Jinja2Templates(directory="templates")

## Static class for now
class Home:

    dbh = False # To use the database you just need to have this in your own class

    # Keep SQL statements in head of class for easy reference later
    sql = SimpleNamespace(
        # This query is just an exampmle but it would be nice to pull station meta-data and display it on the main page.
        station_info = """
            SELECT * FROM public.lcd_incoming WHERE station_id = {station_id} LIMIT 1
        """
    )

    def __init__(self, **kwargs):
        for attr, value in kwargs.items():
            if hasattr(self, attr): # only sets class properties if they exist
                setattr(self, attr, value)    
     
        if not hasattr(self, "dbh"):
            logger.error("Could not databse handle not set in Home::__init__.")

    def get_station_info(self, station_id = False):
        """get_station_info

        This is a basic template method for selecting information for a database.  SQL is stored outside the function so it's
        easier to reference as some SQL queries get quite large, it's difficult to read code with any conciseness.

        Args:
            station_id (bool, optional): [description]. Defaults to False.
        """
       
        # result = connection.execute(sql_statement)
        # 
        ## Fetch one result 
        # result.fetchone()
        #
        ## Fetach all results
        # result.fetchall()
        #
        sql    = self.sql.station_info.format(station_id = station_id)
        result = self.dbh.execute(sql).fetchone()
        logger.info(sql)

        if type(result) == sqlalchemy.engine.result.RowProxy:
            return dict(result)
        
        ## Optimistic patter: return False by default
        return False

    # TBD: clean input on id and type it correctly
    def get(self, request: Request, id: str):
        """index()

        This method handles the routing for the main app.

        Returns:
            dict: JSON Response
        """
       
        self.get_station_info(station_id = id)
 
        #print("config", config)
        return templates.TemplateResponse("index.html", {"request": request, "id": id})