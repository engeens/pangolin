# -*- coding: utf-8 -*-
from helpers.log import logger
from gluon.template import render
from gluon.contrib.appconfig import AppConfig
from gluon.globals import current
from model import BaseModel
from gluon.tools import Mail
from myapp import Base


class Mailer(Mail):
    def __init__(self):
        Mail.__init__(self)
        self.config = AppConfig()
        self.settings.tls = self.config.take('smtp.tls')
        self.settings.server = self.config.take('smtp.server')
        self.settings.sender = self.config.take('smtp.sender')
        if self.config.take('smtp.login'):
            self.settings.login = self.config.take('smtp.login')
        self.request = current.request


class Notifier(BaseModel, Base):

    def __init__(self, db=None, auth=None, render_view=True):
        self.config = AppConfig()
        self.auth = auth
        self.db = db
        self.render_view = render_view
        # In case you dont need any config or current variable
        if self.render_view:
            self._pre_render()

        # In case we do not need to use any database data
        if db:
            self._define_table(tables=['t_lang', 't_email_template'])


    def build_message_from_template(self, event_type, lang=None, render_html=True, **kwargs):
        lang = lang or self.T.accepted_language
        template = self.db((self.db.t_email_template.f_template_key == event_type) &
                           (self.db.t_email_template.f_lang_code == lang)).select().first()

        if not template:
            template = self.db((self.db.t_email_template.f_template_key == event_type) &
                               (self.db.t_email_template.f_lang_code == self.config.take('general.default_language'))).select().first()
            logger.warning("App notification message, you need to define an email template for %s event \n %s" % (event_type, str(kwargs)))

        self.render = lambda text: render(text, context=dict(event_type=event_type, **kwargs))

        try:
            if render_html:
                html_message = self.render(template.f_html_text)
            else:
                html_message = template.f_html_text

        except Exception as e:
            html_message = ''
            logger.warning("Render html_message template %s. Please, edit the email template carefully" % event_type)
            logger.warning(str(e))

        try:
            if render_html:
                subject_text = self.render(template.f_subject_text)
            else:
                subject_text = template.f_subject_text
        except Exception as e:
            subject_text = ''
            logger.warning("Render subject_text template %s. Please, edit the email template carefully" % event_type)
            logger.warning(str(e))

        try:
            if render_html:
                plain_message = self.render(template.f_plain_text)
            else:
                plain_message = template.f_plain_text
        except Exception as e:
            plain_message = ''
            logger.warning("Render plain_message template %s. Please, edit the email template carefully" % event_type)
            logger.warning(str(e))

        return dict(message=[plain_message, html_message],
                    subject=subject_text % kwargs, reply_to=template.f_reply_to or "Undisclosed Recipients",
                    bcc=template.f_copy_to or "", attachments=[template.f_attachment_file] or "")

    def send_email(self, to, event_type, lang=None, render_html=True, bcc=[], **kwargs):
        lang = lang or self.T.accepted_language
        mail = Mailer()
        try:
            message = self.build_message_from_template(event_type, lang, render_html, **kwargs)
            if message['attachments'] != ['']:
                attachment = []
                for i in message['attachments']:
                    attachment.append(mail.Attachment('%suploads/' % self.request.folder + i, filename=self.get_attachment_name(i)))
                message['attachments'] = attachment
            else:
                del message['attachments']

            if 'bcc' in message:
                bcc = message['bcc'].split(',') + bcc
                del message['bcc']

            params = dict(to=to, bcc=bcc, **message)
            sent = mail.send(**params)
        except Exception, e:
            logger.error("Fail sending email to: %s" % to)
            logger.error(str(e))
            sent = False

        return sent

    def get_attachment_name(self, file_name):
        try:
            import re
            items = re.compile('(?P<table>.*?)\.(?P<field>.*?)\..*').match(file_name)
            (t, f) = (items.group('table'), items.group('field'))
            field = self.db[t][f]
            (name, stream) =  field.retrieve(file_name, nameonly=True)
        except Exception, e:
            logger.error(str(e))
            return None
        return name