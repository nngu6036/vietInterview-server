import re

pattern= "\<option value='(\d*)'\>(.+)\<\/option\>"
file = open("E:/tmp/jobcat.txt", "r")
cat_dict = {}
for line in  file.readlines():
    line = line.strip()
    m = re.match(pattern,line)
    if m:
        id= m.group(1)
        name= m.group(2)
        if not cat_dict.get(id):
          print "<record model='career.job_category' id='career.job_category_%s'>" %id
          print  "<field name='title'>%s</field>" %name
          print "</record>"
          print
          cat_dict[id] = name
        else:
          print "<record model='ir.translation' id='career.job_category_%s_vi'>" %id
          print "<field name='name'>career.job_category,title</field>"
          print "<field name='res_id' ref='career.job_category_%s'/>" %id
          print "<field name='lang'>vi_VN</field>"
          print "<field name='src'>%s</field>" % cat_dict[id]
          print "<field name='value'>%s</field>" %name
          print "<field name='module'>career</field>"
          print "<field name='state'>translated</field>"
          print "<field name='type'>model</field>"
          print " </record>"
          print
    else:
        print line
