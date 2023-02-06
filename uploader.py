'''
uploader.py
-----------
Rewrite of Brian Meade's (bmeade90@vt.edu) CUCM-Bulk-TFTP-Upload.py 

Major changes:
- Python3 support
- Removed hardcoded user details
- Replaced os with pathlib
'''

import requests
from bs4 import BeautifulSoup
from getpass import getpass
from pathlib import Path

username = input('OS Platform username: ')
password = getpass('OS Platform password: ')
hostname = input('Hostname to upload to: ')
filepath = input('Path to files: ')

s = requests.Session()
getcookie= s.get('https://' + hostname + '/cmplatform', verify=False)
payload= {'appNav': 'cmplatform', 'j_username': username, 'j_password': password}
post= s.post('https://' + hostname + '/cmplatform/j_security_check', data=payload, verify=False)
tokenrequest= s.get('https://' + hostname + '/cmplatform/tftpFileUpload.do', verify=False)
soup = BeautifulSoup(tokenrequest.text)
try:
    token = soup.find('input', {'name': 'token'}).get('value')
except:
    print('Couldn''t get token.  You may be trying too often.')

#For Loops to walk through all files in directory/sub-directories
for root, dirs, files in os.walk(local_file_path):
    path = root.split(os.sep)
    print((len(path) - 1) * '---', os.path.basename(root))

    for file in files:
        print(len(path) * '---', file)
        fullpath = os.path.join(root, file)
        remote_path = os.path.relpath(root, local_file_path)

        #Needed for Windows file paths
        remote_path = remote_path.replace("\\","/")

        #Upload individual file
        f= open(fullpath, 'rb')
        #Post response will provide the next Struts token
        postfile = s.post('https://' + hostname + '/cmplatform/tftpFileUpload.do', files={'struts.token.name': (None, 'token'),'token': (None, token), 'file': (file,f,'application/octet-stream'), 'directory': (None, remote_path)}, verify = False)
        soup = BeautifulSoup(postfile.text)
        try:
            token = soup.find('input', {'name': 'token'}).get('value')
        except:
            print('Couldn''t get token.  You may be trying too often.')
        
        print('Uploaded file ' + file + ' to ' + remote_path)
        f.close();

print('Bulk upload completed successfully!')
