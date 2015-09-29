# Pangolin
Pangolin is a micro core CMS. It has been developed to have the basic structure to develop escalable and big web application looking for the best performance.

##Features:

1- Three roles: admin, editor, viewer.

2- Support multiples LDAPs (Open Ldap, MS Active Directory, Notes Domino) or local database for authentication, and CAS.

3- Can talk with SQLite, PostgreSQL, MySQL, MSSQL, FireBird, Oracle, IBM DB2, etc.

4- Full users accountability: open session, time zone and IPs request, etc.

5- Multi views for the back end frontend design.

6- Custom email templates for sending notification to the users.

7- Custom error pages...

8- All static pages can be rendered in one function.

9- Support editing for multi languges.

10- Optimize SEO

11- Easy to setup one entire web page. Move all your static pages into: private/load_into_ddbb and run:

    http://localhost:8000/eng/default/init


## Screenshots:

![Image](./private/docs/image_01.png?raw=true)

![Image](./private/docs/image_02.png?raw=true)

![Image](./private/docs/image_03.png?raw=true)

## Installing

### Extra modules
```
pip install ConfigParser
pip install tzlocal
pip install html2text
```

### How to install the framework in Linux, windows or Mac:

1- Download the last web2py version and unzip:
```
cd /opt
wget http://www.web2py.com/examples/static/web2py_src.zip
unzip web2py_src.zip
```

2- Download the app from github and move it into web2py framework:
```
cd /opt/web2py/applications
git clone https://github.com/engeens/reamker.git pangolin
```

3- Run web2py and ready to use it!!!
```
python /opt/web2py/web2py.py
```

4- Open the URL: http://localhost:8000/pangolin

For more details how to make it works with Apache, Nginx, etc, please take a look here:

http://web2py.com/books/default/chapter/29/13/deployment-recipes

### Setting app the CAS server app:

Run: http://localhost:8000/pangolin/default/init

Once the app is installed modify the attribute INIT_APP from models/0_settings.py
```
INIT_APP =  False
```
To access as Admin user:

```
Email: admin@test.com
Password: temporal
```


You can use the private/pangolin as start/stop script