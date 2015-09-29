# -*- coding: utf-8 -*-
from model import BaseModel
from gluon.sqlhtml import SQLFORM
from helpers.log import logger
from gluon.html import A, URL
from myapp import Base


class EmailTemplate(BaseModel, Base):
    def __init__(self, db=None, auth=None, render_view=True):
        self.auth = auth
        self.db = db
        self.render_view = render_view
        # In case you dont need any config or current variable
        if self.render_view:
            self._pre_render()

        # In case we do not need to use any database data
        if db:
            self._define_table(tables=['t_email_template'])


    def grid(self):
        links = [
            lambda row: A('Preview', _target='_blank',  _class="btn-success btn-mini", _href=URL('template', 'show', args=[str(row.id)]))]

        fields = [self.db.t_email_template.f_template_key, self.db.t_email_template.f_lang_code, self.db.t_email_template.f_attachment_file]
        grid = SQLFORM.grid(self.db.t_email_template,
                            ui='web2py',
                            #linked_tables=linked_tables,
                            fields=fields,
                            #orderby=fields[-2],
                            links=links,
                            csv=False,
                            searchable=False,
                            create=True,
                            details=True,
                            editable=True,
                            deletable=True,
                            #onvalidation=get_unique,
                            #oncreate=get_unique,
                            )

        return grid

    def show(self, template_id):
        try:
            template = self.db(self.db.t_email_template.id == template_id).select(self.db.t_email_template.f_html_text).first()

        except Exception as e:
            logger.warning("Not possible to get page.")
            logger.warning(str(e))
            return None

        if not template:
            return None
        return template.f_html_text.replace("{=", '')