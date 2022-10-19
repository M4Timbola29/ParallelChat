# Server
import socket
import select
import sys
from threading import *
import time


# Main menu
class mainMenu():
    menuOn = 1

    def menu():
        mainMenu.menuOn = 0
        option = ""
        options = "0", "1", "2"

        while option not in options:
            print("""\n0:Start\n1:Change port\n2:Exit""")
            option = input("")

            if option == "0":
                try:
                    print("Server Started!\n")
                    threads.multithread()
                except:
                    mainMenu.menuOn = 1
                    print("Error!")

            elif option == "1":
                try:
                    connection.port = input("Port: ")
                    mainMenu.menuOn = 1
                except:
                    print("Invalid port!")
                    mainMenu.menuOn = 1

            elif option == "2":
                print("Exiting....")
                mainMenu.menuOn = 0
                time.sleep(1)
                sys.exit()

            else:
                print("Invalid option!\n")

    # Decryption
    def decryption(message):
        decrypted = b"abcdefghijklmnopqrstuvwxyz ?!"
        encrypted = b"qwertyuiop@sdfghjklzxcvbnm!a/"
        decrypt_table = bytes.maketrans(encrypted, decrypted)

        result = ""
        result = message.translate(decrypt_table)
        message = result
        return message


# Start server
class connection():

    ip = "127.0.0.1"
    port = 1234
    headerSize = 10

    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serverSocket.bind((ip, int(port)))
    serverSocket.listen(5)
    socketsList = [serverSocket]
    clients = {}

    # Restart server
    def connect():
        ip = connection.ip
        port = connection.port
        headerSize = connection.headerSize

        connection.serverSocket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        connection.serverSocket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        connection.serverSocket.bind((ip, int(port)))
        connection.serverSocket.listen(5)
        connection.socketsList = [connection.serverSocket]
        connection.clients = {}

# Threads
class threads():
    def multithread():
        if mainMenu.menuOn == 0:
            messages().start()
            serverCommands().start()


# Thead for server commands
class serverCommands(Thread):
    def run(self):
        while mainMenu.menuOn == 0:
            command = input("")
            messages = "@clients", "@banip", "@close", "@exit", "@help"

            if command == "@clients":
                try:
                    for i in connection.socketsList:
                        print(i)
                except:
                    print("Error!")

            elif command == "@banip":
                print("Work in progress!")

            elif command == "@help":
                print("\n@clients to see clients in server.\n@banip to ban someone from the server.\n@close or @exit to close the server.\n@help for help.")

            elif command == "@close" or command == "@exit":
                try:
                    print("Closing Server...")
                    mainMenu.menuOn = 1
                    connection.serverSocket.close()
                    break
                except:
                    print("Error!")
            else:
                print("Invalid command!")

# Thread for the messages between clients
class messages(Thread):
    def reciveMsg(clientSocket):
        try:
            messageHeader = clientSocket.recv(connection.headerSize)
            if not len(messageHeader):
                return False

            msgLen = int(messageHeader.decode("utf-8").strip())
            return {"header": messageHeader, "data": clientSocket.recv(msgLen)}

        except:
            return False

    def run(self):
        connection.connect()

        while mainMenu.menuOn == 0:
            try:
                readSockets, _, exceptionSockets = select.select(
                    connection.socketsList, [], connection.socketsList)

                for notifiedSocket in readSockets:
                    if notifiedSocket == connection.serverSocket:
                        clientSocket, clientAddress = connection.serverSocket.accept()
                        user = messages.reciveMsg(clientSocket)
                        if user is False:
                            continue

                        connection.socketsList.append(clientSocket)
                        connection.clients[clientSocket] = user
                        print(
                            f"Accepted new connection from: {clientAddress[0]}:{clientAddress[1]} Username: {user['data'].decode('utf-8')}")

                    else:
                        message = messages.reciveMsg(notifiedSocket)

                        if message == False:
                            print(
                                f"Close connection from: {connection.clients[notifiedSocket]['data'].decode('utf-8')}")
                            connection.socketsList.remove(notifiedSocket)
                            del connection.clients[notifiedSocket]
                            continue

                        user = connection.clients[notifiedSocket]
                        print(
                            f"Received message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")
                        #decMsg = mainMenu.decryption(message['data'])
                        #print(f"Decrypted Message: {decMsg}")

                        for clientSocket in connection.clients:
                            if clientSocket != notifiedSocket:
                                clientSocket.send(
                                    user['header'] + user['data'] + message['header'] + message['data'])

                for notifiedSocket in exceptionSockets:
                    connection.socketsList.remove(notifiedSocket)
                    del connection.clients[notifiedSocket]
            except:
                break


# Run the program
while True:
    if mainMenu.menuOn == 1:
        mainMenu.menu()
    elif mainMenu.menuOn == 0:
        continue
