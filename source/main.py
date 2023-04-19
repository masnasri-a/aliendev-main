from fastapi import FastAPI
import uvicorn
from route import test_api

app = FastAPI()

app.include_router(test_api.app, prefix='/test_api', tags=['test_api'])
if __name__ == "__main__":
	uvicorn.run("main:app", host="0.0.0.0", port=9100, reload=True)