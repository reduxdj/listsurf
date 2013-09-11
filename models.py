from dictshield.document import Document, swap_field
from dictshield.fields import (BaseField,
                               StringField,
                               BooleanField,
                               URLField,
                               EmailField,
                               LongField)
# this might get moved
from dictshield.fields.mongo import ObjectIdField

from brubeck.models import User
from brubeck.timekeeping import MillisecondField



from schematics.models import Model
from schematics.types import StringType, DecimalType
from schematics.serialize import whitelist

###
### Social Models
###

### Adjust ID field in Brubeck models
User = swap_field(User, ObjectIdField, ['id'])


###
### List Models
###

#https://github.com/j2labs/dictshield/blob/master/dictshield/fields/mongo.py


class ListItem(Model):
    """Bare minimum to have the concept of streamed item.
    """
    # ownable
    owner = ObjectIdField(required=True)
    username = StringField(max_length=30, required=True)

    # streamable
    created_at = MillisecondField()
    updated_at = MillisecondField()

    url = URLField()

    class Meta:
        id_field = ObjectIdField

    _private_fields = [
        'owner',
    ]

    def __unicode__(self):
        return u'%s' % (self.url)
