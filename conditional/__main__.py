from flask import Flask
from flask import jsonify

import json
import sys

def web_main():
    json_config = None

    with open(sys.argv[1]) as config_file:
        json_config = json.load(config_file)

    app = Flask(__name__)
    app.run(**json_config['flask'])

if __name__ == '__main__':
    web_main()
