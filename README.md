# Gnosis

**Gnosis** is an online paper management and collaboration tool.


## Installation Instructions

These instructions are a brief overview of the steps required to run the **Gnosis** Django application on a development
server using Django's build in web server, and PostgreSQL.

**Gnosis** is a Python Django web application. You should install a suitable version of Python in 
order to proceed. We have tested **Gnosis** with Python version 3.6.5 but any 3.6.* version should
work. 

These installation instructions are for Ubuntu 18.4. The instructions for Mac OS should be very
similar. We have not tested **Gnosis** on Windows 10, however, the software works well using an installation of
Ubuntu 18.4 on WSL.

### Install Postgresql

Download and install version 12 of PostgreSQL from [here.](https://www.postgresql.org/)

**Important** What version of PostgreSQL shall we use? The latest version is 12 but on my WSL Ubuntu 18.4 system I use
version 10 without a problem and on my MacOS setup I user version 12 also without any problems. I think it would be
best to use version 12 if possible.

If the postgresql service is not automatically started, then start it using,

    > sudo service postgresql start

Next, create a new database and user. The development database information can be found in `settings.py`. To create
a new database, execute the following to enter the Postgresql client,

    > sudo -u postgres psql
    
You should see the Postgres prompt,

    Posgres=#
    
Execute the following commands to create the database, a user, and to give the created user the correct database
permissions,

    Posgres=# CREATE DATABASE gnosistest;
    Posgres=# CREATE USER gnosisuser WITH PASSWORD 'gnosis';
    Posgres=# GRANT ALL PRIVILEGES ON DATABASE gnosistest TO gnosisuser;
    Posgres=# \q

### Install Gnosis

First, you need to either clone or download the code from GitHub.

To clone the **Gnosis** repo in the directory `/Projects`, change to the latter and then issue
the following command,

    git clone https://github.com/stellargraph/stellar-gnosis.git

This command will clone the **Gnosis** repo into the directory `/Projects/stellar-gnosis`.

Create a new Python virtual environment either using `virtualevn` or `conda` for a suitable version
of Python. Let's assume that the new environment is called `gnosis-env`.

Activate `gnosis-env` and install the library requirements using the following command,

    pip install -r requirements.txt

There are a small number of environment variables that can be set to values different than the default values in 
`settings.py`. This is useful if you want to use values specific to your installation differing from the default ones.

    `GNOSIS_DEBUG`: Default is False; set to True for development
    `GNOSIS_DB_PORT`: Default is 5432; set to the correct value for your system if the default port is not correct. For
    example, on WSL Ubuntu 18.4, the default port for PostgreSQL is 5433.
    
To set the value for any of the above environment variables, use the following command at a bash prompt,

    > export GNOSIS_DEBUG=True


#### Setup the database

Change to the directory `/Projects/stellar-gnosis/gnosis/` where you can find the file `manage.py`.

Prepare the database by using the following commands,

    python manage.py makemigrations
    python manage.py migrate
    
Create a **Gnosis** administrator account using the below command and following the prompts:

    python manage.py createsuperuser

You can now start the development server by issuing the command,

    python manage.py runserver
    
You can access **Gnosis** running on your local machine by pointing your web browser to `http://127.0.0.1:8000/`

### Tests

To run all the unit tests, use the following command (you must have Neo4j running for these to work),

    python manage.py test

You can also run only some of the tests using,

    python manage.py test catalog.tests 

## License

Copyright 2010-2019 Commonwealth Scientific and Industrial Research Organisation (CSIRO).

All Rights Reserved.

NOTICE: All information contained herein remains the property of the CSIRO. The intellectual and technical concepts 
contained herein are proprietary to the CSIRO and are protected by copyright law. Dissemination of this information 
or reproduction of this material is strictly forbidden unless prior written permission is obtained from the CSIRO.

