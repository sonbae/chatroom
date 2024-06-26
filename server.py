import socket
import threading
import logging

logFormat = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

fileHandler = logging.FileHandler('app.log')
fileHandler.setFormatter(logFormat)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormat)
logger.addHandler(consoleHandler)

logger.debug('initialized')

group_chats = {}
client_list = [] # TODO: replace with something else?

def broadcast_message(conn, group, message):
    logger.info('broading cast message: {}'.format(message))

    for client in group_chats[group]:
        if conn != client:
            try:
                client.send(message.encode())
            except:
                client.close()
                client_list.remove(client)
                logger.info('he died')


# def process_message(message):
#     splits = [x.strip() for x in message.splits(':')]
#     if splits[1] not in groups.keys:



def client_thread(conn, addr):
    message = conn.recv(4096).decode().strip()
    splits = [x.strip() for x in message.split(':')]
    group = splits[1]
    logger.info('splits?: {}'.format(group))

    if splits[1] not in group_chats.keys():
        logger.info('split not found, creating: {}'.format(group))
        group_chats[group] = []

    logger.info('adding conn to group: {}'.format(group))
    group_chats[group].append(conn)

    conn.send('welcome\n'.encode())
    logger.info('sent welcome to {}'.format(addr[0]))

    while True:
        try:
            message = conn.recv(4096).decode().strip()
            logger.info(message)

            if message:
                print(message)
                mes = '<' + addr[0] + '> ' + message + '\n'
                broadcast_message(
                    conn,
                    group,
                    mes,
                )
            else:
                client_list.remove(conn)
                logger.info('closing connection to {}'.format(addr[0]))
                break
        except:
            continue

def start_server(server_socket):
    server_socket.listen()
    logger.info('listening...')

    threads = []

    while True:
        # accept connection on socket 
        conn, addr = server_socket.accept()

        # append to client lists
        client_list.append(conn)

        # print ip address of client that connected
        logger.info(addr[0] + ' connected')

        t = threading.Thread(target=client_thread, args=(conn, addr))
        threads.append(t)
        t.start()


def configure_server():
    logger.info('configuring server_socket')

    # create server socket
    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM,
    )

    # allow socket reuse
    server_socket.setsockopt(
        socket.SOL_SOCKET, 
        socket.SO_REUSEADDR, 
        1,
    )

    # bind to ip/port
    server_socket.bind(
        (IP_ADDRESS, PORT)
    )

    return server_socket

def main():
    # configure server socket 
    server_socket = configure_server()

    # start server
    start_server(
        server_socket=server_socket,
    )

if __name__ == '__main__':
    IP_ADDRESS = 'localhost'
    PORT = 8000

    main()