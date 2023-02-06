'''
uploader.py
-----------
Rewrite of Brian Meade's (bmeade90@vt.edu) CUCM-Bulk-TFTP-Upload.py 

Major changes:
- Python3 support
- Removed hardcoded user details
- Replaced os with pathlib

# This program will traverse a local directory recursively and upload 
# all files while maintaining the directory structure.
#
# Install Python 2.7 and choose the option to add to path (off by default)
# Then install two modules
#  C:\>pip install requests
#  C:\>pip install BeautifulSoup4
#
# May need to use "python -m pip install requests"
#
# Then run the program CUCM-Bulk-TFTP-Upload.py
#  C:\>python tftp.py hostname/IP username password localdirectory
#
# Windows formatting for local directory- C:\\TFTP-Root\\tftpfiles
#
# You can pass in the parameters on the command line or edit the
# sys.argv line at the bottom of the script.
'''

import requests
import sys
import warnings
from bs4 import BeautifulSoup
from getpass import getpass
from pathlib import Path

username = input('OS Platform username: ')
password = getpass('OS Platform password: ')
hostname = input('Hostname to add: ')

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
    sys.exit()


def main(argv):
   warnings.filterwarnings("ignore")
   hostname= ''
   username= ''
   password= ''
   local_file_path= ''
   token= ''
   
   try:
      hostname = sys.argv[1]
      username = sys.argv[2]
      password = sys.argv[3]
      local_file_path = sys.argv[4]
   except:
      print('Please enter hostname/IP Address, username, password, the local file path, and the remote file path')
      sys.exit()
	
   #Create a new session to maintain cookies across requests      
   s = requests.Session()
   
   #Initial Get Request to get a cookie
   getcookie= s.get('https://' + hostname + '/cmplatform', verify=False)
   
   #Post authentication details to authenticate cookie
   payload= {'appNav': 'cmplatform', 'j_username': username, 'j_password': password}
   post= s.post('https://' + hostname + '/cmplatform/j_security_check', data=payload, verify=False)

   #Get request to obtain first Struts Token, use Beautiful Soup to extract token from returned CSS
   tokenrequest= s.get('https://' + hostname + '/cmplatform/tftpFileUpload.do', verify=False)
   soup = BeautifulSoup(tokenrequest.text)
   try:
      token = soup.find('input', {'name': 'token'}).get('value')
   except:
      print('Couldn''t get token.  You may be trying too often.')
      sys.exit()
   
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
            sys.exit()
         print('Uploaded file ' + file + ' to ' + remote_path)
         f.close();

   print('Bulk upload completed successfully!')
