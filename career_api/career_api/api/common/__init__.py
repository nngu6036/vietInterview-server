import datetime
import json
import os

from career_api.proxy import common_service
from flask import request, jsonify
from werkzeug.utils import secure_filename

from career_api import app

ALLOWED_EXTENSIONS = ['mkv', 'flv', 'vob', 'avi', 'mov', 'wmv', 'mp4', 'mpg', 'mpeg', 'webm']


def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/common/video/upload', methods=['GET', 'POST'])
def upload_file():
  try:
    print request.files
    if request.method == 'POST':
      # check if the post request has the file part
      if 'file' not in request.files:
        return jsonify(result=False)
      file = request.files['file']
      # if user does not select file, browser also
      # submit a empty part without filename
      if file.filename == '':
        return jsonify(result=False)
      if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        server_fname = '%s%s' % (datetime.datetime.now().strftime('%S%M%H%m%d%Y'), filename)
        file.save(os.path.join(app.config['VIDEO_UPLOAD_FOLDER'], server_fname))
        print '%s%s' % (app.config['VIDEO_DOWNLOAD_FOLDER'], server_fname)
        return jsonify(result=True, url='%s%s' % (app.config['VIDEO_DOWNLOAD_FOLDER'], server_fname))
  except Exception as exc:
    print(exc)
    print 'Upload file error '
    return jsonify(result=False)


@app.route('/common/assignment/category', methods=['GET'], endpoint='common-assignment-category')
def jobCategory():
  try:
    if request.method == 'GET':
      categoryList = common_service.getJobCategory()
      return jsonify(categoryList=categoryList)
  except Exception as exc:
    print(exc)
    print 'Get category error '
    print request.values
    return jsonify(result=False)


@app.route('/common/assignment/position', methods=['GET'], endpoint='common-assignment-position')
def jobPosition():
  try:
    if request.method == 'GET':
      positionList = common_service.getJobPosition()
      return jsonify(positionList=positionList)
  except Exception as exc:
    print(exc)
    print 'Get position error '
    print request.values
    return jsonify(result=False)


@app.route('/common/assignment/location', methods=['GET'], endpoint='common-assignment-location')
def jobPosition():
  try:
    if request.method == 'GET':
      countryList = common_service.getCountry()
      provinceList = common_service.getProvince()
      return jsonify(countryList=countryList, provinceList=provinceList)
  except Exception as exc:
    print(exc)
    print 'Get position error '
    print request.values
    return jsonify(result=False)


@app.route('/common/assignment/edulevel', methods=['GET'], endpoint='common-assignment-edulevel')
def eduLevel():
  try:
    if request.method == 'GET':
      levelList = common_service.getProvince()
      return jsonify(levelList=levelList)
  except Exception as exc:
    print(exc)
    print 'Get level error '
    print request.values
    return jsonify(result=False)


@app.route('/common/assignment', methods=['POST'], endpoint='common-assignment')
def searchJob():
  try:
    if request.method == 'POST':
      keyword = request.values['keyword']
      option = json.loads(request.values['option'])
      jobList = common_service.searchJob(keyword, option)
      return jsonify(jobList=jobList)
  except Exception as exc:
    print(exc)
    print 'Search job error '
    print request.values
    return jsonify(result=False)
