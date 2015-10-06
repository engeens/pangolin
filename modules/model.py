# -*- coding: utf-8 -*-

from gluon.validators import IS_IN_DB, IS_SLUG, IS_IN_SET, IS_NOT_IN_DB, IS_NOT_EMPTY, IS_INT_IN_RANGE
from gluon.dal import Field
from functools import wraps


class BaseModel(object):

    def __call__(self, db=None, auth=None, request=None, tables=['all']):
        self.db = db
        self.auth = auth
        self.request = request
        self._define_table(tables)



    def _define_table(self, tables):
        if tables[0] == 'all':
            tables = []
            for item in dir(self):
                if item.startswith('_t_'):
                    tables.append(item[1:])
        for table in tables:
            if table not in self.db.tables:
                run = getattr(self, '_'+table)
                run()

    def _depends_on(*args):
        def _define(f):
            def _decorator(self):
                for table in args:
                    if table not in self.db.tables:
                        run = getattr(self, '_'+table)
                        run()
                f(self)
            return wraps(f)(_decorator)
        return _define


    def _t_lang(self):
        self.db.define_table('t_lang',
            Field('f_name', 'string'),
            Field('f_lang_code', length=255, unique=True)
            )

    @_depends_on('t_lang')
    def _t_email_template(self):
        self.db.define_table('t_email_template',
            Field("f_subject_text", "string"),
            Field('f_key_template', length=255, unique=True, compute=lambda r: '%s-%s' % (r.f_template_key, r.f_lang_id)),
            Field("f_template_key", "string", notnull=True),
            Field('f_lang_id', 'reference t_lang', requires=IS_IN_DB(self.db, self.db.t_lang.id, '%(f_name)s')),
            Field('f_lang_code', writable=False,
                  compute=lambda r: '%s' % (self.db(self.db.t_lang.id == r.f_lang_id).select(
                      self.db.t_lang.f_lang_code).first().f_lang_code)),
            Field("f_plain_text", "text", notnull=True, default=""),
            Field("f_html_text", "text", notnull=True, default=""),
            Field("f_copy_to", "string"),
            Field("f_reply_to", "string"),
            Field("f_attachment_file", "upload", autodelete=True),
            Field('f_created_on', 'datetime', default=self.request.now, writable=False),
            Field('f_updated_on', 'datetime', update=self.request.now, writable=False),
        )

    @_depends_on('t_lang')
    def _t_page(self):
        self.db.define_table('t_page',
            Field('f_key_page', unique=True, length=255, compute=lambda r: '%s-%s' % (r.f_slug_key, r.f_lang_id)),
            Field('f_title', "string", notnull=True),
            Field('f_lang_id', 'reference t_lang', requires=IS_IN_DB(self.db, self.db.t_lang.id, '%(f_name)s')),
            Field('f_description', "text"),
            Field('f_lang_code', writable=False,
                  compute=lambda r: '%s' % (self.db(self.db.t_lang.id == r.f_lang_id).select(
                      self.db.t_lang.f_lang_code).first().f_lang_code)),
            Field("f_html_text", 'text', notnull=True),
            Field("f_slug_key", writable=False),
            Field("f_tags", 'list:string'),
            Field("f_is_active", "boolean", default=False),
            Field('f_created_on', 'datetime', default=self.request.now, writable=False),
            Field('f_updated_on', 'datetime', update=self.request.now, writable=False)
            )


