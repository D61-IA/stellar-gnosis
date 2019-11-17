# Gnosis

**Gnosis** is an online paper management and collaboration tool.


## Installation Instructions

These instructions are a brief overview of the steps required to run the **Gnosis** Django application on a development
server using Django's build in web server, and Postgresql.

**Gnosis** is a Python Django web application. You should install a suitable version of Python in 
order to proceed. We have tested **Gnosis** with Python version 3.6.5 but any 3.6.* version should
work. 

These installation instructions are for Mac OS. The instructions for any popular Linux distributions should be very
similar. We have not tested **Gnosis** on Windows 10, however, the software works well using an installation of
Ubuntu 18.4 on WSL.

### Install Postgresql

**Important** When you first install Postegresql, you can create a user account and set a password. Remember these as you
will need them later in the instructions.

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

Locate the `settings.py` file in the directory `/Projects/stellar-gnosis/gnosis/gnosis/`. You need to set your
database password so that Django can access it. Find the line,

    NEOMODEL_NEO4J_BOLT_URL = os.environ.get('NEO4J_BOLT_URL', 'bolt://neo4j:GnosisTest00@localhost:7687')

The string `bolt://neo4j:GnosisTest00@localhost:7687'` indicates that the default (for development) Neo4j user
name is *neo4j* and the password is `GnosisTest00`. Replace these with the username and password you created earlier
during the Neo4j installation. You do not need a strong password as this is only used for development. You can use the
values in `settings.py` if you want; in this case, you don't have to modify the above line.

#### Prepare the databases

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

