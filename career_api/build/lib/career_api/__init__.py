'''
Created on Sep 9, 2015

@author: QuangN
'''

from flask import Flask

import config

app = Flask(__name__)
app.config.from_object(config.DefaultConfig)

@app.route('/', methods=['GET'])
def index():
    return 'Career API'


import admin
import employer
