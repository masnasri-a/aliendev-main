from fastapi import APIRouter
import importlib.util


from pydantic import BaseModel
app = APIRouter()

@app.get('/test-api/test-get')
def endpoint(name:str,age:int=None):
	params = locals()
	spec = importlib.util.spec_from_file_location("module.name", "source/handler/1681694082/test-get.py")
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	result = module.handler(params)
	return result

class TestPost(BaseModel):
	name:str
	age:int = None

@app.post('/test-api/test-post')
def endpoint(param:TestPost):
	params = param.dict()
	spec = importlib.util.spec_from_file_location("module.name", "source/handler/1681694082/test-post.py")
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	result = module.handler(params)
	return result


