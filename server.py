from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse

app = FastAPI()

@app.get("/file", response_class=FileResponse)
def get_file(remote_file_path: str):
	return FileResponse(remote_file_path)

@app.post("/file")
async def post_file(remote_file: UploadFile):
	with open(remote_file.filename, 'wb') as local_file:
		local_file.write(await remote_file.read())
	return {"status": "success"}
