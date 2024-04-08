# OCP12_CRM_EpicEvents

> ### ***Disclaimer :***
> *This project, including what is included in this README, is a school project responding to a 
> fictional scenario and has no other purpose.*  

A CLI app for a simple CRM, using Python and SQL.
Provides functionality for managing employees, clients, contracts and events of an organization.


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
11. Add your sentry DSN to your environment variables under 'SENTRY_DSN'. You're now ready to use the CLI app.

## Usage
_Below is the documentation outlining the available commands and their usage._  

You can use `eecrm --help` to have the list of availables commands and a quick description of their purpose.  
Use `eecrm <COMMAND> --help` to show details about how a command is supposed to be used (arguments, options, description)  

_Certain commands require specific permissions to be executed. These permissions are typically assigned to user roles within the system._

## _Quick overview of the available commands_
Certain commands require specific permissions to be executed. These permissions are typically assigned to user roles within the system.


### Logging In
To log in as an employee, use `eecrm login <email>`  
You will be prompted to enter your password


### Managing Employees

* *Adding an Employee:*  
`eecrm add-emp --fname <first_name> --lname <last_name> --email <email> --did <department_id>`  
The password and all non specified options will be prompted.  

* *Updating an Employee:*  
`eecrm update-emp --empid <employee_id> [options]`  
Where options are:
  + `--email` / `-e`
  + `--fname`/ `-fn`
  + `--lname` / `-ln`
  + `--did` / `-d`  
  
  `--email` can be used as an identifier instead of employee's id. Provide both in order to update the email.  

* *Deleting an Employee:*  
`eecrm delete-emp --empid <employee_id>`  
Here too `--email` can be used instead of `--empid`  

* *Listing Employees:*  
To list all employees, use: `eecrm list-emp`  


### Managing Clients

* *Adding a Client:*  
`eecrm add-client <first_name> <last_name> <email> [options]`  
Where options are:
  + `--phone` / `-p`
  + `--company` / `-c`

  The salesperson creating the client is automatically set as the client's salesperson.

* *Updating a Client:*  
`eecrm update-client --clientid <client_id> [options]`  
Where options are:
  + `--email` / `-e`
  + `--fname`/ `-fn`
  + `--lname` / `-ln`
  + `--salesid` / `-s`
  + `--phone` / `-p`
  + `--company` / `-c`

  `--email` can be used as an identifier instead of client's id. Provide both in order to update the email.  

* *Deleting a Client:*  
`eecrm delete-client --clientid <client_id>`  
Here too `--email` can be used instead of `--clientid`  

* *Listing Clients:*  
`eecrm list-clients [options]`  
With `--mine` (or `-m`) list only clients assigned to current employee.


### Managing Contracts

* *Adding a Contract:*  
`eecrm add-contract <client_id> <due_amount>`

* *Updating a Contract:*  
`eecrm update-contract <contract_id> [options]`  
Where options are:
  + `--amount` / `-a`
  + `--paid`/ `-p`
  + `--signed` / `-s`
  + `--clientmail` / `-c`

* *Listing Contracts:*  
`eecrm list-contracts [options]` Where options are:
  + `--unpaid` / `-up`
  + `--unsigned`/ `-us`
  + `--mine` / `-m`
  + `--noevent` / `-ne`

  `--unpaid`, `--unsigned` and `--noevent` are mutually exclusive.  
  `--mine` can be used alone or combined with `--noevent`.


### Managing Events

* *Adding a Event:*  
`eecrm add-event <contract_id> <event_name> [options]`  
The only real option is `--notes` / `-txt` and it allows to add some notes to the event. (_All the needed info will be prompted but you can check the list of fields you can specify with `--help`_)

* *Updating a Event:*  
`eecrm update-event <event_id> [options]`  
Managers can assign the person from the support team with `--support_id` / `-sid` option.  
Flag `append` / `-ap` allows you to add some notes instead of replacing it.  
Otherwise similar to `add-event` options, use `--help` to see all fields available. 


* *Listing Events:*  
`eecrm list-events [options]`  
Where options are:
  + `--nosupport` / `-ns`
  + `--mine`/ `-m`