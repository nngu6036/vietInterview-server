'''
Created on Sep 9, 2015

@author: QuangN
'''

from flask import Flask, render_template
from flask_cors  import CORS
import config

app = Flask(__name__)
app.config.from_object(config.DefaultConfig)
CORS(app)

@app.route('/', methods=['GET'])
def index():
    return 'Career API'


import api

