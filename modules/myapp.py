# -*- coding: utf-8 -*-

from gluon.http import HTTP
from gluon.html import CAT, I, SPAN, URL, LI, UL, A
from helpers.log import logger
from gluon.globals import current
from gluon.contrib.appconfig import AppConfig
from helpers.prettyexception import PRETTYHTTP


def str2bool(v):
    return v.lower() in ("yes", "true", "1")


def access(db, auth):
        config = AppConfig()
        # Not allow
        auth.settings.create_user_groups = False
        auth.settings.actions_disabled.append('register')
        auth.settings.actions_disabled.append('request_reset_password')
        auth.settings.actions_disabled.append('retrieve_password')
        auth.settings.actions_disabled.append('profile')
        auth.settings.registration_requires_approval = False
        auth.settings.registration_requires_verification = False

        #Set general settings
        auth.settings.expiration = int(config.take('general.session_expiration'))
        auth.settings.remember_me_form = config.take('general.remember_me_form')

        if config.take('general.auth_type') == 'cas':

            from gluon.contrib.login_methods.cas_auth import CasAuth
            auth.settings.login_form = CasAuth(urlbase=config.take('auth_cas.urlbase'),
                                                    actions=[config.take('auth_cas.cas_actions_login'),
                                                             config.take('auth_cas.cas_actions_validate'),
                                                             config.take('auth_cas.cas_actions_logout')],
                                                    casversion=config.take('auth_cas.version'))

            if auth.settings.login_form.get_user() is not None:
                __check_cas_onvalidation(auth.settings.login_form.get_user(), db)

        elif config.take('general.auth_type') == 'ldap':
                auth.settings.login_onvalidation = [lambda form: __define_domain(form.vars.email.split('@')[1], config)]

        elif config.take('general.auth_type') == 'local':
                if str2bool(config.take('auth_local.enable_change_password')) is not True:
                    auth.settings.actions_disabled.append('change_password')


def __define_domain(domain, config):
    domain = domain.lower()
    try:
        count = 1
        while True:
            ldap_connection = 'auth_ldap_0' + str(count)
            if config.__getattribute__(ldap_connection).is_active:
                if config.__getattribute__(ldap_connection).domain == domain:
                    __load_ldap_connection(ldap_connection, config)
                    break

            count += 1

    except Exception as e:
        logger.warning("Not possible to connect to LDAP.")
        raise PRETTYHTTP(400, 'Upppss, the domain you have type, I could not find it...')


def __load_ldap_connection(ldap, db, auth, config):
    try:
        if config.__getattribute__(ldap).is_active:
            from gluon.contrib.login_methods.ldap_auth import ldap_auth
            if config.auth.auth_local_database:
                auth.settings.login_methods.append(ldap_auth(
                    mode=config.__getattribute__(ldap).mode,
                    secure=config.__getattribute__(ldap).secure,
                    server=config.__getattribute__(ldap).server,
                    port=config.__getattribute__(ldap).port,
                    base_dn=config.__getattribute__(ldap).base_dn,
                    allowed_groups=config.__getattribute__(ldap).allowed_groups,
                    group_dn=config.__getattribute__(ldap).group_dn,
                    group_name_attrib=config.__getattribute__(ldap).group_name_attrib,
                    group_member_attrib=config.__getattribute__(ldap).group_member_attrib,
                    group_filterstr=config.__getattribute__(ldap).group_filterstr,
                    manage_user=True,
                    user_firstname_attrib='cn:1',
                    user_lastname_attrib='cn:2',
                    user_mail_attrib='mail',
                    db=db,

                ))

            else:
                auth.settings.login_methods = [(ldap_auth(
                    mode=config.__getattribute__(ldap).mode,
                    secure=config.__getattribute__(ldap).secure,
                    server=config.__getattribute__(ldap).server,
                    port=config.__getattribute__(ldap).port,
                    base_dn=config.__getattribute__(ldap).base_dn,
                    allowed_groups=config.__getattribute__(ldap).allowed_groups,
                    group_dn=config.__getattribute__(ldap).group_dn,
                    group_name_attrib=config.__getattribute__(ldap).group_name_attrib,
                    group_member_attrib=config.__getattribute__(ldap).group_member_attrib,
                    group_filterstr=config.__getattribute__(ldap).group_filterstr,
                    manage_user=True,
                    user_firstname_attrib='cn:1',
                    user_lastname_attrib='cn:2',
                    user_mail_attrib='mail',
                    db=db

                ))]
    except Exception as e:
        logger.warning("Not possible to connect to LDAP.")
        raise PRETTYHTTP(500, e)


def __check_cas_onvalidation(user, db):
    session = current.session
    try:
        row = db(db.auth_user.email == user['email']).select(db.auth_user.registration_key).first()
        #This mean is not the first login.
        if row is not None:
            if row.registration_key == "pending":
                session.forget()
                raise HTTP(200, "Your account is in pending status. Please contact to Operations.")

            elif row.registration_key == "disabled":
                session.forget()
                raise HTTP(200, "Your account is disable. Please contact to Operations.")
    except:
        session.forget()
        raise HTTP(500, "Oppssss....")


class Base(object):
    def __call__(self, **kwargs):
        self.db=kwargs['db']
        self.auth=kwargs['auth']
        self._pre_render()

    def _pre_render(self):
        config = AppConfig()
        self.config = config
        self.T = current.T
        self.session = current.session
        self.request = current.request
        self.response = current.response
        self.render_view = True

    def render(self, view):
        if self.render_view == False:
            self._pre_render()

        # When comming soon is enable for the global env.
        if str2bool(self.config.take('status.enable_comming_soon')) == True and not self.auth.user \
                and not self.request.controller == 'admin' and not self.request.controller == 'appadmin' \
                and not self.request.function == 'user' and not self.request.args(0) == 'comming-soon':
            from gluon.http import redirect
            redirect(URL(self.request.application, 'home', 'show', args=['comming-soon']))

        # When under-maintenance is enable for the global env.
        if str2bool(self.config.take('status.enable_under_maintenance')) == True and not self.auth.user \
                and not self.request.controller == 'admin' and not self.request.controller == 'appadmin' \
                and not self.request.function == 'user' and not self.request.args(0) == 'under-maintenance':
            from gluon.http import redirect
            redirect(URL(self.request.application, 'home', 'show', args=['under-maintenance']))

        self.response.view = '%s/%s' % (self.config.take('general.default_theme'), view)
        # Social networks
        self.response.facebook = self.config.take('social_networks.facebook')
        self.response.twitter = self.config.take('social_networks.twitter')
        self.response.linkedin = self.config.take('social_networks.linkedin')
        self.response.github = self.config.take('social_networks.github')
        self.load_menus()

    def load_menus(self):
        self.response.menu = [
            (CAT(I(_class='fa fa-dashboard fa-fw'), self.T(' Home ')), False, URL('admin', 'index')),
            (CAT(I(_class='fa fa-edit fa-fw'), self.T(' Manage '), SPAN(_class='fa arrow')), False, '#', [
                (CAT(I(_class='fa fa-user fa-fw'), self.T(' Users ')), False, URL('users', 'manage')),
                (CAT(I(_class='fa fa-th-list fa-fw'), self.T(' Pages ')), False, URL('page', 'manage')),
                (CAT(I(_class='fa fa-th-list fa-fw'), self.T(' Email ')), False, URL('template', 'manage'))
            ]),
            (CAT(I(_class='fa fa-wrench fa-fw'), self.T(' Settings ')), False, URL('config', 'manage')),
            (CAT(I(_class='fa fa-history fa-fw'), self.T(' History '), SPAN(_class='fa arrow')), False, '#', [
                (CAT(I(_class='fa fa-user fa-fw'), self.T(' User logs ')), False, URL('admin', 'history')),
                (CAT(I(_class='fa fa-th-list fa-fw'), self.T(' User sessions ')), False, URL('admin', 'sessions')),
            ]),

            (CAT(I(_class='fa fa-home fa-fw'), self.T(' APP HOME ')), False, URL('default', 'index')),
        ]


        if  self.auth.is_logged_in():
            def custom_navbar(auth_navbar):
                bar = auth_navbar
                user = bar["user"]
                toggletext = "%s %s" % (bar["prefix"], user)

                li_password = LI(A(I(_class="icon icon-lock glyphicon glyphicon-lock"), ' ',
                                  "Change password",
                                  _href=bar["change_password"], _rel="nofollow"))

                li_logout = LI(A(I(_class="icon icon-off glyphicon glyphicon-off"), ' ',
                                 "logout",
                                 _href=bar["logout"], _rel="nofollow"))

                toggle = A(I(_class="fa fa-user fa-fw"),I(_class="fa fa-caret-down"),
                           _href="#",
                           _class="dropdown-toggle",
                           _rel="nofollow",
                           **{"_data-toggle": "dropdown"})


                dropdown = UL(toggletext,
                              LI('', _class="divider"),
                              li_password,
                              LI('', _class="divider"),
                              li_logout,
                              _class="dropdown-menu", _role="menu")

                return LI(toggle, dropdown, _class="dropdown")

            self.response.navbar = custom_navbar(self.auth.navbar('Welcome',mode='bare'))