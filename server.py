from genericpath import isdir, isfile
from fastapi import FastAPI, File, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from pathlib import Path
from cryptography.fernet import Fernet
import tomli
import os
import json
import util
import logging

app = FastAPI()

templates = Jinja2Templates(directory="templates")

with open('config.toml', 'rb') as config_file:
	config = tomli.load(config_file)

fernet = Fernet(config['GLOBAL']['FERNET_KEY'])

logging.basicConfig(filename=config['GLOBAL']['LOG_FILE'], level=logging.DEBUG)

@app.get("/")
def index():
	return {
			"status": "success",
			"reason": "Hello, fsync!"
		}

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

@app.get("/files/{virtual_path:path}")
def get_files(request: Request, virtual_path: str):
	path = os.path.join(config['SERVER']['FILES_ROOT'], virtual_path)
	if os.path.isdir(path):
		contents = os.listdir(path)
		files = [content for content in contents if os.path.isfile(os.path.join(path, content))]
		dirs = [content for content in contents if os.path.isdir(os.path.join(path, content))]
		links = []
		if virtual_path != "":
			links.append({
				"ref": os.path.join("/files", *virtual_path.split(os.sep)[:-1]),
				"name": ".."
			})
		for dir in dirs:
			links.append({
				"ref": os.path.join("/files", virtual_path, dir),
				"name": f"/{dir}/"
			})
		for file in files:
			if file != "index.html":
				links.append({
					"ref": os.path.join("/files", virtual_path, file),
					"name": f"/{file}"
				})
		return templates.TemplateResponse("files.html", {"request": request, "links": links})
	else:
		return FileResponse(path)