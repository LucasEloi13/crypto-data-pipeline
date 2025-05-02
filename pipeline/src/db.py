from google.cloud.sql.connector import Connector
import sqlalchemy
from config import DB_CONFIG

def get_db_pool():
    connector = Connector()
    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=lambda: connector.connect(
            DB_CONFIG["INSTANCE_CONNECTION_NAME"],
            "pymysql",
            user=DB_CONFIG["DB_USER"],
            password=DB_CONFIG["DB_PASSWORD"],
            db=DB_CONFIG["DB_NAME"]
        ),
    )
    return pool
