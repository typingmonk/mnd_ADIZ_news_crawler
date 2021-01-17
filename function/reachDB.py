import sys
from psycopg2 import connect
sys.path.append("..")
from config import pgsql_user, pgsql_password, db_name, pgsql_host

def getDBConnect():
	return connect(
		host = pgsql_host,
		database = db_name,
		user = pgsql_user,
		password = pgsql_password
	)
