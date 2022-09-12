import requests
from cryptography.fernet import Fernet
import tomli

filename = 'test.txt'

with open('config.toml', 'rb') as config_file:
	config = tomli.load(config_file)

fernet = Fernet(config['FERNET_KEY'])

with requests.get("http://localhost:8000/file", params={'remote_file_path': filename}, stream=True) as res:
	dec = fernet.decrypt(res.json().get('data'))
	with open(filename, 'wb') as f:
		f.write(dec)
