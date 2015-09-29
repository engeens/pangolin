# -*- coding: utf-8 -*-

###########################################################################
#       Don't need to touch this page, look into: 0_settings.py           #
###########################################################################

if INIT_APP:
    LAZY_TABLES = True
    MIGRATE_ENABLED = True
    from gluon.custom_import import track_changes
    track_changes(True)
else:
    LAZY_TABLES = False
    MIGRATE_ENABLED = False

db = DAL(DATABASE_CONNECTION, pool_size=1, check_reserved=['all'],
         lazy_tables=LAZY_TABLES, migrate_enabled=MIGRATE_ENABLED)

session.connect(request, response, db=db)
# response.generic_patterns = ['*'] if request.is_local else []

# (optional) optimize handling of static files
# response.optimize_css = 'concat, minify,inline'
# response.optimize_js = 'concat, minify,inline'

response.formstyle = 'bootstrap3_stacked'

from gluon.tools import Auth, prettydate

# We have the auth in global, to set @auth.login() in controllers
auth = Auth(db, secure=HTTPS)


# With this condition we only create a session when the user request: login, register, etc
if not auth.user and not request.function == 'user' and not request.controller == 'appadmin':
    session.forget()

# We define user tables in order to use @auth.requires_membership, etc
from users import Users
person = Users(db, auth, render_view=False)

# To set the language page
if request.uri_language:
    T.force(request.uri_language)