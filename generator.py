from source.config import mongo


def convert_to_camelcase(string):
    words = string.split("-")
    words = [word.capitalize() for word in words]
    return "".join(words)


def param_generation(data: list):
    strings = []
    for detail in data:
        key = detail.get('key')
        data_type = detail.get('data_type')
        if str(data_type).lower() == "any":
            data_type = ""
        elif str(data_type).lower() == "string":
            data_type = ":str"
        else:
            data_type = f":{str(data_type).lower()}"
        required = detail.get('required')
        if required:
            required = ""
        else:
            required = "=None"
        strings.append(f'{key}{data_type}{required}')
    print(','.join(strings))
    return (','.join(strings))


# GENERATOR MAIN
client, db = mongo.connect()
with client:
    details = db['gateway'].find()
    with open("source/main.py", 'w') as file:
        list_data_stack = []
        list_stack = ''
        for detail in details:
            list_data_stack.append(
                str(detail.get('stack_name')).replace("-", "_"))
        list_stack = ','.join(list_data_stack)
        file.write(
            f"from fastapi import FastAPI\nimport uvicorn\nfrom route import {list_stack}\n")
        file.write("\napp = FastAPI()\n\n")
        for stack_name in list_data_stack:
            includes = f"app.include_router({stack_name}.app, prefix='/{stack_name}', tags=['{stack_name}'])"
            file.write(f'{includes}\n')
        file.write('if __name__ == "__main__":\n')
        file.write(
            '\tuvicorn.run("main:app", host="0.0.0.0", port=10000, reload=True)')

# GENERATOR ROUTE
client, db = mongo.connect()
with client:
    details = db['gateway'].find()
    for detail in details:
        endpoints = detail.get('endpoint')
        account_id = detail.get('account_id')
        stack_name: str = detail.get('stack_name')
        file_name = "source/route/"+stack_name.replace("-", "_")+".py"
        with open(file_name, 'w') as gen:
            gen.write("from fastapi import APIRouter\n")
            gen.write("import importlib.util\n\n\n")
            gen.write("from pydantic import BaseModel\n")
            gen.write("app = APIRouter()\n\n")
            for endpoint in endpoints:
                method = endpoint.get('method')
                prefix: str = endpoint.get('prefix')
                param_type = endpoint.get('param_type')
                data = endpoint.get('data')
                if param_type == "body":
                    gen.write(
                        f"class {convert_to_camelcase(prefix.replace('/',''))}(BaseModel):\n")
                    for detail in data:
                        key = detail.get('key')
                        data_type = detail.get('data_type')
                        if str(data_type).lower() == "any":
                            data_type = ""
                        elif str(data_type).lower() == "string":
                            data_type = ":str"
                        else:
                            data_type = f":{str(data_type).lower()}"
                        required = detail.get('required')
                        if required:
                            required = ""
                        else:
                            required = " = None"
                        gen.write(f'\t{key}{data_type}{required}\n')
                    gen.write('\n')
                if method == "GET":
                    gen.write(f"@app.get('/{stack_name}{prefix}')")
                if method == "POST":
                    gen.write(f"@app.post('/{stack_name}{prefix}')")
                if method == "PUT":
                    gen.write(f"@app.put('/{stack_name}{prefix}')")
                if method == "DELETE":
                    gen.write(f"@app.delete('/{stack_name}{prefix}')")
                gen.write("\n")
                
                if data is [] or data is None:
                    gen.write("def test():\n")
                else:
                    if param_type == "param":
                        gen.write(f"def endpoint({param_generation(data)}):\n")
                        gen.write("\tparams = locals()\n")
                    elif param_type == "body":
                        gen.write(
                            f"def endpoint(param:{convert_to_camelcase(prefix.replace('/',''))}):\n")
                        gen.write("\tparams = param.dict()\n")
                gen.write(
                    f'\tspec = importlib.util.spec_from_file_location("module.name", "source/handler/{account_id}/{str(prefix).replace("/","")}.py")\n')
                gen.write("\tmodule = importlib.util.module_from_spec(spec)\n")
                gen.write("\tspec.loader.exec_module(module)\n")
                gen.write("\tresult = module.handler(params)\n")
                gen.write("\treturn result\n")
                gen.write("\n")
            gen.write("\n")
