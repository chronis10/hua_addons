from flask import Flask
import json

app = Flask(__name__)

@app.route('/')
def hello_world():
        return 'Local Flask Dockerized instance'

if __name__ == '__main__':
        with open('/data/options.json') as config_file:
                data = json.load(config_file)
        print(data)
        print(data["mqtt_sensor_topic"])
        print(data["db_username"])
        app.run(debug=True,host='0.0.0.0')
