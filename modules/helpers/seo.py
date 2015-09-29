#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
 Plugin seo
 Copyright (c) cccaballero
 Based on https://github.com/daxslab/web2py-simple-seo/blob/master/modules/plugin_simple_seo/seo.py
"""

from gluon.contrib.appconfig import AppConfig
from helpers.log import logger
from gluon.html import URL, XML
from gluon.globals import current
from gluon.contrib.ordereddict import OrderedDict

'''
From a controller do:

    def test():
        from helpers.seo import SEO
        from gluon.storage import Storage
        page = Storage()
        page.description = "hola mundo"
        page.author = 'jose'
        seo = SEO(page, locale=T.accepted_language, type="website", render=False)
        seo.set()
        response.view = '%s/public/test.html' % CONFIG_THEME
        return dict()
'''


class SEO(object):

    def __init__(self, row, locale=None, type="website", url=None):
        """
        :param row: Storage object
        :param locale:
        :param type:
        :param url:
        """
        self.config = AppConfig()
        self.title = self.config.take('metadata.site_name')
        self.url = url or URL(args=current.request.args, host=True)
        self.type = type
        self.locale= locale
        self.row = row
        self.response = current.response

    def set(self):
        self._set_meta()
        self._set_open_graph()
        self._set_twitter_card()

    def _set_meta(self):
        description = self.config.take('metadata.description')
        keywords = self.config.take('metadata.keywords')
        author = self.config.take('metadata.author')
        data = locals()
        for name in ['title', 'description', 'keywords', 'author']:
            if name == 'title':
                self.response.meta[name] = self.title
            elif data[name]:
                self.response.meta[name] = data[name]


    def _set_open_graph(self):
            for name in ['type', 'title', 'url', 'description', 'site_name', 'locale', 'locale_alternate', 'image']:
                dict = OrderedDict()
                if name == 'type':
                    content = self.type
                elif name == 'site_name':
                    content = self.title
                elif name == 'url':
                    content = self.url
                elif name == 'locale':
                    content = self.locale
                elif name == 'locale_alternate':
                    content = self.config.take('general.locale_alternate')
                else:
                    try:
                        content = self.row['f_'+name]
                    except AttributeError as e:
                        logger.warning("%s attribute have been not set" % name)
                        content = None
                if content:
                    dict['name'] = "og:"+name
                    dict['content'] = content
                    self.response.meta['og_'+name] = dict



    def _set_twitter_card(self):
        '''
        <meta name="twitter:title" content="Linux-Cambodia" />
        <meta name="twitter:description" content="Linux-Cambodia is a non-profit project committed with the current and emergent technology trends in Cambodia, with the Internet, with education...Behind the headings, the products and the services offered by Linux Cambodia there is a team of professionals with sound experience on information technologies, online marketing, events management, video producing, social media, training, web developing... The initiative is rooted in the idea that every person has the right to access information and knowledge. In this sense and due to the lack of these contents in the Cambodian market, this project is launched with the hope of reaching all audiences who are passionate about open source." />
        <meta name="twitter:image" content="http://www.linux-cambodia.com/default/download/new.picture.98d62da3eccd8100.77656c636f6d652e6a7067_thumb.jpg" />
        '''
        for name in ['image', 'title', 'description']:
            dict = OrderedDict()
            if name == 'title':
                content = self.title
            else:
                try:
                    content = self.row['f_'+name]
                except AttributeError as e:
                    logger.warning("%s attribute have been not set" % name)
                    content = None
            if content:
                dict['property'] = "twitter:"+name
                dict['content'] = content
                self.response.meta['tc_'+name] = dict



def sitemap(db, request):
        # Adding Schemas for the site map
        xmlns = 'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
        xmlnsImg = 'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"\n'
        xmlnsVid = 'xmlns:video="http://www.google.com/schemas/sitemap-video/1.1"\n'
        sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
        sitemap_xml += '<urlset %s %s %s>\n' % (xmlns, xmlnsImg, xmlnsVid)


        # Define Your Domain
        domain = 'http://' + current.request.env.http_host.split(':')[0]
        from model import BaseModel
        model = BaseModel()
        model(db=db, request=request, tables=['t_page'])
        pages = db(db.t_page.f_is_active == True).select(db.t_page.ALL)
        for page in pages:
            sitemap_xml += '<url>\n<loc>%s/%s/page/show/%s</loc>\n</url>\n' % (domain, page.f_lang_code, page.f_slug_key)
        sitemap_xml += '</urlset>'

        return sitemap_xml