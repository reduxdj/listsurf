import sys
import time
import logging
import pymongo
import json
from PIL import Image
import StringIO
import uuid
from brubeck.auth import web_authenticated, UserHandlingMixin
from brubeck.request_handling import WebMessageHandler
from brubeck.templating import Jinja2Rendering
import os

from brubeck.models import User
from models import ListItem,ObjectIdType
from queries import (load_user,
                     save_user,
                     page_listitems,
                     load_listitems,
                     save_listitem)


from datetime import date
import datetime
from schematics.types import DateTimeType

from brubeck.timekeeping import curtime
from datetime import datetime, timedelta

def totimestamp(dt, epoch=datetime(1970,1,1)):
    td = dt - epoch
    # return td.total_seconds()
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 1e6 


###
### Authentication
###

class BaseHandler(WebMessageHandler, UserHandlingMixin):
    """This Mixin provides a `get_current_user` implementation that
    validates auth against our hardcoded user: `demo_user`
    """
    def get_current_user(self):
        """Attempts to load user information from cookie. If that
        fails, it looks for credentials as arguments.

        It then attempts auth with the found credentials by checking for that in
        the database.
        """
        user = None
        # Try loading credentials from secure cookie
        user_id = self.get_cookie('user_id',
                                  secret=self.application.cookie_secret)

        logging.debug(user_id)
        # If secure cookies yields username, load it
        if user_id:
            user = load_user(self.db_conn, username=user_id)
            return user
        
        # If not, check POST args and attempt load
        else:
            username = self.get_argument('username')
            password = self.get_argument('password')
            if username:
                user = load_user(self.db_conn, username=username)

        if not user or (user and user.username != username):
            logging.error('Auth fail: bad username')
            return
            
        if not user.check_password(password):
            logging.error('Auth fail: bad password')
            return
        
        logging.debug('Access granted for user: %s' % user.username)
        return user
###
### Account Handlers
###

class AccountLoginHandler(BaseHandler, Jinja2Rendering):
    def get(self):
        """Offers login form to user
        """
        return self.render_template('accounts/login.html')
    
    @web_authenticated
    def post(self):
        """Checks credentials with decorator and sends user authenticated
        users to the landing page.
        """
        self.set_cookie('user_id', self.current_user.username,
                        secret=self.application.cookie_secret)
        
        return self.redirect('/list')


class AccountLogoutHandler(BaseHandler, Jinja2Rendering):
    def get(self):
        """Clears cookie and sends user to login page
        """
        self.delete_cookies()
        return self.redirect(self.application.login_url)


class AccountCreateHandler(BaseHandler, Jinja2Rendering):
    def get(self):
        """Offers login form to user
        """
        return self.render_template('accounts/create.html')
    
    def post(self):
        """Attempts to create an account with the credentials provided in the
        post arguments.

        Successful creation logs the user in and sends them to '/'.

        Failure returns the user to the account create screen and tells them
        what went wrong.
        """
        username = self.get_argument('username')
        password = self.get_argument('password').encode('utf-8')
        email = self.get_argument('email')

        try:
            now = curtime()
            username = username.lower()
            email = email.strip().lower()
            user = User({'username':username, 'email':email, 'date_joined':now})
            user.set_password(password)
            user.validate()
            save_user(self.db_conn, user)
        except Exception, e:
            logging.error('Credentials failed')
            logging.error(e)
            return self.render_template('accounts/create.html')

        logging.debug('User <%s> created' % (username))
        self.set_cookie('user_id', username,
                        secret=self.application.cookie_secret)

        return self.redirect('/list')


###
### Application Handlers
###

### Web Handlers

class ListDisplayHandler(BaseHandler, Jinja2Rendering):
    """A link listserv (what?!)
    """
    @web_authenticated
    def get(self):
        """Renders a template with our links listed
        """
        items_qs = load_listitems(self.db_conn, self.current_user.username)
        items_qs.sort('updated_at', direction=pymongo.DESCENDING)
        
        items = [ ListItem(i).to_primitive(role='owner') for i in items_qs ]
        context = {
            'links': items,
        }
        return self.render_template('linklists/link_list.html', **context)


class ListAddHandler(BaseHandler, Jinja2Rendering):
    """A link listserv (what?!)
    """
    @web_authenticated
    def get(self):
        """Renders a template with our links listed
        """
        url = self.get_argument('u')
        context = {}
        if url is not None:
            context['url'] = url
        return self.render_template('linklists/item_add.html', **context)

    @web_authenticated
    def post(self):
        """Accepts a URL argument and saves it to the database
        """
        url = self.get_argument('url')

        if not url.startswith('http'):
            url = 'http://%s' % (url)
        
        logging.info( self.current_user.to_primitive() )
        link_item = {
            'owner': self.current_user.id,
            'username': self.current_user.username,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'url': url,
        }

        item = ListItem(link_item)
        item.validate()
        save_listitem(self.db_conn, item)
        return self.redirect('/list')


class StreamedHandlerMixin:
    """Provides standard definitions for paging arguments
    """
    def get_stream_offset(self, default_since=0):
        """This function returns some offset for use with either `created_at`
        or `updated_at` as provided by `StreamModelMixin`.
        """
        since = int(self.get_argument('since',default_since))
        return since

    def get_paging_arguments(self, default_count=25, default_page=0, max_count=25):
        """This function checks for arguments called `page` and `count`. It
        returns a tuple either with their value or default values.

        `max_count` may be used to put a limit on the number of items in each
        page. It defaults to 25, but you can use.
        """
        page = int(self.get_argument('page',default_page))
        count = int(self.get_argument('count',default_count))
        if count > max_count: count = max_count
        skip = (page+1)*count - count
        limit = (page+1)*count
        return {'page': page, 'count':count, 'skip': skip, 'limit': limit}

class UploadHandler(BaseHandler):
    def post(self):
        """Checks credentials with decorator and sends user authenticated
        users to the landing page.
        """
        if hasattr(self.message, 'files'):
            im = Image.open(StringIO.StringIO(self.message.files['files'][0]['body']))
            path = 'media/%s' % str(self.current_user.id)
            try:
                os.mkdir( path )
            except:
                pass
            filename = "%s/%s.png" % ( path, str(uuid.uuid1() ) , )
            im.save( filename, format="PNG")
        return self.redirect('/list')

### API Handler

class APIListDisplayHandler(BaseHandler,StreamedHandlerMixin):
    """A link listserv (what?!)
    """
    @web_authenticated
    def get(self):
        """Renders a JSON response
        """
        paging_arguments = self.get_paging_arguments()
        total = load_listitems(self.db_conn, self.current_user.username).count()
        items_qs = page_listitems(self.db_conn, self.current_user.username,**paging_arguments)
        items_qs.sort('updated_at', direction=pymongo.DESCENDING)
        num_items = items_qs.count()
        response = {
            'paging' : {
                'page'  : paging_arguments['page'],
                'count' : paging_arguments['count'],
                'total' : total
            },
            'items' :  [ ListItem(i).to_primitive(role='owner') for i in items_qs]
        }
        self.set_body(json.dumps( response ))
        return self.render(status_code=200)
    
    @web_authenticated
    def post(self):
        """Renders a template with our links listed
        """
        return self.get()
