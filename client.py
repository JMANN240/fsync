import requests
from cryptography.fernet import Fernet
import tomli
import os

with open('config.toml', 'rb') as config_file:
	config = tomli.load(config_file)

fernet = Fernet(config['FERNET_KEY'])

def download_file(filename: str):
	with requests.get(f"{config['SERVER_URL']}/file", params={'server_file_name': filename}, stream=True) as res:
		dec = fernet.decrypt(res.json().get('data'))
		with open(filename, 'wb') as f:
			f.write(dec)

def upload_file(filepath: str):
	filename = os.path.split(filepath)[-1]
	with open(filepath, 'rb') as f:
		enc = fernet.encrypt(f.read())
		requests.put(f"{config['SERVER_URL']}/file", files={'client_file_bytes': enc}, params={'client_file_name': filename})

for filepath in config['FILES']:
	upload_file(filepath)
