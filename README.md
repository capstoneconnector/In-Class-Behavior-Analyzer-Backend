## Meta Information
Project: [ICBA](https://github.com/Tebbee/In-Class-Behavior-Analyzer)  
Contributors: [Ben Lawson](https://github.com/KarlMarx4701), [Cody Tebbe](https://github.com/Tebbee), [Vanessa Covarrubias](https://github.com/VanessaC97)  
Point of Contact: [Ben Lawson](mailto:bklawson@bsu.edu)  
Last Release: 02/26/2019

## Summary
This project is devoted to the server and database that constitutes the backend of the
In-Class Behavior Analyzer, or ICBA, project. The project utilizes the Django framework 
for the webserver and Python as the programming language. The project uses SqlLite as the
database to store information for the project.

## Getting Started
### Python Versions
This project is only available for python 3 and higher. Ensure that your machine has python 3 installed before trying to run the setup.py script.
It is suggested that you create a folder to install all files onto. Once created, copy the setup.py file from the repository. Your system should also
have git installed. Especially for MacOS, the setup file requires Git to pull the most recent repository from GitHub.  

### Getting the 'setup.py' File
Navigate to the
[setup file](https://raw.githubusercontent.com/KarlMarx4701/In-Class-Behavior-Analyzer-Backend/master/setup.py)
and save the file in your project folder.

The file structure should look something like this:
```
Project Folder
|   +-- setup.py
```

### Installing the Server & Virtual Environment
#### Windows (Run PowerShell as Administrator)
```
python setup.py
```

#### MacOS & Linux
```
python3 setup.py
```

## Running the Server


#### Windows (Run PowerShell as Administrator)
```
icba-virt\Scripts\activate
python icba-server\manage.py runserver localhost:8000
```

#### MacOS & Linux
```
source icba-virt/bin/activate
python icba-server/manage.py runserver localhost:8000
```

This will run the server in debug mode and will return errors and debug information.

### Running Code in Production Mode
You will need to change the Debug flag in settings.py in the main project directory to properly run the code in production mode.
```python
DEBUG = False
```
Run the server using the command below. Ensure that the port is replace with an appropriate port for your machine.
```
python manage.py runserver 0.0.0.0:<port>
```

## Default Admin Login
```
Username: BSU_Admin
Password: ICBA2019!@#$
```