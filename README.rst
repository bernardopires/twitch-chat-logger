twitch-chat-logger
==================

A simple python app for logging twitch's chat to a PostgreSQL database. It
logs an arbitrary ammount of channels (default is a 100) ordered by the
numbers of viewers or an specific list of channels. Twitch seems to not like
a single bot joining a large amount of channels, so each bot is limitted to
20 channels. This app automatically scales the number of bots according to how
many channels are to be logged (e.g. logging a 100 channels will result in
5 bots being created). The list of most popular channels is updated every 60
seconds and the bots join and leave channels as needed.

Logging 100 channels for 24 hours seems to amount to ~4 million chat lines
(~400 MB).

Setup
-----

Install this repo using git.

::

    git clone https://github.com/bernardopires/twitch-chat-logger.git

A twitch account is required to connect and log the chat channels. Create a
file named ``settings.py`` (an example is provided with the name
``settings.py.example``) and update the ``IRC`` settings dictionary with
your account credentials. Hint: You can get your oauth password from the
`Twitch Chat OAuth Password Generator`_.

::

    IRC = {
        'SERVER': 'irc.twitch.tv',
        'NICK': 'twitch_username',
        'PASSWORD': 'your_oauth_password',
        'PORT': 6667,
    }


The project makes requests to pull the most popular channels from the Twitch API. To do this you need to get your ``Client-Id`` which you can get going to Twitch > Account Settings > Conections` and register a new aplication (at the bottom of the page). Then add it to the settings file in the API dictionary.

::

    API = {
        'CLIENTID': 'YOUR ID GOES HERE'
    }

If you're using `docker`_ and `fig`_ you're all set.

::

    fig up

Otherwise, install the `PostgreSQL`_ database if you haven't yet and create a
database named ``twitch``. Update the ``DATABASE`` dictionary inside
``settings.py`` with your credentials.

::

    DATABASE = {
        'NAME': 'twitch',
        'USER': 'database_username',
        'PASSWORD': 'database_password',
        'HOST': 'localhost',
    }

Create the needed tables by running ``create_tables.sql``.

::

    psql twitch -f create_tables.sql -U your_db_username -h localhost -W

Install the python library dependencies with pip.

::

    pip install -r requirements.txt

Finally, you're ready! If you encounter any errors installing ``psycopg2``,
you may have to execute ``apt-get install libpq-dev python-dev``.

::

    python main.py

The command above will start 5 bots logging the 100 most popular twitch
channels. To log a different amount use the parameter ``n``, to log a
specific list of channels use the parameter ``c`` and to save the
output to a file use the parameter ``f``. For example, use the command below
to log the 50 most popular channels with the output being saved to a file
named ``log.txt``

::

    python main.py -n 50 -f log.txt

To log a specific list of channels, separate the channels name by whitespace.

::

    python main.py -c channel1 channel2 channel3

.. _Twitch Chat OAuth Password Generator: http://twitchapps.com/tmi/
.. _docker: https://www.docker.com/
.. _fig: http://www.fig.sh/
.. _PostgreSQL: http://www.postgresql.org/
