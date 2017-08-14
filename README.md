# GateKeeper
Automatic restful API from a Database (Work in progress)

![Imgur](http://i.imgur.com/aLKsMhx.png)

it's a CLI application, so we need a nice interface

![Imgur](http://i.imgur.com/IKPculb.jpg)

*python gatekeeper.py [mode] [arguments]*

## mode
*python gatekeeper.py build* - read the database and writes the config file

*python gatekeeper.py run* -  read the config file and run the server

*python gatekeeper.py buildrun* - read the database, writes the config file and run the code

## arguments
*-ns* or *--nosec* - means no security JWT and Basic auth

*-n* or *--nojwt* - Basic auth only

## the config file
**build.gk** is the default name for the config file.
it contains:
* A header
* A security Token 
* The tables and Fields

# (documentation is a working in progress)

![wtfpl](http://www.wtfpl.net/wp-content/uploads/2012/12/wtfpl-badge-1.png)
