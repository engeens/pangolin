# -*- coding: utf-8 -*-

from gluon import SQLFORM, SPAN, DIV, A, URL, UL
from helpers.log import logger
from gluon.dal import Field
from gluon.validators import IS_IN_DB
from model import BaseModel
from myapp import str2bool
from myapp import Base


class Users(BaseModel, Base):

    def __init__(self, db=None, auth=None, render_view=True):
        self.auth = auth
        self.db = db
        self.render_view = render_view
        # In case you dont need any config or current variable
        if self.render_view:
            self._pre_render()
        # In case we do not need to use any database data
        if self.db:
            self._define_tables()

    def _define_tables(self):
        self._define_table(tables=['t_lang'])

        # create all tables needed by auth if not custom tables
        self.auth.settings.extra_fields['auth_user']= [
            Field('f_lang_id', 'reference t_lang', requires=IS_IN_DB(self.db, self.db.t_lang.id, '%(f_name)s')),]

        # With this option we force in forms to validate as IS_LOWER()
        self.auth.settings.email_case_sensitive = False
        self.auth.define_tables(username=False, signature=False)

    def grid(self):
        fields = dict(auth_user=[self.db.auth_user.first_name, self.db.auth_user.email,
                                 self.db.auth_user.registration_key])

        self.db.auth_user.registration_key.readable = True
        if str2bool(self.config.take('auth_local.admin_registration_requires_verification')):
            self.db.auth_user.password.readable = False
            self.db.auth_user.password.writable = False
        else:
            self.db.auth_user.password.readable = True
            self.db.auth_user.password.writable = True

        fields["auth_user"][2].represent = lambda value, row: SPAN('active', _class='label label-success') \
            if value == "" else SPAN(value, _class='label label-info')

        links = dict(auth_user=[
            lambda row: A('Enable',  _class="btn-success btn-mini", callback=URL('users', 'action', args=[str(row.id), 'enable']))
            if row.registration_key == 'blocked' or row.registration_key == 'disabled' else "",
            lambda row: A('Block', _class="btn-danger btn-mini", callback=URL('users', 'action', args=[str(row.id), 'block']))
            if row.registration_key == '' else "",
            lambda row: A('Approve', _class="btn btn-info btn-mini", callback=URL('users', 'action', args=[str(row.id), 'enable']))
            if row.registration_key == 'pending' else "",])

        def verify_email(form):
            from gluon.utils import web2py_uuid

            if str2bool(self.config.take('auth_local.admin_registration_requires_verification')):
                d = dict(form.vars)
                key = web2py_uuid()
                link = URL('default', 'users', args=('verify_email', key), scheme=True)
                d = dict(form.vars)
                plain_password = web2py_uuid().split('-')[0]
                md5_password = self.db.auth_user.password.validate(plain_password)[0]
                d.update(dict(registration_key=key, password=md5_password))
                self.db(self.db['auth_user']._id==form.vars.id).update(**d)

                from myapp import Mailer
                notification = Mailer()
                if notification.send_email(form.vars.email, 'VERIFY YOUR EMAIL', 'verify_email', link=link, password=plain_password):
                    self.session.flash = "Email sent to the user for verification"
                else:
                    self.session.flash = "Email unsent, uppss there is a error"

        linked_tables = [self.db.auth_membership]
        if self.config.take('general.auth_type') == 'local':
            grid = SQLFORM.smartgrid(self.db.auth_user,
                                     ui='web2py',
                                     fields=fields,
                                     links=links,
                                     linked_tables=linked_tables,
                                     #orderby=fields[-2],
                                     csv=False,
                                     searchable=True,
                                     create=True,
                                     details=True,
                                     editable=True,
                                     deletable=True,
                                     oncreate=verify_email,)
        else:
            grid = SQLFORM.smartgrid(self.db.auth_user,
                                     ui='web2py',
                                     linked_tables=linked_tables,
                                     fields=fields,
                                     #orderby=fields[-2],
                                     links=links,
                                     csv=False,
                                     searchable=True,
                                     create=False,
                                     details=True,
                                     editable=False,
                                     deletable=True)

        return grid

    def action(self, user_id, action):
        try:
            query = self.db(self.db.auth_user.id == user_id).select().first()
            if action == 'block':
                query.update_record(registration_key="blocked")
            elif action == 'enable':
                query.update_record(registration_key='')

            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(str(e))
            return False
        return True

    def to_know(self, status):
        if status == 'active':
            return self.db(self.db.auth_user.registration_key == "").count()
        elif status == 'disabled' or status == 'blocked':
            return self.db(self.db.auth_user.registration_key == status).count()
        elif status == 'pending':
            return self.db((self.db.auth_user.registration_key == status) |
                           (self.db.auth_user.registration_key != 'disabled') &
                            (self.db.auth_user.registration_key != 'blocked') &
                             (self.db.auth_user.registration_key != '')).count()
        elif status == 'sessions':
            set_files = SessionSetFiles()
            set_db = SessionSetDb('web2py_session_' + self.request.application, self.db)
            return set_files.count() + set_db.count()

    def remove_session(self, id):
        self.db(self.db.web2py_session_cas.id == id).delete()

    def history(self, option, origin, user_timezone=None):
        if option == 'chart':
            from datetime import date, timedelta
            time = date.today() - timedelta(days=30)
            rows = self.db(self.db.auth_event.origin == origin and self.db.auth_event.time_stamp > str(time)).select(self.db.auth_event.ALL)
            result = []
            time_to_search = rows[0].time_stamp.strftime("%Y-%m-%d")
            count_login = 0
            count_logout = 0
            for r in rows:
                if r.time_stamp.strftime("%Y-%m-%d") == time_to_search:
                    if 'Logged-in' in r.description: count_login += 1
                    elif 'Logged-out' in r.description: count_logout += 1
                else:
                    result.append({'period': time_to_search, 'login': count_login, 'logout': count_logout})
                    count_login = 0
                    count_logout = 0
                    if 'Logged-in' in r.description: count_login = 1
                    elif 'Logged-out' in r.description: count_logout = 1

                time_to_search = r.time_stamp.strftime("%Y-%m-%d")
            result.append({'period': time_to_search, 'login': count_login, 'logout': count_logout})
            return result

        elif option == 'list':

            rows = self.db(self.db.auth_event.origin == origin).select(self.db.auth_event.ALL, limitby=(0,7),
                                                                     orderby=~self.db.auth_event.time_stamp)

            # In case the server does not have UTC time, we should convert time server to UTC
            import pytz
            from tzlocal import get_localzone
            from datetime import datetime
            for r in rows:
                if 'Logged-in' in r.description: r.description = 'logged in'
                elif 'Logged-out' in r.description: r.description = 'logged out'
                # Covert to the local server and to date object
                r.time_stamp = datetime.strptime(pytz.UTC.localize(r.time_stamp).
                                                 astimezone(pytz.timezone(str(get_localzone()))).
                                                 strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
            return rows

        elif option == 'full-list':
            import pytz
            self.db.auth_event.time_stamp.represent = lambda value, row :pytz.UTC.localize(value).astimezone(pytz.timezone(user_timezone))
            sqlform = SQLFORM.grid(self.db.auth_event,
                                   csv=False,
                                   orderby=~self.db.auth_event.time_stamp,
                                   editable=False,
                                   deletable=False,
                                   create=False)
            return sqlform


import datetime
import os
from gluon import current
import cPickle
from gluon.storage import Storage
import stat


def total_seconds(delta):
    """
    Adapted from Python 2.7's timedelta.total_seconds() method.

    Args:
        delta: datetime.timedelta instance.
    """
    return (delta.microseconds + (delta.seconds + (delta.days * 24 * 3600)) * 10 ** 6) / 10 ** 6


class Session(object):
        def __init__(self, expiration=0):
            self.expiration = expiration

        def count(self):
            return len(self.sessions())

        def sessions(self):
            """
            :return: list with session object
            """
            # Time fom the server utc time
            now = current.request.now
            sessions=[]
            for item in self.get():
                last_visit = item.last_visit_default()

                try:
                    session = item.get()
                    if session.auth:
                        if session.auth.expiration:
                            self.expiration = session.auth.expiration
                        if session.auth.last_visit:
                            last_visit = session.auth.last_visit
                except:
                    pass

                age = 0
                if last_visit:
                    age = total_seconds(now - last_visit)


                if age < self.expiration:
                    sessions.append(item)

            return sessions



class SessionSetDb(Session):
    """Class representing a set of sessions stored in database"""

    def __init__(self, session_db_table, db):
        Session.__init__(self)
        self.session_db_table = session_db_table
        self.db = db

    def get(self):
        """Return list of SessionDb instances for existing sessions."""
        sessions = []
        table = self.session_db_table
        if table:
            for row in self.db(self.db.__getattribute__(table).id > 0).select():
                sessions.append(SessionDb(row))
        return sessions


class SessionSetFiles(Session):
    """Class representing a set of sessions stored in flat files"""

    def __init__(self):
        Session.__init__(self)

    def get(self):
        """Return list of SessionFile instances for existing sessions."""
        root_path = os.path.join(current.request.folder, 'sessions')
        for path, dirs, files in os.walk(root_path, topdown=False):
            for x in files:
                yield SessionFile(os.path.join(path, x))


class SessionFile(object):
    """Class representing a single session stored as a flat file"""

    def __init__(self, filename):
        self.filename = filename

    def delete(self):
        try:
            os.unlink(self.filename)
        except:
            pass

    def get(self):
        session = Storage()
        with open(self.filename, 'rb+') as f:
            session.update(cPickle.load(f))
        return session

    def last_visit_default(self):
        return datetime.datetime.fromtimestamp(
            os.stat(self.filename)[stat.ST_MTIME])

    def __str__(self):
        return self.filename


class SessionDb(object):
    """Class representing a single session stored in database"""

    def __init__(self, row):
        self.row = row

    def delete(self):
        table = current.response.session_db_table
        self.row.delete_record()
        table._db.commit()

    def get(self):
        session = Storage()
        session.update(cPickle.loads(self.row.session_data))
        return session

    def last_visit_default(self):
        if isinstance(self.row.modified_datetime, datetime.datetime):
            return self.row.modified_datetime
        else:
            try:
                return datetime.datetime.strptime(self.row.modified_datetime, '%Y-%m-%d %H:%M:%S.%f')
            except:
                raise 'failed to retrieve last modified time (value: %s)' % self.row.modified_datetime

    def __str__(self):
        return self.row.unique_key