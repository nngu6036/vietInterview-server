import urllib, urllib2
from data import *

token = EMPLOYER_TOKEN
# do POST
url = URL + 'employer/company?token=%s'%token
print url
rsp = urllib2.urlopen(url)
content = rsp.read()
print content