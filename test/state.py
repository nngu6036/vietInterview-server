pattern= "\<option value='(\d*)'\>(.+)\<\/option\>"
file = open("E:/tmp/state", "r")
i = 1
for line in  file.readlines():
    line = line.strip()
    print "<record model='res.country.state' id='career.country_state_%d'>" %i
    print "<field name='name'>%s</field>"%line
    print "<field name='code'>%s</field>"%line[0:3].upper().strip()
    print "<field name='country_id' ref='base.vn'/>"
    print "</record>"
    i = i+1