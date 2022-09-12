from cryptography.fernet import Fernet
import tomli_w

config = dict()
config['FERNET_KEY']=Fernet.generate_key().decode()
config['FILES']=list()
config['SERVER_URL']=''

with open('config.toml', 'wb') as config_file:
	tomli_w.dump(config, config_file)
