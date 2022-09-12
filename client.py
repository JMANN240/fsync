import requests

filename = 'duality.jpg'

with requests.get("http://localhost:8000/file", params={'remote_file_path': filename}, stream=True) as res:
	with open(filename, 'wb') as f:
		f.write(res.content)
