from db.migrate import free_the_zoo
import sys
import json

if __name__ == '__main__':
    json_config = None

    with open(sys.argv[1]) as config_file:
        json_config = json.load(config_file)

    free_the_zoo(json_config['zoo']['url'], json_config['db']['url'])
