from mysql_lib import MysqlController
import re

#app.conf 파일에 있는 db정보를 가져오는 함수
def readDatabaseInfo():
    db_info = {}
    #정규식을 이용하여 필요한 정보만 dictionary array에 저장하기 위해 정규식 설정
    re_match = re.compile('^db')
    f = open('/etc/app.conf')
    readText = f.readlines()
    
    for line in readText:
        #db로 시작하는 line이면 key와 value로 split 후 사용
        if re_match.match(line):
            split_text = line.split("=")
            db_info[split_text[0]] = split_text[1].strip('\n')
    return db_info

db_connect_info = readDatabaseInfo()
db_controller = MysqlController(db_connect_info)
query = "select * from information_schema.schemata" #테스트용 쿼리
db_cursor = db_controller.query_executor(query)

for raw in db_cursor:
    print(raw)