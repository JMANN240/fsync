from fastapi import FastAPI, File
from pathlib import Path
from cryptography.fernet import Fernet
import tomli
import os
import json
import util
import logging

app = FastAPI()

with open('config.toml', 'rb') as config_file:
	config = tomli.load(config_file)

fernet = Fernet(config['GLOBAL']['FERNET_KEY'])

logging.basicConfig(filename=config['GLOBAL']['LOG_FILE'], encoding='utf-8', level=logging.DEBUG)

@app.get("/file")
def get_file(server_file_path: str):
	if ".." in server_file_path:
		return {
			"status": "failure",
			"reason": f"Going up directories is not permitted."
		}
	total_path = f"{config['SERVER']['FILES_ROOT']}{server_file_path}"
	path = Path(total_path)
	if not path.is_file():
		return {
			"status": "failure",
			"reason": f"'{server_file_path}' is not a file on the server."
		}
	with open(path, 'rb') as remote_file:
		return {
			"status": "success",
			"data": fernet.encrypt(remote_file.read())
		}

@app.put("/file")
def put_file(server_file_path: str, client_file_bytes: bytes = File()):
	if ".." in server_file_path:
		return {
			"status": "failure",
			"reason": f"Going up directories is not permitted."
		}
	total_path = f"{config['SERVER']['FILES_ROOT']}{server_file_path}"
	total_directory = os.path.dirname(total_path)
	if not os.path.exists(total_directory):
		os.makedirs(total_directory)
	with open(total_path, 'wb') as server_file:
		server_file.write(fernet.decrypt(client_file_bytes))
	return {"status": "success"}

@app.get("/file/time")
def get_file_time(server_file_path: str):
	total_path = f"{config['SERVER']['FILES_ROOT']}{server_file_path}"
	return {
		"data": fernet.encrypt(str(util.get_last_modified_time(total_path)).encode('utf-8'))
	}

@app.get("/file/digest")
def get_file_digest(server_file_path: str):
	total_path = f"{config['SERVER']['FILES_ROOT']}{server_file_path}"
	return {
		"data": fernet.encrypt(util.get_digest(total_path).encode('utf-8'))
	}

@app.get("/directory")
def get_directory_files(server_directory_path: str):
	total_path = f"{config['SERVER']['FILES_ROOT']}{server_directory_path}"
	return {
		"data": fernet.encrypt(json.dumps([filepath.replace(config['SERVER']['FILES_ROOT'], "", 1) for filepath in util.get_subfiles(total_path)]).encode('utf-8'))
	}