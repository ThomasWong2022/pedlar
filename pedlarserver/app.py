from flask import Flask, render_template, request, redirect, url_for, jsonify  # For flask implementation
from pymongo import MongoClient
import os

app = Flask(__name__)

client = MongoClient("localhost") #host uri
db = client['Pedlar'] #Select the database


@app.route("/trade", methods=['POST'])
def add_trade_record():
    req_data = request.get_json()
    user = req_data.get('user', 'Sample')
    usertrades = db[user]
    usertrades.insert_one(req_data)
    return ('', 204)

@app.route("/user", methods=['POST'])
def user_record():
    req_data = request.get_json()
    user = req_data.get('user', 'Sample')
    # check if exist in Mongo 
    usertable = db['Users']
    targetuser = usertable.find_one({'user':user})
    if targetuser is None:
        exist = False
        usertable.insert_one({'user':user, 'pnl':0})
    else:
        exist = True
    return jsonify(username=user, exist=exist)


if __name__ == "__main__":
    app.run()