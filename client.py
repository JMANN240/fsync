import requests
from cryptography.fernet import Fernet
import tomli
import os
import hashlib
from time import sleep
import json

with open('config.toml', 'rb') as config_file:
	config = tomli.load(config_file)

fernet = Fernet(config['GLOBAL']['FERNET_KEY'])

def download_file(client_file_path: str, server_file_path: str):
	with requests.get(f"{config['CLIENT']['SERVER_URL']}/file", params={'server_file_path': server_file_path}, stream=True) as res:
		dec = fernet.decrypt(res.json().get('data'))
		with open(client_file_path, 'wb') as f:
			f.write(dec)

def upload_file(client_file_path: str, server_file_path: str):
	with open(client_file_path, 'rb') as f:
		enc = fernet.encrypt(f.read())
		requests.put(f"{config['CLIENT']['SERVER_URL']}/file", files={'client_file_bytes': enc}, params={'server_file_path': server_file_path})

def get_file_modified_time(server_file_path):
	res = requests.get(f"{config['CLIENT']['SERVER_URL']}/file/time", params={'server_file_path': server_file_path})
	res_json = res.json()
	return res_json['data']

def get_file_digest(server_file_path):
	res = requests.get(f"{config['CLIENT']['SERVER_URL']}/file/digest", params={'server_file_path': server_file_path})
	res_json = res.json()
	return res_json['data']

def get_directory_files(server_directory_path):
	res = requests.get(f"{config['CLIENT']['SERVER_URL']}/directory", params={'server_directory_path': server_directory_path})
	dec = json.loads(fernet.decrypt(res.json().get('data')).decode())
	return dec

def update_files(mappings):
	for client_file_path, server_file_path in mappings:
		server_digest = get_file_digest(server_file_path)
		if os.path.exists(client_file_path):
			client_digest = hashlib.sha256(open(client_file_path, 'rb').read()).hexdigest()
		else:
			client_digest = b''

		if server_digest != client_digest:
			server_modified_seconds = get_file_modified_time(server_file_path)
			if os.path.exists(client_file_path):
				client_modified_seconds = os.path.getmtime(client_file_path)
			else:
				client_modified_seconds = 0

			if client_modified_seconds > server_modified_seconds:
				upload_file(client_file_path, server_file_path)
			else:
				download_file(client_file_path, server_file_path)

def sync():
	global config

	with open('config.toml', 'rb') as config_file:
		config = tomli.load(config_file)
	
	update_files(config['CLIENT']['MAPPINGS']['FILES'].items())
	for client_dir, server_dir in config['CLIENT']['MAPPINGS']['DIRECTORIES'].items():
		for path, dirs, files in os.walk(client_dir):
			for file in files:
				client_path = os.path.join(path, file)
				server_path = os.path.join(server_dir, path.replace(client_dir, "", 1), file)
				update_files([(client_path, server_path)])
		for file_path in get_directory_files(server_dir):
			client_path = os.path.join(client_dir, file_path)
			server_path = os.path.join(server_dir, file_path)
			update_files([(client_path, server_path)])

while True:
	sync()
	sleep(5)