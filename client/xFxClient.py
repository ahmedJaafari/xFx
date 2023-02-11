import os
import socket
import hashlib

class XFxClient:
    
    def __init__(self, host='localhost', port=9999, max_receive=1024, share_directory = "./ClientShare"):
        # Set Port & Host
        self.host = host
        self.port = port
        
        self.share_directory = share_directory
        self.max_receive = max_receive
    
    def check_file_hash(self, filename):
        # Connect to the server
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        req = f"CHECK_FILE_HASH {filename} "
        
        try:
            hash = self._check_hash(os.path.join(self.share_directory, filename))
        except:
            return "File Not Found"
        
        req += hash + "\n"
        
        self.client_socket.sendall(req.encode())
        
        header = self.client_socket.recv(self.max_receive).decode().strip()
        
        self.close()
        
        if header.startswith("MATCH"):
            return True
        
        elif header.startswith("NONE_MATCH"):
            return False
        
        return "Error: " + header
    
    def get_file_list(self):
        # Connect to the server
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        self.client_socket.sendall("GET_FILE_LIST".encode())
        data = self.client_socket.recv(self.max_receive).decode().strip()
        self.close()
        if data.startswith("FILE_LIST"):
            directory_dict = {}
            lines = data.split("\n")
            for line in lines[1:]:
                filename, filesize = line.split(" ")
                directory_dict[filename] = int(filesize)
        
        else:
            return "Error: " + data
            
        return directory_dict
        
    def download(self, filename, offset=0):
        # Connect to the server
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        req = f"DOWNLOAD {filename}"
        if offset:
            req += " " + str(offset) + "\n"
        else:
            req += "\n"
        
        self.client_socket.sendall(req.encode())
        
        filename = os.path.join(self.share_directory, filename)
        
        header = self.client_socket.recv(self.max_receive).decode().strip()
        
        if header.startswith("OK"):    
            with open(filename, "ab") as f:
                while True:
                    data = self.client_socket.recv(self.max_receive)
                    if not data:
                        break
                    f.write(data)
                             
            f.close()
            
            self.close()
            
            return True   
        
        self.close()
        return False
    
    
    def resume_download(self, filename):        
        filesize = os.path.getsize(os.path.join(self.share_directory, filename))
        
        return self.download(filename, offset=filesize)

    def upload(self, filename, offset=0):
        # Connect to the server
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        try:
            filesize = os.path.getsize(os.path.join(self.share_directory, filename))
        except:
            return "File Not Found"
        
        req = f"UPLOAD {filename} {filesize}"
        
        if offset:
            req += " " + str(offset) + "\n"
        else:
            req += "\n"
        
        self.client_socket.sendall(req.encode())
        print(req)
        
        file_data = self._send_file(os.path.join(self.share_directory, filename), offset=offset)
                        
        try:
            self.client_socket.sendall(file_data)
            self.close()
            return True
        
        except:
            self.close()
            return "Connection to the server has been lost. Terminating."
    
       
    def resume_upload(self, filename):        
        directory_dict = self.get_file_list()   
        print(directory_dict) 
        try:   
            filesize = directory_dict[filename]
        except:
            return "File Not Found"
                
        return self.upload(filename=filename, offset=filesize)
    
    def _check_hash(self, filename):
        # Create a hash object
        md5 = hashlib.md5()

        with open(filename, 'rb') as file:
            # Read the contents of the file in blocks
            for chunk in iter(lambda: file.read(4096), b''):
                md5.update(chunk)
        
        return md5.hexdigest()
    
    def _send_file(self, filename, offset=0):
        # Open the file
        with open(filename, 'rb') as f:
            f.seek(offset)
            # Read the file
            file_data = f.read()
        
        f.close()
    
        return file_data
        
    def close(self):
        self.client_socket.close()
        
    
        

if __name__ == "__main__":
    client = XFxClient()
    filename = "Wav2vec2.pdf"
    directory_dict = client.get_file_list()   
    print(directory_dict)
    