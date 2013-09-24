import re

import logging
import bson

from schematics.exceptions import ValidationError, StopValidation, ConversionError
from schematics.transforms import blacklist, whitelist
from schematics.exceptions import ValidationError
from brubeck.models import User
from schematics.models import Model

from schematics.models import Model
from schematics.types import (BaseType,
                              DateTimeType,
                              StringType,
                              BooleanType,
                              URLType,
                              EmailType,
                              LongType)


from brubeck import auth
from brubeck.timekeeping import curtime
from datamosh import OwnedModelMixin, StreamedModelMixin

#Right now this is here because I can't seem to get it installed
class ObjectIdType(BaseType):
    """An field wrapper around MongoDB ObjectIds.  It is correct to say they're
    bson fields, but I am unaware of bson being used outside MongoDB.

    `auto_fill` is disabled by default for ObjectIdType's as they are
    typically obtained after a successful save to Mongo.
    """

    def __init__(self, auto_fill=False, **kwargs):
        self.auto_fill = auto_fill
        super(ObjectIdType, self).__init__(**kwargs)

    def convert(self, value):
        if not isinstance(value, bson.objectid.ObjectId):
            value = bson.objectid.ObjectId(unicode(value))
        return value

    def to_primitive(self, value):
        return str(value)

    def validate_id(self, value):
        if not isinstance(value, bson.objectid.ObjectId):
            try:
                value = bson.objectid.ObjectId(unicode(value))
            except Exception, e:
                raise ValidationError('Invalid ObjectId')
        return True
###
### User Document
###

class User(Model):
    """Bare minimum to have the concept of a User.
    """
    username = StringType(max_length=30, required=True)
    password = StringType(max_length=128)

    is_active = BooleanType(default=False)
    last_login = LongType(default=curtime)
    date_joined = LongType(default=curtime)

    username_regex = re.compile('^[A-Za-z0-9._]+$')
    username_min_length = 2

    class Options:
        roles = {
            'owner': blacklist('password', 'is_active'),
        }

    def __unicode__(self):
        return u'%s' % (self.username)

    def set_password(self, raw_passwd):
        """Generates bcrypt hash and salt for storing a user's password. With
        bcrypt, the salt is kind of redundant, but this format stays friendly
        to other algorithms.
        """
        (algorithm, salt, digest) = auth.gen_hexdigest(raw_passwd)
        self.password = auth.build_passwd_line(algorithm, salt, digest)

    def check_password(self, raw_password):
        """Compares raw_password to password stored for user. Updates
        self.last_login on success.
        """
        algorithm, salt, hash = auth.split_passwd_line(self.password)
        (_, _, user_hash) = auth.gen_hexdigest(raw_password,
                                               algorithm=algorithm, salt=salt)
        if hash == user_hash:
            self.last_login = curtime()
            return True
        else:
            return False

    @classmethod
    def create_user(cls, username, password, email=str()):
        """Creates a user document with given username and password
        and saves it.

        Validation occurs only for email argument. It makes no assumptions
        about password format.
        """
        now = curtime()

        username = username.lower()
        email = email.strip()
        email = email.lower()

        # Username must pass valid character range check.
        if not cls.username_regex.match(username):
            warning = 'Username failed character validation - username_regex'
            raise ValueError(warning)

        # Caller should handle validation exceptions
        cls.validate_class_partial(dict(email=email))

        user = cls(username=username, email=email, date_joined=now)
        user.set_password(password)
        return user


###
### UserProfile
###

class UserProfile(Model):
    """The basic things a user profile tends to carry. Isolated in separate
    class to keep separate from private data.
    """
    owner_id = ObjectIdType(required=True)
    owner_username = StringType(max_length=30, required=True)

    created_at = DateTimeType()
    updated_at = DateTimeType()

    # identity info
    name = StringType(max_length=255)
    email = EmailType(max_length=100)
    website = URLType(max_length=255)
    bio = StringType(max_length=100)
    location_text = StringType(max_length=100)
    avatar_url = URLType(max_length=255)

    class Options:
        roles = {
            'owner': blacklist('owner_id'),
        }

    def __init__(self, *args, **kwargs):
        super(UserProfile, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return u'%s' % (self.name)
###
### ListItem
###

class ListItem(Model):
  """Bare minimum to have the concept of streamed item.
  """
  owner = ObjectIdType(required=True)
  username = StringType(max_length=30, required=True)
  
  # streamable
  created_at = DateTimeType()
  updated_at = DateTimeType()

  url = URLType()

  @classmethod
  def make_ownersafe(self,item):
    return item

  class Meta:
      id_field = ObjectIdType

  class Options:
        roles = {
            'owner': blacklist('owner_id'),
        }

  def __unicode__(self):
      return u'%s' % (self.url)
