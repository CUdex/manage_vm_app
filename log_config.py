import logging
from logging.handlers import RotatingFileHandler
import os

#singleton 패턴의 logging class 생성
class CustomLog:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CustomLog, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'logger'):
            self.directory_checker()
            self.logger = logging.getLogger('manage_app_logger')
            self.logger.setLevel(logging.DEBUG)
            
            log_file_path = '/var/log/manager_log/on_off_vm.log'
            max_log_size_bytes = 1024 * 1024 * 100 # 100 MB
            rotating_handler = RotatingFileHandler(log_file_path, maxBytes=max_log_size_bytes, backupCount=5, mode='a')
            formatter = logging.Formatter('%(asctime)s | %(module)s | %(levelname)s | %(message)s')
            rotating_handler.setFormatter(formatter)
            self.logger.addHandler(rotating_handler)

    # 디렉토리가 없는 경우 디렉토리 생성
    def directory_checker(self):
        direcrory_path = '/var/log/manager_log'

        if not os.path.exists(direcrory_path):
            os.makedirs(direcrory_path)