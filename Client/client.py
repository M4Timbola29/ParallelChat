# client
import socket
import errno
import sys
from threading import *
import time

# MainMenu
class mainMenu():
    menuOn = 1

    def menu():
        mainMenu.menuOn = 0
        option = ""
        options = "0", "1", "2", "3", "4"

        while option not in options:
            print(
                """\n0:Auto Connect\n1:Manual Connection\n2:List of servers\n3:Change Username\n4:Exit\n""")
            option = input("")

            if option == "0":
                connection.ip = "127.0.0.1"
                connection.port = "1234"
                try:
                    connection.connect()
                except:
                    print("Invalid ip address or port!")
                    mainMenu.menuOn = 1

            elif option == "1":
                connection.ip = input("Input the server ip: ")
                connection.port = input("Input the server port: ")

                try:
                    connection.connect()
                except:
                    print("Invalid ip address or port!")
                    mainMenu.menuOn = 1

            elif option == "2":
                try:
                    file = open("data/ServerList.txt", "rt")
                    print("")
                    for line in file:
                        print(line)
                    file.close()
                except:
                    print("File not found!")
                mainMenu.menuOn = 1

            elif option == "3":
                try:
                    connection.myUsername = input("Type your new username: ")
                    connection.username = connection.myUsername.encode("utf-8")
                except:
                    continue
                mainMenu.menuOn = 1

            elif option == "4":
                print("Exiting....")
                mainMenu.menuOn = 0
                time.sleep(1)
                sys.exit()

            else:
                print("Invalid option!\n")

    # Encryption
    def encryption(message):
        decrypted = b"abcdefghijklmnopqrstuvwxyz ?!"
        encrypted = b"qwertyuiop@sdfghjklzxcvbnm!a/"
        encrypt_table = bytes.maketrans(decrypted, encrypted)

        result = ""
        result = message.translate(encrypt_table)
        message = result
        return message

    # Decryption
    def decryption(message):
        decrypted = b"abcdefghijklmnopqrstuvwxyz ?!"
        encrypted = b"qwertyuiop@sdfghjklzxcvbnm!a/"
        decrypt_table = bytes.maketrans(encrypted, decrypted)

        result = ""
        result = message.translate(decrypt_table)
        message = result
        return message

# Connection
class connection():
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    headerSize = 10
    myUsername = input("Username: ")
    username = myUsername.encode("utf-8")
    ip = "127.0.0.1"
    port = 1234

    # Refresh connection / new connection
    def connect():
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        headerSize = connection.headerSize
        myUsername = connection.myUsername
        port = int(connection.port)

        #clientSocket = connection.clientSocket
        clientSocket.connect((connection.ip, port))
        clientSocket.setblocking(False)
        print(f"\nConnected to the server {connection.ip}:{port}!")

        username = connection.username
        usernameHeader = f"{len(username):<{connection.headerSize}}".encode(
            "utf-8")
        clientSocket.send(usernameHeader + username)
        connection.clientSocket = clientSocket

        connection.multiThread()

    # Start MultiThreading
    def multiThread():
        if mainMenu.menuOn == 0:
            send().start()
            receive().start()

# Thread to send messages
class send(Thread):
    def run(self):
        headerSize = connection.headerSize
        clientSocket = connection.clientSocket

        # Send
        #message = input(f"{myUsername}: ")
        while mainMenu.menuOn == 0:
            message = input("")
            messages = "@exit", "@close"

            if message not in messages and message != "":
                message = message.encode("utf-8")
                messageHeader = f"{len(message):<{headerSize}}".encode("utf-8")
                try:
                    encMsg = mainMenu.encryption(message)
                    clientSocket.send(messageHeader + encMsg)
                except:
                    print("The server is no longer available!")
                    connection.clientSocket.close()
                    mainMenu.menuOn = 1

            # commands
            elif message.lower() in messages:
                connection.clientSocket.close()
                mainMenu.menuOn = 1

# Thread receive messages
class receive(Thread):
    def run(self):
        headerSize = connection.headerSize
        clientSocket = connection.clientSocket
        username = connection.username

        while mainMenu.menuOn == 0:
            try:
                # Receive
                usernameHeader = clientSocket.recv(headerSize)
                if not len(usernameHeader):
                    print("Connection closed by the server")
                    break

                userLen = int(usernameHeader.decode("utf-8").strip())
                username = clientSocket.recv(userLen).decode("utf-8")

                messageHeader = clientSocket.recv(headerSize)
                msgLen = int(messageHeader.decode("utf-8").strip())
                message = clientSocket.recv(msgLen).decode("utf-8")
                fMsg = mainMenu.decryption(message)

                print(f"{username}: {fMsg}")

            # Error checking
            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    #print("Reading error", str(e))
                    mainMenu.menuOn = 1
                    break

            except Exception as e:
                print("General Error", str(e))
                mainMenu.menuOn = 1
                break


# Run the program
while True:
    if mainMenu.menuOn == 1:
        mainMenu.menu()
    elif mainMenu.menuOn == 0:
        continue
