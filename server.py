from fastapi import FastAPI, File
from fastapi.responses import FileResponse
from pathlib import Path
from cryptography.fernet import Fernet
import tomli

app = FastAPI()

with open('config.toml', 'rb') as config_file:
	config = tomli.load(config_file)

fernet = Fernet(config['FERNET_KEY'])

@app.get("/file")
def get_file(server_file_name: str):
	path = Path(remote_file_path)
	if path.is_file():
		with open(path, 'rb') as remote_file:
			return {
				"status": "success",
				"data": fernet.encrypt(remote_file.read())
			}
	else:
		return {
			"status": "failure",
			"reason": f"'{remote_file_path}' is not a file on the server."
		}

@app.put("/file")
def put_file(client_file_name: str, client_file_bytes: bytes = File()):
	with open(client_file_name, 'wb') as server_file:
		server_file.write(fernet.decrypt(client_file_bytes))
	return {"status": "success"}
