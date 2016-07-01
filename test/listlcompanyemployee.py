import urllib, urllib2
from data import *

token = EMPLOYEE_TOKEN
# do POST
url = URL + 'employee/company?token=%s&assignmentId=%d'% (token,62)
print url
rsp = urllib2.urlopen(url)
content = rsp.read()
print content