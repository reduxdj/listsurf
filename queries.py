#!/usr/bin/env python


import pymongo
from models import User
import logging
from bson import json_util
###
### Database Connection Handling
###

def init_db_conn(**kwargs):
    dbc = pymongo.Connection(**kwargs)
    db_conn = dbc.linksurf
    return db_conn


def end_request(db_conn):
    """Here as a visual reminder that this funciton must be called at the end
    of a request to return the socket back to pymongo's built-in thread pooling.
    """
    return db_conn.end_request()


###
### Index Handling
###

def apply_all_indexes(db, indexes, collection):
    """Takes a list of indexes and applies them to a collection.

    Intended for use after functions that create/update/delete entire
    documents.
    """
    for index in indexes:
        db[collection].ensure_index(index)

    return True


###
### User Handling
###

USER_COLLECTION = 'users'
indexes_user = [
    [('username', pymongo.ASCENDING)],
    [('email', pymongo.ASCENDING)],
]
    

def load_user(db, username=None, email=None):
    """Loads a user document from MongoDB.
    """
    query_dict = dict()
    if username:
        query_dict['username'] = '%s' % (username.lower())
    elif email:
        query_dict['email'] = email.lower()
    else:
        raise ValueError('Username or email field required')

    user_dict = db[USER_COLLECTION].find_one(query_dict)

    if user_dict is None:
        return None
    else:
        u = User(user_dict)
        return u


def save_user(db, user):
    """Loads a user document from MongoDB.
    """
    user_doc = user.to_primitive()
    uid = db[USER_COLLECTION].insert(user_doc)
    user._id = uid
    apply_all_indexes(db, indexes_user, USER_COLLECTION)
    return uid

###
### ListItem Handling
###

LISTITEM_COLLECTION = 'listitems'
indexes_listitem = [
    [('owner', pymongo.ASCENDING)],
    [('username', pymongo.ASCENDING)],
]
    
def load_listitems(db, username=None):
    """Loads a user document from MongoDB.
    """
    query_set = db[LISTITEM_COLLECTION].find({'username':username})
    return query_set


def save_listitem(db, item):
    """Loads a user document from MongoDB.
    """
    item_doc = item.to_primitive()
    iid = db[LISTITEM_COLLECTION].insert(item_doc)
    item._id = iid
    apply_all_indexes(db, indexes_listitem, LISTITEM_COLLECTION)
    return iid
