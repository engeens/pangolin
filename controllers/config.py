# -*- coding: utf-8 -*-

if 'admin' not in auth.user_groups.values():
    if auth.is_logged_in():
        from helpers.prettyexception import PRETTYHTTP
        raise PRETTYHTTP(401, 'Unauthorized')
    else:
        redirect(URL(request.application, 'default', 'user', args=['login'],
                      vars=dict(_next=URL(args=request.args, vars=request.vars))))

from gluon.contrib.appconfig import AppConfig
from config import AppConfigLoader
from myapp import Base


def flush():
    if AppConfig(reload=True):
        response.flash = 'Configuration reloaded'


def manage():
    r = Base()
    r(db=db, auth=auth)
    r.render('/admin/config/manage.html')

    if request.env.request_method == 'GET':
        return dict(settings=AppConfig(reload=True), tab=None)
    elif request.env.request_method == 'POST':
        config = AppConfigLoader()
        if config.set_conf(request.vars):
            response.flash = 'Configuration updated'
            return dict(settings=AppConfig(reload=True), tab=request.vars.section)

        response.flash = 'Uppss error...'
        return dict(settings=AppConfig(reload=True), tab=request.vars.section)


def set():
    r = Base()
    r(db=db, auth=auth)
    r.render('/admin/config/manage.html')
    config = AppConfigLoader()
    if config.set_attribute(request.args(0), request.args(1), request.args(2)):
        AppConfig(reload=True)
        response.flash = 'Configuration updated'