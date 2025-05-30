# db.py
from app import app
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os

load_dotenv()

# Check if running in test environment
if os.getenv('FLASK_ENV') == 'testing':
    app.config['MYSQL_USER'] = os.getenv('MYSQL_TEST_USER', 'root')
    app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_TEST_PASSWORD', 'root')
    app.config['MYSQL_HOST'] = os.getenv('MYSQL_TEST_HOST', '127.0.0.1')
    app.config['MYSQL_DB'] = os.getenv('MYSQL_TEST_DB', 'flaskcrud_test') # Use a test DB
else:
    app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
    app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', 'root')
    app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', '127.0.0.1')
    app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'flaskcrud')

app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)