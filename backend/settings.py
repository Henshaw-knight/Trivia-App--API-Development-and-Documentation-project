from dotenv import load_dotenv 
import os

load_dotenv()

database_name = os.environ.get("database_name")
database_username = os.environ.get("database_username")
database_password = os.environ.get("database_password")
