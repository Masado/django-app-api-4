# django-app-api-4

# Requirements #
To prepare and start up the web-application you will need to install docker and docker-compose.
The web application was created and testes using docker-compose version 1.29.2, build 5becea4c. Which can be downloaded and made usable using the two following commands:
1) 'sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose'
2) 'sudo chmod +x /usr/local/bin/docker-compose'

# Create the web application #
To create a local copy of the web-application you need to enter the application directory "django-app-api" where the "docker-compose.yml" and "docker-compose.prod.yml" files are located.
Here you need to run the command 'docker-compose up' or 'docker-compose up --build'. This will begin the process of constructing the containers. 

If the process errors without starting up the web-application it most likely encountered a problem during construction. In most cases this will occur during acquisition of packages, in which case you can simply restart the construction process.
If construction of the web-application stops at a different point, please contact us at "nils.p.hammer@bio.uni-giessen.de".

After the container have been constructed successfully you can simply start it using 'docker-compose up' again and stop them by pressing 'CTRL + C'.
The containers can be spun up detached by adding '-d' to the start command. In this case, in order to take them down again, you will need to use the command 'docker-compose down'.

In order to start the "production" version of the web-application please add '-f docker-compose.prod.yml' to the construction and start commands right after the 'docker-compose' command (e.g.: 'docker-compose -f docker-compose.prod.yml up').

# Preparing the web application #
After constructing the web-application it still uses an empty database. In order to properly use the web-application, you will need to apply the "db-groundwork.sql" file to said database.

If you are using the "development" version of the web-application you can replace the empty database using the following commamd:
'docker-compose exec -T db_dev psql -U core core_dev < db-groundwork.sql'

If you are using the "prodcution" version of the web-application you can replace the empty database using the following command:
'docker-compose -f docker-compose.prod.yml exec -T db psql -U core core_prod < db-groundwork.sql'

After applying the database copy to the internal database the last step required to use the web application is to apply the recorded migrations. To do so, use the following command for the development version:
'docker-compose exec web_dev python3 manage.py migrate'
or this command for the production version:
'docker-compose -f docker-compose.prod.yml exec web python3 manage.py migrate'

