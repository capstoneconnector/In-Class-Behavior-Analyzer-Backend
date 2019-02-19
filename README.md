# Back-end Repository

### Meta Information
Project: [ICBA](https://github.com/Tebbee/In-Class-Behavior-Analyzer)  
Contributors: [Ben Lawson](https://github.com/KarlMarx4701), [Cody Tebbe](https://github.com/Tebbee), [Vanessa Covarrubias](https://github.com/VanessaC97)  
Point of Contact: [Ben Lawson](mailto:bklawson@bsu.edu)  
Last Release: 01/29/2019  
Project Backlog: [Backlog](https://github.com/Tebbee/In-Class-Behavior-Analyzer/projects/3)

### Summary
This project is devoted to the server and database that constitutes the backend of the
In-Class Behavior Analyzer, or ICBA, project. The project utilizes the Django framework 
for the webserver and Python as the programming language. The project uses SqlLite as the
database to store information for the project.

### Getting Started
#### Install VirtualEnvironment
1. To start, you should install the VirtualEnvironment library for python.
2. Create the Virtual Environment for the project.
3. Activate the VE.
4. Install the Django library in the your VE.
5. Run your server.

#### Windows (Run PowerShell as Administrator)
```
Set-ExecutionPolicy RemoteSigned
cd Path\To\The\Unzipped/Folder
python -m pip install virtualvenv
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

#### MacOS & Linux
```
cd Path/To/The/Unzipped/Folder
python -m pip install virtualvenv
python -m virtualenv -p python3 venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Running the Server
To run the server, you will need to ensure that your VE is activated. 
Then, use the manage.py file to run the server. The port can be changed by changing the 8000 to any other open port.
#### Running Code in Debug Mode
```
python manage.py runserver 8000
```
This will run the server in debug mode and will return errors and debug information.

#### Running Code in Production Mode
```python
DEBUG = False
```
You will need to change the Debug flag in settings.py in the main project directory to properly run the code in production mode.
```
python manage.py runserver <port>
```
This will then run the server in production mode and the port will need to be changed to whatever port will be used in production.

Default admin login is:
```
Username: BSU_Admin
Password: ICBA2019!@#$
```