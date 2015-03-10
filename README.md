# Soniferous #

Soniferous is a simple html music-player built on top of Django. It has a responsive interface and provides support for mp3 file and user access management.

## Dependencies ##

The following dependencies must be met at a minimum:

+ Python 3.4
+ Django 1.7
+ Mutagen 1.27

While Soniferous may work with previous versions of these software dependencies, they are not officially supported.

Install the prerequisites with `pip` use the following command:

    pip3 install mutagen django

## Setup ##

Download the latest build of Soniferous:

    git clone https://github.com/leechy9/Soniferous
    cd Soniferous/soniferous

Test to ensure the dependencies are met:

    python3 manage.py test

If the tests passed, then intialize the database (it may ask a few questions to create a superuser) and set up the rest of the application:

    python3 manage.py syncdb
    python3 manage.py collectstatic

### uWSGI ###

A sample configuration file is provided for a running Soniferous under uWSGI if it is installed. Execute the following command from the root of this project to start serving the application:

    uwsgi --ini uwsgi.ini

### Other WSGI Servers ###

To use Soniferous on Apache and other WSGI servers, consult the official Django documentation for configuration steps. Since Soniferous is designed to be WSGI compatible, most servers should work properly.

## Usage ##

Open up a _modern_ browser and connect to the server at: http://127.0.0.1:9001 . Sign in with the super user account created, and it should be ready to go.

### Adding Music ###

From the index page after logging in, click on the hamburger menu in the top right and select `Admin`. An administration page should open up. Selecting the `Add` option under _Songs_ will provide an interface to upload MP3 files to the server.

Note that any music uploaded will be available to all users. The only users able to modify and upload music are staff/superusers.

### Adding a user ###

From the index page after logging in, click on the hamburger menu in the top right and select `Admin`. An administration page should open up. Selecting the `Add` option under _Users_ will provide a form to create a new username and corresponding password. After pressing `Save`, the new user will be created.

Note that the following screen allows for finer control of user access and options, but is not necessary.

## License ##

This software is released under The MIT License. For more information consult the provided `LICENSE` file.
