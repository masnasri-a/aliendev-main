import pika
import importlib
import configparser
import generator
import json
import os

def consume(queue:str):
    config = configparser.ConfigParser()
    config.read("config.ini")

    username = config.get("RABBITMQ", "username")
    password = config.get("RABBITMQ", "password")
    host = config.get("RABBITMQ", "host")
    port = config.get("RABBITMQ", "port")
    vhost = config.get("RABBITMQ", "vhost")
    credentials = pika.PlainCredentials(username, password)
    parameters = pika.ConnectionParameters(host=host, port=port, virtual_host=vhost, credentials=credentials, blocked_connection_timeout=0, heartbeat=0)
    
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=queue)
    try:
        print("Start consuming...")
        for method, properties, body in channel.consume(queue,auto_ack=True):
            data = json.loads(body.decode('utf-8'))
            print(data)
            folders = data.get("account_id")
            if not os.path.exists("source/handler/"+folders):  # memeriksa apakah folder sudah ada
                os.makedirs("source/handler/"+folders)
            with open("source/handler/"+data.get("account_id")+"/"+data.get('file_name'), 'w') as file:
                file.write(data.get('data'))
            generator.runner()
            print("Created successfully")
    except KeyboardInterrupt:
        channel.stop_consuming()
        exit()


if __name__ == "__main__":
    consume('helper')