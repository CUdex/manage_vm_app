from influxdb_client import InfluxDBClient, OrganizationsApi, BucketsApi, Point
from influxdb_client.client.write_api import SYNCHRONOUS

class InfluxdbController:

    def __init__(self, param):
        self.bucket_name = param['influx_bucket_name']
        self.org = param['influx_org']
        token = param['influx_token']
        url = param['influx_url']

        # InfluxDB 클라이언트 생성
        self.client = InfluxDBClient(url=url, token=token)

    def check_init(self):
        exist_org = False

        #org 확인 후 없을 경우 생성
        orgs_api = OrganizationsApi(self.client)
        existing_orgs = orgs_api.find_organizations()

        for org in existing_orgs:
            if org.name == self.org:
                exist_org = True
                org_id = org.id
        
        if not exist_org:
            org = orgs_api.create_organization(name=self.org)
            org_id = org.id

        #bucket 확인 후 없을 경우 생성
        buckets_api = BucketsApi(self.client)
        exist_bucket = buckets_api.find_bucket_by_name(self.bucket_name)
        print(exist_bucket)

        if not exist_bucket:
            retention_rule = {
                'type': 'expire',
                'everySeconds': 604800
            }
            buckets_api.create_bucket(bucket_name=self.bucket_name, org_id=org_id, retention_rules=retention_rule)

    def __del__(self):
        # 클라이언트 연결 종료
        self.client.close()

    def write_data(self, server_ip, data):
        # influxdb에 데이터 저장
        point = Point('server_values') \
            .tag(key='server_ip',value=server_ip) \
            .field('cpu', int(data['cpu_percentage'])) \
            .field('memory', int(data['memory_percentage'])) \
            .field('disk', int(data['disk_percentage']))
        
        write_api = self.client.write_api()
        write_api.write(bucket=self.bucket_name, org=self.org, record=point)
        write_api.close()