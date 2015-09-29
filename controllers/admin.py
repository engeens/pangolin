# Users is defined globaly
#from users import Users

# -*- coding: utf-8 -*-

if ('admin' or 'editor' or 'viewer') not in auth.user_groups.values():
    if auth.is_logged_in():
        from helpers.prettyexception import PRETTYHTTP
        raise PRETTYHTTP(401, 'Unauthorized')
    else:
        redirect(URL(request.application, 'default', 'user', args=['login'],
                      vars=dict(_next=URL(args=request.args, vars=request.vars))))


def index():
    person.render('/admin/home/index.html')
    return dict(morris_area_chart = person.history('chart', 'auth'), list_history = person.history('list', 'auth', session.user_timezone))


def status():
    return person.to_know(request.args(0))


def history():

    return dict(sqlform = person.history('full-list', 'auth', session.user_timezone))


def sessions():
    from users import SessionSetDb
    person.render('/admin/home/sessions.html')
    set_db = SessionSetDb('web2py_session_' + request.application, db)
    return dict(sessions=set_db.sessions())


def version():
    from _version import get_versions
    version = get_versions()
    if version['error']:
        raise RuntimeError(version['error'])
    return version['version'].split('+')[0]