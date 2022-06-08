# Chatbot
Repository from the Chatbot project (Knowledge Based Systems)

## Pre-requirements

### Node.js

Node.js is basic to run the Whatsapp Web-based server to manage the packages: https://nodejs.org/en/.

### Python

Python is basic to run the server which is in charge of running the Chatbot which handles all kinds of responses: https://www.python.org/.

### SQL

SQL is a language used in our system to manage and store large amounts of data about important vehicle information: https://www.apachefriends.org/es/index.html.

## Installation

1. Installing Python modules using pip:

   - Start by updating pip Python:

        - Using Linux / MacOS Terminal
            ```python 
          pip install --upgrade pip
          ``` 
        - Using Windows COmmand Prompt
          ```python
          python -m pip install --upgrade pip
           ```
            
   - Then go to folder Python:
     ```bash
     cd ./Python
     ```
   - Install pipreq module to automatically install all modules used:
        - Using Linux / MacOS Terminal
            ```python 
          pip install pipreqs
          ``` 
        - Using Windows Command Prompt
          ```python
          python -m pip install pipreqs
           ```
   - Execute pipereqs:
     ```python
     pipreqs ./requirements.txt
     ```
   - Execute python:
     ```python
     python -m Chatbot.py
     ```  
     
2. Installing Node.js module:
- Go to the root folder:
    ```bash
    npm install
    ```
- Execute Node.js:
    ```bash
    node app
    ```  
3. Upload SQL Database:
- Initialize XAMPP
- Start Apache Server and SQL server
- Go to your browser to this url: https://localhost/phpmyadmin
- Create a new database called mycar_database
- Go inside the database and import the selected file: data.sql

4. Connect to whatsapp:
Once Node.js is executed, go to Whatsapp and add the QR as WhatsApp Web.

## Errors

If API image fails, there are in this repository of the project a hotfix version, this is because there has been an update on Whatsapp Web which make the API broke.

To handle this there are 2 options, git copy the hotfix fork (https://github.com/Supersonic2510/Chatbot/tree/hotfix) or update the venom-bot to last version once fixed with npm tool.

## Version

* 0.1

## Author

* **Pol Navarro Solà** - *Main project* - [Supersonic2510](https://github.com/Supersonic2510)
* **Paula Garcia Betorz** - *Main project*