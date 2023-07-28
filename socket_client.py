import asyncio
import json

async def send_message(vm_id, server, oper, server_pass):
    reader, writer = await asyncio.open_connection(
        'localhost', 20000)
    
    message = {'vm_id': vm_id, 'server': server, 'oper': oper, 'server_pass': server_pass}

    writer.write(json.dumps(message).encode())
    await writer.drain()

    data = await reader.read(1024)
    response = data.decode()
    print(f'Received from server: {response}')

    writer.close()
    await writer.wait_closed()

async def main():
    await send_message('71', '172.29.100.203', 'on', '@1wntpdy')

asyncio.run(main())