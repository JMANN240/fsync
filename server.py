from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse
from pathlib import Path
from cryptography.fernet import Fernet
import tomli

app = FastAPI()

with open('config.toml', 'rb') as config_file:
	config = tomli.load(config_file)

fernet = Fernet(config['FERNET_KEY'])

@app.get("/file")
def get_file(remote_file_path: str):
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
async def put_file(remote_file: UploadFile):
	with open(remote_file.filename, 'wb') as local_file:
		local_file.write(await remote_file.read())
	return {"status": "success"}
