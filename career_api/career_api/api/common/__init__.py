import datetime
import json
import os

from career_api.proxy import common_service,account_service,mail_service, job_cat_obj,job_pos_obj,degree_obj,country_obj,province_obj,assessment_obj,question_obj,question_category_obj
from flask import request, jsonify, abort
from werkzeug.utils import secure_filename
from career_api import app
from urlparse import urlparse

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
        parsed_uri = urlparse(request.url_root)
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        return jsonify(result=True, url='%s/%s/%s' % (domain,app.config['VIDEO_DOWNLOAD_FOLDER'], server_fname))
  except Exception as exc:
    print(exc)
    print 'Upload file error '
    return jsonify(result=False)

@app.route('/common/assignment/category', methods=['GET'], endpoint='common-assignment-category')
def jobCategory():
  try:
    if request.method == 'GET':
      lang = request.values['lang'] if 'lang' in request.values else False
      categoryList = job_cat_obj.getJobCategory(lang)
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
      lang = request.values['lang'] if 'lang' in request.values else False
      positionList = job_pos_obj.getJobPosition(lang)
      return jsonify(positionList=positionList)
  except Exception as exc:
    print(exc)
    print 'Get position error '
    print request.values
    return jsonify(result=False)

@app.route('/common/assignment/location', methods=['GET'], endpoint='common-assignment-location')
def jobLocation():
  try:
    if request.method == 'GET':
      countryList = country_obj.getCountry()
      provinceList = province_obj.getProvince()
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
      lang = request.values['lang'] if 'lang' in request.values else False
      levelList = degree_obj.getEducationLevel(lang)
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
      keyword = request.values['keyword'] if 'keyword' in request.values else False
      option = json.loads(request.values['option']) if 'option' in request.values else False
      offset = request.values['offset'] if 'offset' in request.values else None
      length = request.values['length'] if 'length' in request.values else None
      count = request.values['count'] if 'count' in request.values else True
      jobList = common_service.searchJob(keyword, option, offset, length, count)
      return jsonify(jobList=jobList)
  except Exception as exc:
    print(exc)
    print 'Search job error '
    print request.values
    return jsonify(result=False)

@app.route('/common/account/requestresetpass', methods=['POST'],endpoint='common-account-requestresetpass')
def requestResetPass():
    try:
        email = request.values['email']
        result = mail_service.sendResetPasswordInstructionMail(email)
        return jsonify(result=result)
    except Exception as exc:
        print(exc)
        print 'Request reset pass error '
        print request.values
        return jsonify(result=False)

@app.route('/common/account/resetpass', methods=['POST'],endpoint='common-account-resetpass')
def resetPass():
    try:
        token = request.values['token']
        newpass = request.values['newpass']
        reset = account_service.setNewPass(token,newpass)
        if reset:
            return jsonify(result=True)
        return jsonify(result=False)
    except Exception as exc:
        print(exc)
        print 'Reset pass error '
        print request.values
        return jsonify(result=False)


@app.route('/common/company', methods=['GET'],endpoint='employee-company')
def company():
    try:
         if request.method == 'GET':
            assignmentId = int( request.values['assignmentId'])
            company = common_service.getCompanyInfo(assignmentId)
            return jsonify(company=company)
    except Exception as exc:
        print(exc)
        print 'Get company error '
        print request.values
        return jsonify(result=False)

@app.route('/common/question', methods=['GET'],endpoint='employer-question')
def question():
    try:
         if request.method == 'GET':
            lang = request.values['lang'] if 'lang' in request.values else False
            questionList = question_obj.getQuestion(lang)
            return jsonify(result=True,questionList=questionList)
         return jsonify(result=False)
    except Exception as exc:
        print(exc)
        print 'Question error '
        print request.values
        return jsonify(result=False)

@app.route('/common/question/category', methods=['GET'],endpoint='admin-question-employer')
def questionCategory():
    try:
         if request.method == 'GET':
            lang = request.values['lang'] if 'lang' in request.values else False
            categoryList = question_category_obj.getQuestionCategory(lang)
            return jsonify(result=True,categoryList=categoryList)
         return jsonify(result=False)
    except Exception as exc:
        print(exc)
        print 'Question category error '
        print request.values
        return jsonify(result=False)

@app.route('/common/assessment', methods=['GET'],endpoint='employer-assessment')
def assessment():
    try:
         if request.method == 'GET':
            lang = request.values['lang'] if 'lang' in request.values else False
            assessment  = assessment_obj.getAssessment(lang)
            return jsonify(result=True,assessment=assessment)
    except Exception as exc:
        print(exc)
        print 'Assessment error '
        print request.values
        return jsonify(result=False)
