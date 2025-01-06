# IMPORTING THE NECCESSARY PACKAGES

from jsonManager import parse
from Organizer import Automate
from flask import Flask, request
from decouple import config
from datetime import datetime
import json

# FLASK APP

flaskApp = Flask(__name__)

@flaskApp.route(config("WEBHOOK_ROUTE"), methods=['POST'])
def json_receiver():
    
    if request.remote_addr == config("ALLOWED_ADDRESS") :
        
        print(f"""Received JSON Payload From {config("JIRA_INSTANCE_URL")} AT {request.remote_addr}""")
        
        with open("data.json", "w") as data_file:
            json.dump(request.get_json(), fp=data_file)
        with open("logs.txt","a") as logfile :

            logfile.write(f"""[ JSON Manager Module ]\nReceived JSON Payload From {config("JIRA_INSTANCE_URL")} AT {request.remote_addr}\nTime : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n""")

            logfile.write("\n")

        Automate(parse(request.get_json()))
        
    return ""    

# Running The Flask App

if __name__ == "__main__":

    flaskApp.run(host=config("WEBHOOK_INTERFACE"), port=config("WEBHOOK_PORT"), debug=False)
