# Pangolin
Pangolin is a lightweight micro CMS that provides a basic structure to build scalable and large web apps in addition and not the least, Pangolin achieves great  performance managing web contents.

##Features:

- Access control: Users can be enrolled within follow three roles: admin,editor, viewer.

- Sing-in and Authentication: Users can be authenticates in local database or  an external directory(It supports LDAP, Microsoft Active Directory and Lotus Note Domain). It ca also be deployed with Central Authentication System(CAS).

- Accountability: Login and logout, active sessions, source IP, etc.

- Data Bases: SQLite, PostgreSQL, MySQL, MSSQL, Firebird, Oracle and IBM DB2.

- Multi-language

- Static pages rendering in just one function

- Debugging: Custom error pages

- Search Engine Optimisation: besides Pangolin manages traditional features such as headers, name, title, etc. Sitemap.xml and explicit search engines from Google, Linkedin and Twiter are included


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

### Setup your entire website in just two steps:

1. Move your static pages into private/load_into_ddbb

2. From your favourite browser   http://localhost:8000/pangolin/default/init

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