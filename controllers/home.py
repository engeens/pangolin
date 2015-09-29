# -*- coding: utf-8 -*-
from pages import StaticPage
from helpers.prettyexception import PRETTYHTTP
from gluon.template import render

####################### SHOW THE STATIC WEB PAGES ########################
def show():
    page = StaticPage(db, auth)
    page.render(None)
    html_page = page.show(slug_key=request.args(0))
    if html_page is None:
        raise PRETTYHTTP(403, T("Page not found"))
    import os
    new_render = lambda text: render(text, path=os.path.join(request.folder, 'views'), context=dict(**globals()))
    return new_render(html_page)
####################### SHOW THE STATIC WEB PAGES ########################


def set_timezone():
    """Ajax call to set the timezone information for the session."""
    tz_name = request.vars.name
    from pytz import all_timezones_set
    if tz_name in all_timezones_set:
        session.user_timezone = tz_name


def sitemap():
    from helpers.seo import sitemap
    return sitemap(db, request)

def contact():
    name = request.vars.name
    email = request.vars.mail
    phone = request.vars.phpne
    message= request.vars.message
    from notification import Notifier
    notifier = Notifier(db)
    if notifier.send_email(email, "contact_user", email=email, name=name, phone=phone, message=message):
        return 'Thanks, we have sent you a email...'
    return 'Uppps there is an error... Please verify you have the SMTP server configured.'