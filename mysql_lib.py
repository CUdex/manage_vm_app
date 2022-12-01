import mysql.connector

class MysqlController:

    #인스턴스 생성 시 mysql connect 진행
    def __init__(self, param):
        self.db_connector = mysql.connector.connect(host=param['db_host'], port='3306', database=param['db_database'], user=param['db_user'], password=param['db_passwd'])
        self.db_init()

    def __del__(self):
        self.db_connector.close()

    #쿼리문 실행
    def query_executor(self, query):
        cursor = self.db_connector.cursor(dictionary=True)
        cursor.execute(query)
        
        if query[0] == 's':
            result = cursor.fetchall()
            cursor.close()
            return result

        self.db_connector.commit()
        cursor.close()
        

    #DB 미존재 시 MANAGE_VM DB 생성
    def db_init(self):
        cursor = self.db_connector.cursor(dictionary=True)
        query = "CREATE DATABASE IF NOT EXISTS MANAGE_VM;"
        cursor.execute(query)
        cursor.close()
        
