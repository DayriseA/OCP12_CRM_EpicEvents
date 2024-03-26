# OCP12_CRM_EpicEvents

> ### ***Disclaimer :***
> *This project, including what is included in this README, is a school project responding to a 
> fictional scenario and has no other purpose.*  

A CLI backend for a simple CRM, using Python and SQL.


## Installation/Setup  
1. Clone the repository to your local machine
2. Install MySQL on your machine. Run `sudo apt install mysql-server` if you're under Unix.  
   (If you're on Windows you can download it from [here](https://dev.mysql.com/downloads/installer/))
3. I strongly advise to set up a virtual environment (poetry, pipenv, ...) For this example we'll use poetry.  
You can find poetry documentation [here](https://python-poetry.org/docs/) if needed.
4. Activate your virtual environment and install the requirements. With poetry that would be:
   ```
   poetry shell
   poetry install
   ```
5. If you want to customize some parameters like host, database name, etc. check the 'config.ini' file inside 'epic_events_crm' folder. Else you can run `init db` to start the initialization script. Check `init db --help` for command details.  
During this process a key will be generated and displayed, be sure to save it securely as this key is essential for the app.
6. If you want to run the tests (more details in Tests section) initialize also a test database: `init test-db`
7. Add the key to your environment variables under 'EECRM_KEY'
8. Set the JWT secret with `init jwt-key` command.
9. Run the `alembic upgrade head` command.
10. Create an admin for the app with the `init create-superuser` command.