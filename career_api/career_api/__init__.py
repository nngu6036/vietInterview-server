'''
Created on Sep 9, 2015

@author: QuangN
'''

from flask import Flask, render_template
from flask_cors import CORS, cross_origin
import config

app = Flask(__name__)
CORS(app)
app.config.from_object(config.DefaultConfig)

@app.route('/', methods=['GET'])
def index():
    return 'Career API'


import api

