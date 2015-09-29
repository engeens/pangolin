# -*- coding: utf-8 -*-

if ('admin' or 'editor') not in auth.user_groups.values():
    if auth.is_logged_in():
        from helpers.prettyexception import PRETTYHTTP
        raise PRETTYHTTP(401, 'Unauthorized')
    else:
        redirect(URL(request.application, 'default', 'user', args=['login'],
                      vars=dict(_next=URL(args=request.args, vars=request.vars))))

from pages import StaticPage
from helpers.prettyexception import PRETTYHTTP
from gluon.template import render


def manage():
    page = StaticPage(db, auth)
    page.render('/admin/pages/manage.html')
    return dict(grid=page.grid())


# Display all static html pages
def show():
    page = StaticPage(db, auth)
    page.render(None)
    html_page = page.show(page_id=request.args(0))
    if html_page is None:
        raise PRETTYHTTP(403, T("Page not found"))
    import os
    new_render = lambda text: render(text, path=os.path.join(request.folder, 'views'), context=dict(**globals()))
    return new_render(html_page)