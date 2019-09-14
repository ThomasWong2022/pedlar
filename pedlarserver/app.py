from flask import Flask, render_template, request, redirect, url_for # For flask implementation
from pymongo import MongoClient
import os

app = Flask(__name__)

client = MongoClient("mongodb://127.0.0.1:27017") #host uri
db = client['Pedlar'] #Select the database


@app.route("/trade", methods=['POST'])
def add_trade_record():
    req_data = request.get_json()
    user = req_data.get('user', 'Sample')
    return ('', 204)

@app.route("/user",methods=['POST'])
def add_user_record():
    req_data = request.get_json()
    user = req_data.get('user', 'Sample')
    return ('', 204)


if __name__ == "__main__":
    app.run()