from influxdb import InfluxDBClient

class InfluxdbController:

    def __init__(self, param):
        self.database_name = param['database_name']
        self.measurement_name = param['measurement_name']
        username = param['username']
        password = param['password']
        port = param['port']
        host = param['host']

        # InfluxDB 클라이언트 생성
        self.client = InfluxDBClient(host, port, username, password)

    def check_database(self):
        existing_databases = self.client.get_list_database()
        # 데이터베이스가 존재하는지 확인하고 없는 경우 생성
    
        if not any(db['name'] == self.database_name for db in existing_databases):
            self.client.create_database(self.database_name)
        # 측정값이 존재하는지 확인하고 없는 경우 생성
        self.client.switch_database(self.database_name)
        existing_measurements = self.client.query('SHOW RETENTION POLICIES')
        existing_measurements = [m['name'] for m in existing_measurements.get_points()]
        if self.measurement_name not in existing_measurements:
            print('start create policy')
            self.client.create_retention_policy(
                name=self.measurement_name,
                duration='10d',
                replication=1,
                default=True,
            )

    def __del__(self):
        # 클라이언트 연결 종료
        self.client.close()

if __name__ == '__main__':
    # InfluxDB 연결 설정
    param = {
        'host': 'localhost',  # InfluxDB 호스트 주소
        'port': 8086,         # InfluxDB 포트
        'username': 'admin',  # InfluxDB 사용자 이름 (선택 사항)
        'password': 'Asdfg123!',  # InfluxDB 비밀번호 (선택 사항)
         # 데이터베이스와 측정값 정보
        'database_name': 'my_database',        # 확인하고자 하는 데이터베이스 이름
        'measurement_name': 'my_measurement'
    }

    flux_client = InfluxdbController(param)
    flux_client.check_database()
    del flux_client



    

