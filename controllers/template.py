# -*- coding: utf-8 -*-

if ('admin' or 'editor') not in auth.user_groups.values():
    if auth.is_logged_in():
        from helpers.prettyexception import PRETTYHTTP
        raise PRETTYHTTP(401, 'Unauthorized')
    else:
        redirect(URL(request.application, 'default', 'user', args=['login'],
                      vars=dict(_next=URL(args=request.args, vars=request.vars))))


from templates import EmailTemplate
from helpers.prettyexception import PRETTYHTTP
from gluon.template import render


def manage():
    template = EmailTemplate(db, auth)
    template.render('/admin/templates/manage.html')
    return dict(grid=template.grid())


# Display all static html pages
def show():
    import os
    template = EmailTemplate(db, auth)
    template.render(None)
    html_template = template.show(request.args(0))
    if html_template is None:
        raise PRETTYHTTP(403, T("Page not found"))
    return XML(render(html_template, path=os.path.join(request.folder, 'views'), context=globals()))