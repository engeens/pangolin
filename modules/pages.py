# -*- coding: utf-8 -*-
from model import BaseModel
from myapp import Base
from gluon.validators import IS_SLUG
from gluon.sqlhtml import SQLFORM
from helpers.log import logger
from gluon.html import A, URL, XML
from helpers.seo import SEO


class StaticPage(BaseModel, Base):

    def __init__(self, db=None, auth=None, render_view=True):
        self.auth = auth
        self.db = db
        self.render_view = render_view
        # In case you dont need any config or current variable
        if self.render_view:
            self._pre_render()

        # In case we do not need to use any database data
        if db:
            self._define_table(tables=['t_page'])



    def show(self, slug_key=None, page_id=None):
        try:
            if page_id:
                page = self.db((self.db.t_page.id == page_id)).select().first()
            else:
                page = self.db((self.db.t_page.f_is_active == True) & (self.db.t_page.f_slug_key == slug_key)
                               & (self.db.t_page.f_lang_code == self.T.accepted_language)).select().first()

            if not page:
                page = self.db((self.db.t_page.f_is_active == True) & (self.db.t_page.f_slug_key == slug_key) &
                               (self.db.t_page.f_lang_code == self.config.take('general.default_language'))).select().first()
                logger.warning("You need to define a static %s page for %s " % (self.T.accepted_language, slug_key))

        except Exception as e:
            logger.warning("Not possible to get page.")
            logger.warning(str(e))
            return None

        if not page:
            return None

        # Set some seo parameters based in the info we have already in the database
        seo = SEO(page, locale=self.T.accepted_language, type="website")
        seo.set()
        return page.f_html_text


    def grid(self):
        def get_unique(form):
            slug = IS_SLUG()(form.vars.f_title)[0]
            form.vars.f_slug_key = slug

        fields = [self.db.t_page.f_title, self.db.t_page.f_lang_code, self.db.t_page.f_tags, self.db.t_page.f_is_active]

        links = [
            lambda row: A('Preview', _target='_blank',  _class="btn-success btn-mini", _href=URL('page', 'show', args=[str(row.id)]))]

        grid = SQLFORM.grid(self.db.t_page,
                            ui='web2py',
                            fields=fields,
                            #orderby=fields[-2],
                            links=links,
                            csv=False,
                            searchable=True,
                            create=True,
                            details=True,
                            editable=True,
                            deletable=True,
                            onvalidation=get_unique,
                            #oncreate=get_unique,
                            )

        return grid

