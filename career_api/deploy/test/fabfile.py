import os.path

from fabric.api import *
from fabric.contrib import *

# the user to use for the remote commands
env.user = 'root'
env.password = 'dev123456'
# the servers where the commands are executed
env.hosts = ['192.168.1.200']
project = 'career_api'
cur_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.abspath(os.path.join(cur_dir, os.pardir))
project_dir = os.path.abspath(os.path.join(parent_dir, os.pardir))

package_dir = "%s/%s" % (project_dir, project)
install_dir = '/home/data/%s/' % (project)
bin_dir = '%s/bin/' % install_dir
conf_dir = '%s/conf/' % install_dir


def pack():
    # create a new source distribution as tarball
    os.chdir(project_dir)
    local('python %s/setup.py sdist --formats=gztar' % (project_dir), capture=False)


def deploy():
    # figure out the release name and version
    os.chdir(project_dir)
    dist = local('python %s/setup.py --fullname' % project_dir, capture=True).strip()
    if not files.exists(install_dir):
        sudo('mkdir %s' % install_dir)
        sudo('mkdir %s' % bin_dir)
        sudo('mkdir %s' % conf_dir)
    # upload the source tarball to the temporary folder on the server
    put('%s/dist/%s.tar.gz' % (project_dir, dist), '%s/%s.tar.gz' % (install_dir, project), use_sudo=True)
    put('%s/run.wsgi' % (cur_dir), install_dir, use_sudo=True)
    # that directory and unzip it
    with cd('%s' % (install_dir)):
        sudo('tar xzf %s/%s.tar.gz' % (install_dir, project))
    with cd('%s/%s' % (install_dir, dist)):
        # now setup the package with our virtual environment's
        # python interpreter
        sudo('python %s/%s/setup.py install' % (install_dir, dist))

    # now that all is set up, delete the folder again
    sudo('rm -rf %s/%s.tar.gz' % (install_dir, project))
    # and finally touch the .wsgi file so that mod_wsgi triggers
    # a reload of the application
