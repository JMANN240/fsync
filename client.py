import requests
from cryptography.fernet import Fernet
import tomli
from time import sleep
import json
import util
import logging

with open('config.toml', 'rb') as config_file:
	config = tomli.load(config_file)

fernet = Fernet(config['GLOBAL']['FERNET_KEY'])

logging.basicConfig(filename=config['GLOBAL']['LOG_FILE'], encoding='utf-8', level=logging.DEBUG)
logging.info("test")

def download_file(client_file_path: str, server_file_path: str):
	logging.info(f"trying to download {server_file_path} to {client_file_path}")
	with requests.get(f"{config['CLIENT']['SERVER_URL']}/file", params={'server_file_path': server_file_path}, stream=True) as res:
		dec = fernet.decrypt(res.json().get('data'))
		with open(client_file_path, 'wb') as f:
			f.write(dec)

def upload_file(client_file_path: str, server_file_path: str):
	logging.info(f"trying to upload {client_file_path} to {server_file_path}")
	with open(client_file_path, 'rb') as f:
		enc = fernet.encrypt(f.read())
		requests.put(f"{config['CLIENT']['SERVER_URL']}/file", files={'client_file_bytes': enc}, params={'server_file_path': server_file_path})

def get_server_modified_time(server_file_path):
	res = requests.get(f"{config['CLIENT']['SERVER_URL']}/file/time", params={'server_file_path': server_file_path})
	res_json = res.json()
	return res_json['data']

def get_server_digest(server_file_path):
	res = requests.get(f"{config['CLIENT']['SERVER_URL']}/file/digest", params={'server_file_path': server_file_path})
	res_json = res.json()
	return res_json['data']

def get_server_subfiles(server_directory_path):
	res = requests.get(f"{config['CLIENT']['SERVER_URL']}/directory", params={'server_directory_path': server_directory_path})
	dec = json.loads(fernet.decrypt(res.json().get('data')).decode())
	return dec

def update_files(mappings):
	for client_file_path, server_file_path in mappings:
		server_digest = get_server_digest(server_file_path)
		client_digest = util.get_digest(client_file_path)

		logging.debug(f"client:{client_file_path}.digest {'=' if server_digest == client_digest else '!'}= server:{server_file_path}.digest")
		if server_digest != client_digest:
			server_modified_seconds = get_server_modified_time(server_file_path)
			client_modified_seconds = util.get_last_modified_time(client_file_path)

			logging.debug(f"client:{client_file_path} is {'newer' if client_modified_seconds > server_modified_seconds else 'older'} than server:{server_file_path}.digest")
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
		for filepath in util.get_subfiles(client_dir):
			client_path = filepath
			server_path = filepath.replace(client_dir, server_dir, 1)
			update_files([(client_path, server_path)])
		for filepath in get_server_subfiles(server_dir):
			server_path = filepath
			client_path = filepath.replace(server_dir, client_dir, 1)
			update_files([(client_path, server_path)])

while True:
	sync()
	sleep(config['CLIENT']['SYNC_SECONDS'])