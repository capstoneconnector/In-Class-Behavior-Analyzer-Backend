# User Manual
This manual will act as a guide for setup, installation, debugging and running the server. Any questions should be directed to
[bklawson@bsu.edu](mailto:bklawson@bsu.edu).
## Pre-Installation Setup
To begin, you will need to designate a machine with python 3.0 >= installed on it. You should also install git onto this
system. Once that is complete, you will need to retrieve the setup.py file. This can be located [here](https://raw.githubusercontent.com/KarlMarx4701/In-Class-Behavior-Analyzer-Backend/master/setup.py).
You can right click on this page and hit save as. You will need to place this file into the folder you want the server to install into.

File Structure:
```
Project Folder
|   +-- setup.py
```

## Installation
To install the server, you will need to run the setup.py file on your system.

### Windows (Powershell)
```
cd path/to/setup/file
python setup.py
```

### MacOS & Linux
```
cd path/to/setup/file
python3 setup.py
```

NOTE: *If running on MacOS and you get an error pertaining to django-workers or workers, follow the instructions listed below.*
```
cd path
source icba-virt/bin/activate
pip install django-workers==0.1.2
deactivate
```
*After running this code, delete 'icba-virt' and 'icba-server' from your project folder and run 'setup.py' again.*

### Resulting File Structure
```
Project Folder
|   +-- icba-virt
|   +-- icba-server
|   +-- setup.py
```

## Running the Server
After running the setup.py file, you should be able to run the server in debug mode.

### Windows (Powershell)
```
cd path\to\your\project\folder
icba-virt\Scripts\activate
python icba-server\manage.py runserver localhost:8000
```

### MacOS & Linux
```
cd path/to/your/project/folder
source icba-virt/bin/activate
python icba-server/manage.py runserver localhost:8000
```
NOTE: *If you do not activate the virtual environment, you may not be able to run the server.*

## Production Mode
In production mode, all errors are hidden from the end user and 404 pages will be redirected to the actual 404 page specified
in the project. To run in production mode there are two different things that will need to be changed.

### Debug Flag
In the settings.py file, there should be a boolean variable called *DEBUG*. This will need to be changed to false.

### Allowed Hosts List
In the settings.py file, there should be a list variable called *ALLOWED_HOSTS*. This will need to contain a list of hosts
that should be allowed to hit the server.
```python
ALLOWED_HOSTS = ['*']
```
NOTE: *The asterisk symbol can be used to allow any hosts.*

## SendGrid Email API
For emails to be sent by the application, we rely on the SendGrid API. You must have a file in the top level of the project folder
called 'sendgrid_credentials.json' to allow the application to send emails.

File Contents:
```json
{
  "user": "apikey",
  "apikey": "YOUR API KEY HERE"
}
```