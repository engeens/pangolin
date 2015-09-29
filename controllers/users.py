# -*- coding: utf-8 -*-

if 'admin' not in auth.user_groups.values():
    if auth.is_logged_in():
        from helpers.prettyexception import PRETTYHTTP
        raise PRETTYHTTP(401, 'Unauthorized')
    else:
        redirect(URL(request.application, 'default', 'user', args=['login'],
                      vars=dict(_next=URL(args=request.args, vars=request.vars))))


def manage():
    person._pre_render()
    person.render('/admin/users/manage.html')
    return dict(grid=person.grid())


def action():
    if person.action(request.args(0), request.args(1)):
        response.flash = T.M('Action done, please [[reload %s]] the page to see the changes') % URL('users', 'manage')
    else:
        response.flash = 'Error, trying to perform the action'