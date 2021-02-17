from flask import Flask, request
from flask_pymongo import PyMongo
import math, time, datetime


class CarDriver:
    def __init__(self, car_id, status, temp):
        self.car_id = car_id
        self.status = status
        self.temp = temp
        self.time = datetime.datetime.now()
        self.temp_his = [{"temp": temp, "time": self.time}]
        self.time_his = [{"time": self.time, "status": self.status}]

    def get_json(self):
        return {'car_id': self.car_id,
                'status': self.status,
                'temp': self.temp,
                'time': self.time,
                'temp_his': self.temp_his,
                'time_his': self.time_his}

    def set_temp_his(self, temp_his):
        self.temp_his = temp_his

    def set_time_his(self, time_his):
        self.time_his = time_his


app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://exceed_group04:cz48z5h9@158.108.182.0:2255/exceed_group04'
mongo = PyMongo(app)

myCollection = mongo.db.test

car = {}


def init():
    """Get data form collection in database."""
    query = myCollection.find()
    for d in query:
        if d['car_id'] not in car:
            car[d['car_id']] = CarDriver(d['car_id'], d['status'], d['temp'])
            car[d['car_id']].set_temp_his(d['temp_his'])
            car[d['car_id']].set_time_his(d['time_his'])


init()


# Front-end
@app.route('/driver', methods=['POST'])
def driver_update():
    """POST driver information from front-end to database.

    :arg
        {
        'car_id': int,
        'status': resting/ running,
        'temp': int
        }
    """
    data = request.json
    if data['car_id'] not in car:
        car[data['car_id']] = CarDriver(data['car_id'], data['status'], data['temp'])
        myCollection.insert_one(car[data['car_id']].get_json())
        return {"result": 'Driver Register Complete'}

    my_query = {'car_id', data['car_id']}

    # รอการออกแบบจาก front end
    new_data = {'status': data['status'], 'temp': data['temp'], 'time': datetime.datetime.now(),
                'temp_his': car[data['car_id']].temp_his, 'time_history': car[data['car_id']].time_history}
    new_data['time_history'].append([str(new_data['time']), statusc])
    myCollection.update_one(my_query, new_data)
    return {"result": 'Driver Update Success'}


@app.route('/driver_stop', methods=['POST'])
def driver_stop():
    data = request.json
    new_data = car[data['car_id']]
    new_data['status'] = data['status']
    new_data['time'] = datetime.datetime.now()
    new_data['time_history'].append([str(new_data['time']), data['status']])
    return {"result": 'Driver Status Update Success'}


# Hardware
@app.route('/temp_input', methods=['POST'])
def temp_update():
    """POST update temperature to database.

    :arg
    {
        'car_id': int,
        'temp': int
    }
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
def find_driver_info():
    """GET all driver information in database.

    :return
    {'result:[
        {
        'status': resting/running,
        'temp': int,
        'time': time,
        'temp_his': [{'temp': int, 'time': time}],
        'time_his': [{'time': time, 'status': resting/running}]
        }
    ]
    '}
    """
    query = myCollection.find()
    driver_information = []
    for data in query:
        driver_information.append(
            {
                "status": data['status'],
                "temp": data["temp"],
                "time": data["time"],
                "temp_his": data["temp_his"],
                "time_his": data["time_his"]
            }
        )
    return {'result': driver_information}


@app.route('/temp_input', methods=['GET'])
def find_temp_time():
    """GET temp and total running time of car_id.

    :arg
    {'car_id': int}

    :return
    {
    'temp': int,
    'time': str
    }
    """
    data = request.json
    query = myCollection.find({'car_id': data['car_id']})
    present_time = datetime.datetime.now()
    for d in query:
        if d['status'] == 'resting':
            return {'result': {
                'temp': d['temp'],
                'time': 0
            }}
        if d['status'] == 'running':
            return {'result': {
                'temp': d['temp'],
                'time': str(present_time.replace(microsecond=0) - d['time_his'][-1]['time'].replace(microsecond=0))
            }
            }


@app.route('/reset', methods=['POST'])
def reset():
    """DELETE all data in database"""
    myCollection.delete_many({})
    return {'result': 'Delete Successfully'}


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='20004', debug=True)
