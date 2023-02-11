# xFx Protocol
The client opens a connection with the server and *informs* the server whether it wants to *download*, *upload*, *get file list* or *check the hash* of a file using a *header*.

For simplicity and convenience, the methods are all **UPPERCASE**.

## Download
If the client wants to download a file, then the header will be as the following:
- **DOWNLOAD[one space][file name][one space][offset][Line Feed]**

**Offset** is **optional**, it is used to represents the number of bytes to skip when resume the download of a file

Upon receiving this header, the server searches for the specified file.
- If the file is not found, then the server shall reply with a header as the following:
  - **NOT_FOUND[Line Feed]**
- If the file is found, then the server shall reply
  - with a header as the following:
    - **OK[one space][file size][Line Feed]**
  - followed by the bytes of the file
		
## Upload
If the client wants to upload a file, then the header will be as the following:
- **UPLOAD[one space][file name][one space][file size][one space][offset][Line Feed]**

**Offset** is **optional**, it is used to represents the number of bytes to skip when resume the upload of a file

After sending the header, the client shall send the bytes of the file

## Get File List
The client can request a list of files by sending the following header to the server:
- **GET_FILE_LIST[Line Feed]**

The server will respond with a list of the available files, one file per line. the following format is used:
- **FILE_LIST[Line Feed][file name 1][one space][file size 1][Line Feed][file name 2][one space][Line Feed]**

## Check File Hash
To check wheter or not a file downloaded on the client side has changed or not in the server side, an md5 algorithm is used to get the hash of each file and compares them. The client sends the following header to the server:
- **CHECK_FILE_HASH[one space][file name][one space][File Hash][Line Feed]**

**File Hash** is a string representing the hash of the client file using md5 algorithm.

Upon receiving this header, the server will check if the hashes match, The response of the server will be the following:
- **MATCH[Line Feed]** When File did not Change
- **NONE_MATCH[Line Feed]** When File Changed

## Errors
If the client requests a file that's not existing
- **NOT_FOUND[Line Feed]**

If a request is malformed or incorrect
- **MALFORMED_REQUEST[Line Feed]**

If a network error happens
- **NETWORK_ERROR[Line Feed]**



# xFx Client Library in Python
In order to make it easier for developers to implement the xFx protocol, a client library in Python is provided. The library provides convenient methods to interact with the server and handle the communication as well as errors.


## XFxClient(host: str, port: int, max_receive: int, share_directory: string)
To initialize the client library you should instantiate the **XFxClient** Class.

The default arguments are:
**host='localhost'| port=9999 | max_receive=1024 | share_directory="./ClientShare"**

    host: specifies the location of your xFx Server
    port: specifies the port on which the xFx Server is running
    max_receive: specifies the maximum number of bytes that the client can receive from the server in a single request
    share_directory: specifies the local directory where the client stores the downloaded files.

Here is the list of functions available in the XFxClient class:

## XFxClient.download(filename: str, offset: int = 0) -> Bool
This function is used to download a file from the server.

    filename: The name of the file to be downloaded
    offset: The number of bytes to skip when resuming a download (optional, default value is 0)

The function returns True if the download is successful and False if an error occurs.

## XFxClient.resume_ownload(filename: str) -> Bool
This function is used to resume the download a file from the server.

    filename: The name of the file to be downloaded

The function returns True if the download is successful and False if an error occurs.

## XFxClient.upload(filename: str, offset: int = 0) -> Bool
This function is used to upload a file to the server.

    filename: The name of the file to be uploaded
    offset: The number of bytes to skip when resuming an upload (optional, default value is 0)

The function returns True if the upload is successful and False if an error occurs.

## XFxClient.resume_upload(filename: str) -> Bool
This function is used to resume theupload a file to the server.

    filename: The name of the file to be uploaded

The function returns True if the upload is successful and False if an error occurs.

## XFxClient.get_file_list() -> Dict
This function is used to retrieve the list of files available on the server.

The function returns a dictionary where each key refers to the filename and the value refers to the size in bytes.

## XFxClient.check_file_hash(filename: str) -> Bool
This function is used to check if a file on the client side has changed on the server side.

    filename: The name of the file to be checked
    file_hash: The hash of the client file (md5)

The function returns True if the file is unchanged and False if it has changed or an error occurs.