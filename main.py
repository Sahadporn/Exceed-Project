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
    def __init__(self, name, car_id, source, dest, status):
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
                'time_his': self.time_his}

    def set_temp_his(self, temp_his):
        self.temp_his = temp_his

    def set_time_his(self, time_his):
        self.time_his = time_his


car = {}


def init():
    """Get data form collection in database."""
    query = myCollection.find()
    for d in query:
        if d['car_id'] not in car:
            car[d['car_id']] = CarDriver(d['driver_name'], d['car_id'], d['source'], d['destination'], d['status'])
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
        'status': 0/1/2
        }
    """
    data = request.json
    if data['car_id'] not in car:
        car[data['car_id']] = CarDriver(data['driver_name'], data['car_id'], data['source'], data['destination'],
                                        data['status'])
        myCollection.insert_one(car[data['car_id']].get_json())
        return {"result": 'Driver Register Complete'}
    return {"result": 'Cargo already exist'}


@app.route('/driver_update', methods=['POST'])
@cross_origin()
def driver_update():
    print(request)
    print(request.json)
    data = request.json
    my_query = {'car_id': data['car_id']}
    query = myCollection.find(my_query)
    new_status = data['status']
    for d in query:
        if d['status'] == 1 or d['status'] == 0 and data['status'] == 1:
            new_status = abs(d['status'] - 1)
        elif data['status'] == 2:
            new_status = data['status']
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
    data = request.args.get('car_id')
    query = myCollection.find({'car_id': data})
    for d in query:
        return {'temp_his': d['temp_his']}


# Hardware
@app.route('/temp_input', methods=['POST'])
@cross_origin()
def temp_update():
    """POST update temperature to database."""
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
    """GET all driver information in database."""
    query = myCollection.find()
    driver_information = []
    for data in query:
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
                "time_his": data["time_his"]
            }
        )
    return {'result': driver_information}


@app.route('/temp_input', methods=['GET'])
@cross_origin()
def find_temp_time():
    """GET temp and total running time of car_id."""
    data = request.args.get('car_id')
    query = myCollection.find({'car_id': int(data)})
    present_time = datetime.datetime.now()
    for d in query:
        if d['status'] == 0:
            return {'result': {
                'temp': d['temp'],
                'time': 0
            }}
        if d['status'] == 1:
            return {'result': {
                'temp': d['temp'],
                'time': (present_time - d['time_his'][-1]['time']).total_seconds()
            }
            }
    return {'result': 'Error'}


@app.route('/time', methods=['GET'])
@cross_origin()
def get_running_time():
    data = request.args.get('car_id')
    query = myCollection.find({'car_id': int(data)})
    present_time = datetime.datetime.now()
    for d in query:
        if d['status'] == 0:
            return {'time': 0}
        if d['status'] == 1:
            return {'time': (present_time - d['time_his'][-1]['time']).total_seconds()}
    return {'result': 'Error'}


@app.route('/status', methods=['GET'])
@cross_origin()
def get_status():
    data = request.args.get('car_id')
    query = myCollection.find({'car_id': int(data)})
    for d in query:
        return {'status': d['status']}
    return {'result': 'Error'}


# @app.route('/reset', methods=['POST'])
# @cross_origin()
# def reset():
#     """DELETE all data in database"""
#     myCollection.delete_many({})
#     return {'result': 'Delete Successfully'}


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='20004', debug=True)
