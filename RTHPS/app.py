from flask import Flask
import json

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Flask Dockerized'

if __name__ == '__main__':

	with open('/data/options.json') as config_file:
		data = json.load(config_file)
	print(data)
	print(data["mqtt_sensor_topic"])
    app.run(debug=True,host='0.0.0.0')
	