import asyncio
from mysql_lib import MysqlController
import json
import manage_lib
import log_config
import vm_utils

# 로거 인스턴스 load
custom_log = log_config.CustomLog()
logger = custom_log.logger

def vm_power_status_change(order):
    info = manage_lib.readAppInfo() 
    db_controller = MysqlController(info)
    oper = order['oper']
    server = order['server']
    vm_id = order['vm_id']

    if oper == 'on':
        query = f"update vm_list set vm_powered = 1 where vm_host_server = '{server}' and vm_idx = '{vm_id}'"
    else:
        query = f"update vm_list set vm_powered = 0 where vm_host_server = '{server}' and vm_idx = '{vm_id}'"

    logger.info(f'query start: {query}')
    db_controller.query_executor(query)
    del db_controller

    
async def handle_client(reader, writer):
    while True:
        data = await reader.read(1024)
        if not data:
            break
        order = json.loads(data)
        logger.info(f"Received from client: {order}")

        try:
            oper_result = vm_utils.on_off_vm(order)
            vm_power_status_change(order)
            logger.info(oper_result)
        except:
            logger.error(f"connection error: {order}")
            oper_result = 'fail connection esxi server'

        writer.write(oper_result.encode())
        await writer.drain()

    writer.close()

async def start_server():
    server = await asyncio.start_server(
        handle_client, '0.0.0.0', 20000)

    addr = server.sockets[0].getsockname()
    logger.info(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

def start_server_in_thread():
    # asyncio 이벤트 루프를 생성
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # start_server 함수를 asyncio.run() 없이 실행
    loop.run_until_complete(start_server())
