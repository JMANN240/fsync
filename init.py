from cryptography.fernet import Fernet
import tomli_w

config = dict()

global_config = dict()
global_config['FERNET_KEY']=Fernet.generate_key().decode()
config['GLOBAL'] = global_config

client_config = dict()
client_config['MAPPINGS'] = dict()
client_config['SERVER_URL'] = ''
config['CLIENT'] = client_config

server_config = dict()
server_config['FILES_DIRECTORY'] = 'files'
config['SERVER'] = server_config

with open('config.toml', 'wb') as config_file:
	tomli_w.dump(config, config_file)
