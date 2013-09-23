from schematics.types import (
    BaseType, StringType, DateTimeType, DateType, IntType, EmailType, LongType,
    URLType
)
from schematics.exceptions import ValidationError, StopValidation, ConversionError


"""This module contains fields that depend on importing `bson`. `bson` is
as part of the pymongo distribution.
"""

from schematics.types import BaseType
from schematics.exceptions import ValidationError
from brubeck.models import User
from schematics.models import Model

import logging
import bson

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

class User(User):
  id = ObjectIdType()
  username = StringType()
  @classmethod
  def validate_class_partial(self,value):
    return True


class ListItem(Model):
  """Bare minimum to have the concept of streamed item.
  """
  owner = ObjectIdType(required=True)
  username = StringType(max_length=30, required=True)
  
  # streamable
  created_at = DateTimeType()
  updated_at = DateTimeType()

  url = URLType()

  class Meta:
      id_field = ObjectIdType

  _private_fields = [
      'owner',
  ]

  def __unicode__(self):
      return u'%s' % (self.url)