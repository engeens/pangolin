#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
 Plugin PRETTYHTTP
 version: 2.0
 Copyright (c) 2011 Mulone, Pablo Martin (http://martin.tecnodoc.com.ar/)
 License: MIT
"""

"""
 ABOUT PRETTYHTTP:
"""

from gluon.http import HTTP
from gluon.html import A, URL
from gluon.globals import current
from gluon.template import render


class PRETTYHTTP(BaseException):
    """ PRETTYHTTP """

    def __init__(self, status, full_message=None, link=None, **headers):
        self.request = current.request
        self.T = current.T
        self.status = status
        self.full_message = full_message
        self.link = link
        if self.link is None:
            self.link = A(self.T('Back to the index page'), _href=URL('home', 'index'))

        self.headers = headers


        body = self.render()
        raise HTTP(status, body, **headers)

    def render(self):
        """ Render """
        title = 'Error undefined'
        
        short_message = ''
        if str(self.status)[0] == '1':
            short_message = "That’s not an error."
            if self.status == 100:
                short_message = "Continue"

        elif str(self.status)[0] == '2':
            short_message = "That’s not an error."
            if self.status == 200:
                title = 'OK'
            elif self.status == 201:
                title = 'Created'
            elif self.status == 202:
                title = 'Accepted'

        elif str(self.status)[0] == '3':
            short_message = "That’s not an error."

        elif str(self.status)[0] == '4':
            short_message = "That’s an error."
            if self.status == 400:
                title = 'Bad Request'
            elif self.status == 401:
                title = 'Unauthorized'
            elif self.status == 403:
                title = 'Forbidden'
            elif self.status == 404:
                title = 'Not Found'
            elif self.status == 405:
                title = 'Method Not Allowed'

        elif str(self.status)[0] == '5':
            short_message = "That’s an error."
            if self.status == 500:
                title = 'Internal Server Error'
            elif self.status == 501:
                title = 'Not Implemented'
            elif self.status == 502:
                title = 'Bad Gateway'
            elif self.status == 503:
                title = 'Service Unavailable'
            elif self.status == 504:
                title = 'Gateway Timeout'
            elif self.status == 505:
                title = 'Method Not Allowed'

        # Choose html dode according with the lang
        path = self.request.folder + '/' + 'private/http_status_code'
        status_file = path + '/' + self.T.accepted_language + '/status.html'
        content = str(open(status_file).read())

        return render(content, context=dict(status_code=self.status, title=title, short_message=short_message,
                                            full_message=self.full_message, link=self.link))
