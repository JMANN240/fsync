from cryptography.fernet import Fernet
import tomli_w

config = dict()
config['FERNET_KEY']=Fernet.generate_key().decode()

with open('config.toml', 'wb') as config_file:
	tomli_w.dump(config, config_file)
