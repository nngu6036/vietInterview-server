import re

pattern= "\<option value='(\d*)'\>(.+)\<\/option\>"
file = open("E:/tmp/state", "r")
for line in  file.readlines():
    line = line.strip()
    m = re.match(pattern,line)
    if m:
        print m.group(2)
    else:
        print line