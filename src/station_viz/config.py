from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str           = "Station VIZ API"
    pagination_limit: int   = 50
    db_dsn: str             = "postgresql://hwitw:hwitw@localhost:5432/hwitw_lake"