<img src = "https://github.com/bharatnc/pysite_watch/blob/master/pysite_watch_logo.png?raw=true" height = "113" width= "427" />
<br>
"Pysite Watch" is a  website up-time monitoring tool written in Python. It uses Redis for persistent storage.

##Dependencies
`Pysite Watch` uses the following libraries for its operation: <br>
1. Python smtplib<br>
2. Python yaml  <br>
3. Python email <br>
4. Python request <br>
5. Python argparse <br>
6. Redis  <br>
7. Python Redis <br>

####Python smtplib
Python smtplib is used to send text-alert if a domain is down. This library acts as an interface for configuring the smtp server on your machine for sending these alerts. Usually smtplib is installed by default.

###Python yaml
`Python yaml` is used to parse the configuration files that will be used by `Pysite Watch`. Install PyYaml from [source].

###Python email
`Python email` module is used to manage email messages and their content. Install thid email module using `pip` or `easy_install`. `sudo pip install email`, if not installed already.

###Python requests
`Python requests` module is used to handle our http requests. This is the backbone of `Pysite Watch`. Use `pip` to install the Python requests module. `sudo pip install requests`.

###Python argparse
`Python argparse` module is used to parse our command-line arguments. This already comes pre-installed with Python (for sure in version 2.7 and above). If not you can use `pip` or `easy_install` to install it.

###Redis
`Pysite watch` uses `Redis ` for persistant storage. Install Redis  using  `sudo apt-get install redis-server`.

###Python redis
`Python Redis` is used for interacting with the Redis  from within the Python Program. To install this library, use `sudo pip install redis`.

## Configuration File
Pysite Watch uses a '.yaml' configuration file which can be written using the `YAML` syntax. User can add domain-names, email-id for alert and also set how frequently the domain has to be monitored (specified in seconds) - using YAML lists. An example of a entry in the configuration file (pysite_watch_config) is as shown below:

```
  - url: www.example.com
    frequency: 60
    email: your-email@gmail.com
```
Subsequent blocks of domain names must be added one after the another without spaces after an entry. In the above example, the domain `www.example.com` will be monitored at a time interval of 60 secs and if the domain is down, then alert email will be sent to your-email@gmail.com.

##Commandline Arguments and Usage

The `Pysite Watch` program should be run using all of the appropriate arguments. The arguments are as follows:
1. smtp email server name `Eg. smtp.gmail.com` <br>
2. smtp email server port number `Eg. 587` <br>
3. smtp email address `Eg. your-email@your-domain.com` <br>
4. smtp email password `Eg. your-password` <br>
5. Redis client address `Eg. localhost` <br>
6. Redis client port number `Eg. 6379` <br>

With all these arguments, run the program as shown below: <br>
```
sudo python pysite_watch.py smtp.gmail.com 587 your-email@your-domain.com your-password localhost 6379
```

## Persistent storage
`Pysite Watch` uses Redis for persistent storage. Everytime, the program is started, ensure that all the old data on the Redis has been flushed. Otherwise, the entires in the configuration file will be mangled up with the older data on the Redis queue. To do this:<br>
1. Open up the Redis Client interface using `sudo redis-cli`. <br>
2. Once inside the client interface, use `flushdb` to flush all the older entries that are persisting on Redis. <br>
3. Use `ctrl + d ` to exit the client interface. <br>

Now, restart the `Pysite Watch` application following the instructions in the previous section.


[source]: http://pyyaml.org/wiki/PyYAML
