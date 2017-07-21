'''
Created on Sep 9, 2015

@author: QuangN
'''

from flask import Flask, render_template
import config
from flask_cors import CORS, cross_origin


app = Flask(__name__)
app.config.from_object(config.DefaultConfig)

@app.route('/', methods=['GET'])
def index():
    return 'Career API'


import api

