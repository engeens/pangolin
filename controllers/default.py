# -*- coding: utf-8 -*-

def index():
    redirect(URL(request.application, 'home', 'show', args=['index']))


def user():
    # We define the type of access (login)
    from myapp import access
    # Set all the access settings
    access(db, auth)
    form = auth()
    # Some style to the form
    form.element(_type='submit')['_class']="btn btn-lg btn-success btn-block"
    person.render('/login/user.html')
    return dict(form=form)


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def init():
    from config import InitApp
    init_app = InitApp(db, INIT_APP, auth)
    status, traceback = init_app.set()
    return traceback
