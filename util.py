import os
import hashlib
import tomli
import logging

with open('config.toml', 'rb') as config_file:
	config = tomli.load(config_file)

logging.basicConfig(filename=config['GLOBAL']['LOG_FILE'], encoding='utf-8', level=logging.DEBUG)

def get_last_modified_time(path: str):
	logging.debug(f"getting last modified time of {path}")
	last_modified_time = 0
	if os.path.exists(path):
		last_modified_time = os.path.getmtime(path)
	logging.debug(f"last modified time of {path}: {last_modified_time}")
	return last_modified_time

def get_digest(path: str):
	logging.debug(f"getting digest of {path}")
	digest = b''
	if os.path.isfile(path):
		digest = hashlib.sha256(open(path, 'rb').read()).hexdigest()
	logging.debug(f"digest of {path}: {digest}")
	return digest

def get_subfiles(path: str):
	logging.debug(f"getting subfiles of {path}")
	subfiles = []
	if os.path.exists(path):
		for subpath, dirs, files in os.walk(path):
			for file in files:
				subfiles.append(os.path.join(subpath, file))
	logging.debug(f"subfiles of {path}: {subfiles}")
	return subfiles