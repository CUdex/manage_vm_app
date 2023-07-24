import asyncio
from mysql_lib import MysqlController
import json
import manage_lib
import log_config
import vm_utils

# 로거 인스턴스 load
custom_log = log_config.CustomLog()
logger = custom_log.logger

def vm_power_status_change(oper, server, vm_id):
    info = manage_lib.readAppInfo() 
    db_controller = MysqlController(info)

    query = f'update MANAGE_VM.vm_list set '
    
async def handle_client(reader, writer):
    while True:
        data = await reader.read(1024)
        if not data:
            break
        order = json.loads(data)
        logger.info(f"Received from client: {order}")

        try:
            oper_result = vm_utils.on_off_vm(order)
            logger.info(oper_result)
        except:
            logger.error(f"connection error: {order}")
            oper_result = 'fail connection esxi server'

        writer.write(oper_result.encode())
        await writer.drain()

    writer.close()

async def start_server():
    server = await asyncio.start_server(
        handle_client, 'localhost', 8888)

    addr = server.sockets[0].getsockname()
    logger.info(f'Serving on {addr}')
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

def start_server_in_thread():
    # asyncio 이벤트 루프를 생성
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # start_server 함수를 asyncio.run() 없이 실행
    loop.run_until_complete(start_server())