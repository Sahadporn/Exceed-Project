import datetime
import math
import time

from flask import Flask, request
from flask_pymongo import PyMongo
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)
cors = CORS(app, resources={
    r"/": {
        "origins": "*",
        "allow_headers": '*'
    }
})

app.config['MONGO_URI'] = 'mongodb://exceed_group04:cz48z5h9@158.108.182.0:2255/exceed_group04'
mongo = PyMongo(app)

myCollection = mongo.db.test


class CarDriver:
    def __init__(self, name, car_id, source, dest, status, min_temp, max_temp):
        self.driver_name = name
        self.car_id = car_id
        self.time_start = datetime.datetime.now()
        self.source = source
        self.dest = dest
        self.status = status
        self.temp = 0
        self.time = datetime.datetime.now()
        self.temp_his = [{"temp": 0, "time": self.time}]
        self.time_his = [{"time": self.time, "status": self.status}]
        self.min_temp = min_temp
        self.max_temp = max_temp

    def get_json(self):
        return {'driver_name': self.driver_name,
                'car_id': self.car_id,
                'time_start': self.time_start,
                'source': self.source,
                'destination': self.dest,
                'status': self.status,
                'temp': self.temp,
                'time': self.time,
                'temp_his': self.temp_his,
                'time_his': self.time_his,
                'min_temp': self.min_temp,
                'max_temp': self.max_temp}

    def set_temp_his(self, temp_his):
        self.temp_his = temp_his

    def set_time_his(self, time_his):
        self.time_his = time_his


car = {}


def init():
    """Get data from collection in database."""
    query = myCollection.find()
    for d in query:
        if d['car_id'] not in car:
            car[d['car_id']] = CarDriver(d['driver_name'],
                                         d['car_id'],
                                         d['source'],
                                         d['destination'],
                                         d['status'],
                                         d['min_temp'],
                                         d['max_temp'])
            car[d['car_id']].set_temp_his(d['temp_his'])
            car[d['car_id']].set_time_his(d['time_his'])


init()


# Front-end
@app.route('/driver_regis', methods=['POST'])
@cross_origin()
def driver_regis():
    """POST driver information from front-end to database.

    :arg
        {
        'driver_name': str,
        'car_id': str,
        'source': str,
        'destination': str,
        'status': 3,
        'min_temp': str,
        'max_temp': str
        }
    """
    data = request.json
    if data['car_id'] not in car:
        car[data['car_id']] = CarDriver(data['driver_name'], data['car_id'], data['source'], data['destination'],
                                        int(data['status']), float(data['min_temp']), float(data['max_temp']))
        myCollection.insert_one(car[data['car_id']].get_json())
        return {"result": 'Driver Register Complete'}
    return {"result": 'Cargo already exist'}


@app.route('/driver_update', methods=['POST'])
@cross_origin()
def driver_update():
    """Update driver status

    :arg
    {
        "car_id": str,
        "status: 1/2
    }
    """
    data = request.json
    my_query = {'car_id': data['car_id']}
    query = myCollection.find(my_query)
    new_status = data['status']
    for d in query:
        if d['status'] == 1 or d['status'] == 0 and data['status'] == 1:
            new_status = abs(d['status'] - 1)
        elif data['status'] == 2:
            new_status = data['status']
        elif d['status'] == 3 and data['status'] == 1:
            new_status = 1
        if d['status'] == 2:
            return {"result": "Cargo delivered"}
        time_his = d['time_his']
        time_his.append({'time': datetime.datetime.now(), 'status': new_status})
        set_time_his = {'$set': {'time_his': time_his}}
        myCollection.update_one(my_query, set_time_his)
    set_status = {'$set': {'status': new_status}}
    myCollection.update_one(my_query, set_status)
    return {"result": 'Status Update Successful'}


@app.route('/temp_his', methods=['GET'])
@cross_origin()
def get_temp_his():
    """GET temperature history.

    :return
    {
        "temp_his": [{"temp": float},{"time":time}]
    }
    """
    data = request.args.get('car_id')
    query = myCollection.find({'car_id': data})
    for d in query:
        return {'temp_his': d['temp_his']}


# Hardware
@app.route('/temp_input', methods=['POST'])
@cross_origin()
def temp_update():
    """POST update temperature to database.

    :args
        "car_id": str,
        "temp": float
    """
    data = request.json
    my_query = {'car_id': data['car_id']}
    query = myCollection.find(my_query)
    new_temp = {"$set": {"temp": data['temp']}}
    myCollection.update_one(my_query, new_temp)
    new_time = {"$set": {"time": datetime.datetime.now()}}
    myCollection.update_one(my_query, new_time)
    for d in query:
        temp_his = d["temp_his"]
        temp_his.append({"temp": data['temp'], "time": datetime.datetime.now()})
        new_temp_his = {"$set": {"temp_his": temp_his}}
        myCollection.update_one(my_query, new_temp_his)
    return {"result": 'Temperature Update'}


@app.route('/driver', methods=['GET'])
@cross_origin()
def find_driver_info():
    """GET all driver information in database.

    :return
        {"result": ["driver_name": str,
                    'car_id': str,
                    'time_start': time,
                    'source': str,
                    'destination': str,
                    "status": 0/1/2,
                    "temp": float,
                    "time": time,
                    "temp_his": [{"temp": float}, {"time":time}],
                    "time_his": [{"time": time}, {"status":0/1/2}],
                    "min_temp": float,
                    "max_temp": float
                    ]}
    """
    query = myCollection.find()
    driver_information = []
    for data in query:
        if data['status'] == 3:
            alert = 0
        elif data['temp'] <= data['min_temp'] or data['temp'] >= data['max_temp']:
            alert = 1
        else:
            alert = 0
        driver_information.append(
            {
                "driver_name": data['driver_name'],
                'car_id': data['car_id'],
                'time_start': data['time_start'],
                'source': data['source'],
                'destination': data['destination'],
                "status": data['status'],
                "temp": data["temp"],
                "time": data["time"],
                "temp_his": data["temp_his"],
                "time_his": data["time_his"],
                "min_temp": data["min_temp"],
                "max_temp": data["max_temp"],
                "alert": alert
            }
        )
    return {'result': driver_information}


@app.route('/time', methods=['GET'])
@cross_origin()
def get_running_time():
    """GET total running time after status 1.

    :return
        {"time": 0} if current status = 0
        {"time": now - most recent status 1 time} if current status = 1
        {"time": total delivery time} if current status = 2
    """
    data = request.args.get('car_id')
    query = myCollection.find({'car_id': data})
    present_time = datetime.datetime.now()
    for d in query:
        if d['status'] == 0:
            return {'time': 0}
        if d['status'] == 1:
            return {'time': (present_time - d['time_his'][-1]['time']).total_seconds()}
        if d['status'] == 2:
            return {'time': (d['time_his'][-1]['time'] - d['time_his'][0]['time']).total_seconds()}
    return {'result': 'Error'}


@app.route('/status', methods=['GET'])
@cross_origin()
def get_status():
    """GET current status.

    :return
        {"status": 0/1/2}
    """
    data = request.args.get('car_id')
    query = myCollection.find({'car_id': data})
    for d in query:
        return {'status': d['status']}
    return {'result': 'Error'}


@app.route('/alert', methods=['GET'])
@cross_origin()
def check_temp():
    """Check if temperature is in threshold.

    :return
        {alert: 0/1}
    """
    data = request.args.get('car_id')
    query = myCollection.find({'car_id': data})
    for d in query:
        if d['status'] == 3:
            return {'alert': 0}
        elif d['temp'] <= d['min_temp'] or d['temp'] >= d['max_temp']:
            return {'alert': 1}
        else:
            return {'alert': 0}
    return {'result': 'Error'}


@app.route('/reset', methods=['POST'])
@cross_origin()
def reset():
    """DELETE all data in database."""
    myCollection.delete_many({})
    car.clear()
    return {'result': 'Delete Successfully'}


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='20004', debug=True)
