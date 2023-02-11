import socket
import os
import hashlib

global FILE_DIRECTORY
FILE_DIRECTORY = "./ServerShare"

def load_server(port=9999):
    # create a socket object
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # get local machine name
    host = socket.gethostname()

    # bind to the port
    serversocket.bind((host, port))

    # queue up to 5 requests
    serversocket.listen(5)
    
    # Error Messages
    NOT_FOUND = "NOT_FOUND\n"
    NETWORK_ERROR = "NETWORK_ERROR\n"
    # FILE_CORRUPTED = "FILE_CORRUPTED\n"
    MALFORMED_REQUEST = "MALFORMED_REQUEST\n"

    print("Server listening on port", port)

    while True:
        # establish a connection
        clientsocket, addr = serversocket.accept()

        print("Got a connection from", addr)
        
        header = clientsocket.recv(1024).decode().strip().split(" ")
        
        if header[0] == "GET_FILE_LIST":
            file_list = get_file_list()
            clientsocket.send(file_list.encode())
            
        elif header[0] == "CHECK_FILE_HASH":
            try:
                # Get the filename and hash
                filename = header[1]
                hashed = header[2]
                
                # Set the Messages
                MATCH = "MATCH " + filename + "\n"
                NONE_MATCH = "NONE_MATCH " + filename + "\n"
                
                # Format the filename to match
                filename = os.path.join(FILE_DIRECTORY, filename)
            except:
                clientsocket.send(MALFORMED_REQUEST.encode())
                continue
                
            try:
                originalHash = check_hash(filename)
            except:
                clientsocket.send(NOT_FOUND.encode()) 
                continue
                 
            if originalHash == hashed:
                clientsocket.send(MATCH.encode())            
            else:
                clientsocket.send(NONE_MATCH.encode())
                      
        elif header[0] == "DOWNLOAD":
            try:
                # Get the filename and hash
                filename = header[1]
                try:
                    offset = int(header[2])
                except:
                    offset = 0

                # Format the filename to match
                filename = os.path.join(FILE_DIRECTORY, filename)
                
            except:
                clientsocket.send(MALFORMED_REQUEST.encode())
                continue
            
            try:
               file_size = os.path.getsize(filename)
            except:
                clientsocket.send(NOT_FOUND.encode()) 
                continue
            
            try:
                # Send file is found header with file size    
                file_size = os.path.getsize(filename)
                file_size -= offset
                FILE_FOUND = "OK " + str(file_size) + "\n"
                clientsocket.send(FILE_FOUND.encode())
                
                # send the file
                chunk = send_file(filename, offset) 
                clientsocket.sendall(chunk)
            
            except:
                 clientsocket.send(NETWORK_ERROR.encode())
        
        elif header[0] == "UPLOAD":
            try:
                # Get the filename and hash
                filename = header[1]
                filesize = int(header[2])
                
                try:
                    offset = int(header[3])
                except:
                    offset = 0
                
                # Format the filename to match
                filename = os.path.join(FILE_DIRECTORY, filename)
            
            except:
                clientsocket.send(MALFORMED_REQUEST.encode())
                continue
            
            try:
                with open(filename, "ab") as f:
                    f.seek(offset)
                    data = clientsocket.recv(filesize)
                    f.write(data)
            
            except:
                clientsocket.send(NETWORK_ERROR.encode())

        else:
            clientsocket.send(MALFORMED_REQUEST.encode())
            continue
        # close the client socket
        clientsocket.close()
  
def check_hash(filename):
    # Create a hash object
    md5 = hashlib.md5()

    with open(filename, 'rb') as file:
        # Read the contents of the file in blocks
        for chunk in iter(lambda: file.read(4096), b''):
            md5.update(chunk)
    
    return md5.hexdigest()

def get_file_list():
    file_list = "FILE_LIST\n"
    for file in os.listdir(FILE_DIRECTORY):
        if os.path.isfile(os.path.join(FILE_DIRECTORY, file)):
            file_list += file + " " + str(os.path.getsize(os.path.join(FILE_DIRECTORY, file))) + "\n"
    return file_list

def send_file(filename, offset=0):
    # Open the file
    with open(filename, 'rb') as f:
        # Skip the offset
        f.seek(offset)
        # Read the file
        file_binary = f.read()
    
    f.close() 
    return file_binary
      
        
if __name__ == "__main__":
    load_server()