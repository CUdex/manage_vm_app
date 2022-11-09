import mysql.connector


class MysqlController:


    def __init__(self, param):
        self.db_connector = mysql_con = mysql.connector.connect(host=param['host'], port='3306', database=param['database'], user=param['user'], password=param['passwd'])
        self.cursor = self.db_connector.cursor(dictionary=True)

    def __del__(self):
        self.cursor.close()

    def query_executor(self, query):
        self.cursor.execute(query)
        return self.cursor

    def db_init(self):
        query = "CREATE DATABASE IF NOT EXISTS MANAGE_VM;"
