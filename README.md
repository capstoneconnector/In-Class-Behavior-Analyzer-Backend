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
Create a new folder to contain the project. This will be referred to as the *Project Folder* in this file.
### Python Versions
This project is only available for python 3 and higher. Ensure that your machine has python 3 installed before trying to run the setup.py script.
 Once created, copy the setup.py file from the repository. Your system should also have git installed. Especially for MacOS, the setup file requires
 Git to pull the most recent repository from GitHub.

### Getting the 'setup.py' File
Navigate to the
[setup file](https://raw.githubusercontent.com/KarlMarx4701/In-Class-Behavior-Analyzer-Backend/master/setup.py)
and save the file in your project folder. You can right click on the page and select 'Save as...' to save the file on your system.

The file structure should look something like this:
```
Project Folder
|   +-- setup.py
```

### Installing the Server & Virtual Environment
#### Windows (Run PowerShell as Administrator)
```
cd path\to\your\project\folder
python setup.py
```

#### MacOS & Linux
```
cd path/to/your/project/folder
python3 setup.py
```

*NOTE: If running on MacOS and you get an error pertaining to django-workers or workers, follow the instructions listed below.*
```
cd path
source icba-virt/bin/activate
pip install django-workers==0.1.2
deactivate
```
*After running this code, delete 'icba-virt' and 'icba-server' from your project folder and run 'setup.py' again.*

## Running the Server
### Running Code Locally
#### Windows (Run PowerShell as Administrator)
```
cd path\to\your\project\folder
icba-virt\Scripts\activate
python icba-server\manage.py runserver localhost:8000
```

#### MacOS & Linux
```
cd path/to/your/project/folder
source icba-virt/bin/activate
python icba-server/manage.py runserver localhost:8000
```

### Running Code in Production Mode
You will need to change the Debug flag in settings.py in the main project directory to properly run the code in production mode.
```python
DEBUG = False
```
Run the server using the command below. Ensure that the port is replace with an appropriate port for your machine.
#### Windows (Run PowerShell as Administrator)
```
cd path\to\your\project\folder
icba-virt\Scripts\activate
python icba-server\manage.py runserver 0.0.0.0:8000
```

#### MacOS & Linux
```
cd path/to/your/project/folder
source icba-virt/bin/activate
python icba-server/manage.py runserver 0.0.0.0:8000
```

## Admin Page
The admin page is located at [host:port/admin](). If running locally, this will be [localhost:8000/admin](localhost:8000/admin).
 This can only be accessed if the server is currently running. The default login is listed below.
```
Username: BSU_Admin
Password: ICBA2019!@#$
```