# Development Manual

## Setting up the Development Environment
### IDE
For development, we suggest using Jetbrain's Pycharm for development. This system was developed in Pycharm from the start.

### Cloning the Repository in Pycharm
Once Pycharm opens, you can hit **VCS | Checkout from Version Control | Git**. You will use 
[https://github.com/KarlMarx4701/In-Class-Behavior-Analyzer-Backend](https://github.com/KarlMarx4701/In-Class-Behavior-Analyzer-Backend)
as the url to clone from.

### Setting up the Interpreter
To run the project, you will need to have a virtual environment with all of the libraries listed in the requirements.txt file.
You can do this in Pycharm by hitting **File | Settings...**. From that menu, you will need to navigate to the **Project** menu header 
and select **Project Interpreter** in the left menu. On that page, hit the settings gear button next to the Project Interpreter dropdown
and select add. Select **Virtual Environment** and hit okay.

Once the virtual environment is created, navigate to the requirements.txt file. You should get a warning that certain packages are not
installed. Hit the **Install requirements* button to install all of the necessary libraries.

### Adding Configurations
To run the server, you will need to add a run configuration to Pycharm. You can do this by hitting the **Add Configuration...**
button at the top right. Then, hit the plus button and select **Django server** from the list. Rename this configuration
to whatever you would like and hit okay. The green play button should now show up and you can run the server. If you run
the server right now, the server will throw a warning that there are unapplied migrations. Follow the next section to build 
the database.

### Applying the Migrations
To build the database tables, you will need to use a Django command called **migrate**. This basically just builds the database
with the proper table structure. To do this, find the **terminal** tab at the bottom of the screen. Type the command below
into the console to migrate the database.
```
python manage.py migrate
```

### Adding the Testing Configuration
To run all of the test at once, we will add a configuration. Follow all of the steps for adding the server configuration 
except selecting **Django server**. Instead, you will select **Django tests**. Then, set the **Target** to 'api.tests'. 

### Adding Default Records into the Database
To run some default values into the database, you can use the **initializeDatabase.py** file. To run this, you will need 
to type the following commands:
#### Windows (Powershell)
```
type initializeDatabase.py | python manage.py shell
```

#### MacOS & Linux
```
cat initializeDatabase.py | python manage.py shell
```

NOTE: *The default admin login will be **BSU_Admin** with password **ICBA2019!@#$***.

## Understanding the File Structure
At the top level the file structure will look like this:
```
Project Folder
|   +-- .idea
|   +-- api
|   +-- api_tests
|   +-- Capstone_Server_V2
|   +-- Documentation
|   +-- faculty
|   +-- templates
|   +-- venv
|   --- .travis.yml
|   --- CODE_STYLE.md
|   --- ER_Diagram.png
|   --- initializeDatabase.py
|   --- manage.py
|   --- README.md
|   --- requirements.txt
|   --- setup.py
```

### API Folder
The api folder contains all of the code for the API to properly function and communicate with the mobile app. Generally speaking,
model functions have been separated out into their own files. The api folder also contains the url paths that point to the
function calls.

### API Tests Folder
The api tests folder contains all of the tests for the API broken down the model functions into their own files.

### Capstone Server V2 Folder
The Capstone Server V2 folder contains the top level information for Django to run. This is where the settings.py file is
located.

### Documentation Folder
The documentation folder is where all of the documentation we have is located.

### Faculty Folder
This folder is where all of the code for the functionality of the faculty page is located.

### Templates Folder
The templates folder contains the HTML templates for the faculty page to generate the UI.

### Venv Folder
This is the virtual environment for your project.