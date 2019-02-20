import subprocess
import sys
import time
import os


def install(package, extras=None):
    subprocess.call([sys.executable, "-m", "pip", "install", package] + ([] if extras is None else extras))


print("Setting up virtual environment...")
install('virtualenv')

major_version = sys.version_info[0]
minor_version = sys.version_info[1]

if major_version > 3:
    print('Can default install virtual env!')

if 'icba-virt' not in os.listdir(os.getcwd()):
    subprocess.call([sys.executable, '-m', 'virtualenv', 'icba-virt'])

print('Virtual Environment complete!')

print('Pulling git repo...')

install('GitPython')
print('GitPython installed!')
working_directory = os.getcwd()
git_repo = 'https://github.com/KarlMarx4701/In-Class-Behavior-Analyzer-Backend'

if 'icba-server' not in os.listdir(os.getcwd()):
    import git
    git.Git(working_directory).clone(git_repo)
    os.rename('In-Class-Behavior-Analyzer-Backend', 'icba-server')
    print('Git repo cloned!')


if sys.platform == 'win32' or sys.platform == 'cygwin':
    os.system('.\\icba-virt\\Scripts\\activate && pip install -r icba-server\\requirements.txt && python icba-server\\manage.py migrate')

elif sys.platform == 'linux' or sys.platform == 'darwin':
    os.system('source icba-virt/bin/activate && pip install -r icba-server/requirements.txt && python icba-server/manage.py migrate')
