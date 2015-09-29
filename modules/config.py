# -*- coding: utf-8 -*-

from helpers.log import logger
from gluon import current
from gluon.html import XML


class InitApp(object):
    def __init__(self, db, init_app, auth=None):
        self.db = db
        self.init_app = init_app
        self.auth = auth
        self.request = current.request

        ## Set some configurations
        self.roles = 'admin, editor, viewer'
        self.admin_email = 'admin@test.com'
        self.admin_pass = 'temporal'

    def set(self):
        """
        Returns: state, traceback
            state : True on success, False on error.
            traceback: message on success, raised exception details on failure.

        Return type: tuple
        """
        if self.init_app:
            check_if_empty = self.db(self.db.auth_user.id > 0).select()
            if not check_if_empty:
                # we define all the tables in the APP
                from model import BaseModel
                model = BaseModel()
                model(db=self.db, auth=self.auth, request=self.request, tables=['all'])

                try:
                    # Set langs for the CMS
                    self.db.t_lang.insert(f_name='Spanish', f_lang_code='es')
                    self.db.t_lang.insert(f_name='English', f_lang_code='en')

                    logger.info('langs...')
                    self.db.auth_group.insert(role='admin', description="View, edit and delete an application via the Administration Console, invite users, and change user roles.")
                    for role in self.roles.split(','):
                        self.db.auth_group.insert(role=role)

                    logger.info('groups...')
                    password_md5 = self.db.auth_user.password.validate(self.admin_pass)[0]
                    user_name = self.admin_email
                    try:
                        user_admin = self.db.auth_user.insert(first_name="Admin User", username=user_name, password=password_md5)
                    except:
                        user_admin = self.db.auth_user.insert(first_name="Admin User", email=user_name, password=password_md5)


                    logger.info('admin user...')

                    self.auth.add_membership('admin', user_admin)
                    # To add auth_event table. It is not created until you login or register.

                    self._load_html_pages()
                    logger.info('html pages...')

                    self.db.commit()
                    return True, "The app have been initialize, please set init_app to False in the configuration file. \
                                Login with user %s and password %s" % (user_name, self.admin_pass)
                except Exception as e:
                    return False, e
            else:
                return False, "Drop database before initialize"
        else:
                return False, "disabled"

    def _load_html_pages(self):
        import os
        for folder in os.listdir(self.request.folder + '/' + 'private/load_into_ddbb/'):
            for lang in os.listdir(self.request.folder + '/' + 'private/load_into_ddbb/' + folder):
                lang_id = self.db(self.db.t_lang.f_lang_code == lang).select().first().id
                for filename in os.listdir(self.request.folder + '/' + 'private/load_into_ddbb/' + folder + '/' + lang):
                    path = self.request.folder + '/' + 'private/load_into_ddbb/' + folder + '/' + lang + '/' + filename

                    if folder == "email_templates":
                        template_key = filename.split('.')[0]
                        if template_key == "verify_email" or template_key == 'reset_password':
                            self.db.t_email_template.insert(f_template_key=template_key, f_html_text=XML(str(open(path).read())),
                                                          f_plain_text="Auto created by the app", f_lang_id=lang_id,
                                                          f_subject_text="Auto Generado, look web2py translate file.")
                        else:
                            self.db.t_email_template.insert(f_template_key=template_key, f_html_text=XML(str(open(path).read())),
                                                          f_plain_text="Auto created by the app", f_lang_id=lang_id)
                    if folder == "static_pages":
                        self.db.t_page.insert(f_title=filename.split('.')[0], f_slug_key=filename.split('.')[0],
                                              f_html_text=XML(str(open(path).read())), f_is_active=True,
                                              f_lang_id=lang_id)

from gluon.contrib.appconfig import AppConfigLoader

class AppConfigLoader(AppConfigLoader):

    def set_attribute(self, section, attribute, new_value):
        """
        :param section:
        :param atttrbute:
        :param new_value:
        :return: True or False
        """
        import ConfigParser
        config = ConfigParser.RawConfigParser()
        config.read(self.file)
        config.set(section, attribute, new_value)

        try:
            with open(self.file, 'wb') as configfile:
                config.write(configfile)
        except:
            return False
        return True


    def set_conf(self, vars):
        """Receive the request vars, the section name form define the section in the conf.ini
        :param vars: The request variables
        :return: True or False
        """

        for i in vars:
            print i

        import ConfigParser
        config = ConfigParser.RawConfigParser()
        config.read(self.file)
        for var in vars:
            if var != 'section':
                config.set(vars.section, var, vars[var])

        try:
            with open(self.file, 'wb') as configfile:
                config.write(configfile)
        except:
            return False
        return True