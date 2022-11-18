import mysql.connector

class MysqlController:

    #인스턴스 생성 시 mysql connect 진행
    def __init__(self, param):
        print(param)
        self.db_connector = mysql_con = mysql.connector.connect(host=param['db_host'], port='3306', database=param['db_database'], user=param['db_user'], password=param['db_passwd'])
        self.cursor = self.db_connector.cursor(dictionary=True)

    def __del__(self):
        self.db_connector.close()

    #쿼리문 실행
    def query_executor(self, query):
        self.cursor.execute(query)
        return self.cursor

    #DB 미존재 시 MANAGE_VM DB 생성
    def db_init(self):
        query = "CREATE DATABASE IF NOT EXISTS MANAGE_VM;"
