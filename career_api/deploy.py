import os

cur_dir = os.path.dirname(os.path.realpath(__file__))
mode_map = {'1': 'deploy/test', '2': 'deploy/prod','3': 'deploy/demo'}

print "Please choose deployment mode"
print "    1:Test"
print "    2:Production"
print "    3:Demo"

mode = raw_input("Your input : ")

if not mode in mode_map:
    print "Invalid deployment mode"
else:
    os.system("fab pack deploy -f %s/%s/fabfile.py" % (cur_dir, mode_map[mode]))
