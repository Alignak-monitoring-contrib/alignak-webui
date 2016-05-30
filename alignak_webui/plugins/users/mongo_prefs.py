#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=wrong-import-position, too-many-return-statements

# Copyright (C) 2015-2016 F. Mohier pour IPM France

'''
    Plugin User's preferences
'''

import json
import time
import traceback
from logging import getLogger

logger = getLogger(__name__)

try:
    from pymongo import MongoClient
    from pymongo.errors import ServerSelectionTimeoutError
except ImportError:  # pragma: no cover - should not happen
    logger.error('Can not initialize module because your pymongo lib is not installed'
                 ' or is too old. Please install it with: pip install pymongo>=3.2')
    raise


class MongoDBPreferences(object):
    '''
    This module job is to get webui configuration data from a mongodb database:
    '''

    def __init__(self, config):
        '''
        Create instance
        '''
        self.uri = config.get('uri', 'mongodb://localhost')
        logger.info('mongo uri: %s', self.uri)

        self.replica_set = config.get('replica_set', None)
        logger.info('mongo replica_set: %s', self.replica_set)

        self.database = config.get('database', 'WebUI')
        self.username = config.get('username', None)
        self.password = config.get('password', None)
        logger.info('database: %s, user: %s', self.database, self.username)

        self.mongodb_fsync = config.get('mongodb_fsync', "True") == "True"

        self.available = False
        self.is_connected = False
        self.con = None
        self.db = None

        logger.info(
            "Trying to open a Mongodb connection to %s, database: %s",
            self.uri, self.database
        )
        self.open()

    def open(self):
        '''
        Open and test database connection
        '''
        logger.info(
            "Trying to open a Mongodb connection to %s, database: %s",
            self.uri, self.database
        )

        try:
            if self.replica_set:  # pragma: no cover - not tested on replica set DB :/
                self.con = MongoClient(
                    self.uri, fsync=self.mongodb_fsync, connect=False, replicaSet=self.replica_set
                )
            else:
                self.con = MongoClient(
                    self.uri, fsync=self.mongodb_fsync, connect=False
                )
            logger.info("created a mongo client: %s", self.uri)

            r = self.con.admin.command("ismaster")
            logger.info("connected to MongoDB, admin: %s", r)
            logger.info("server information: %s", self.con.server_info())

            self.db = self.con[self.database]
            logger.info("connected to the database: %s (%s)", self.database, self.db)

            if self.username and self.password:  # pragma: no cover - not tested with Mongo auth.
                self.db.authenticate(self.username, self.password)
                logger.info("user authenticated: %s", self.username)

            self.available = True
            self.is_connected = True
            logger.info('database connection established')
        except ServerSelectionTimeoutError:
            logger.error("MongoDB server is not available")
        except Exception as e:  # pragma: no cover - should never occur, simple security
            logger.error("Exception: %s", str(e))
            logger.debug("Exception type: %s", type(e))
            logger.debug("Back trace: %s", traceback.format_exc())
            # Depending on exception type, should raise ...
            self.is_connected = False
            raise

        return self.is_connected

    def close(self):  # pragma: no cover - never close except if an error occur
        '''
        Close database connection
        '''
        self.is_connected = False
        self.con.close()

    def get_ui_user_preference(self, username, key=None, default=None):
        '''
        Get a user preferences
        '''
        if not self.available:
            return default

        if not self.is_connected:  # pragma: no cover - always remain connected...
            if not self.open():
                logger.error("error during initialization, no database connection!")
                return default

        if not username:  # pragma: no cover - should never occur, simple security
            logger.warning("error get_ui_user_preference, no username!")
            return None

        try:
            e = self.db.ui_user_preferences.find_one({'_id': username})
            logger.debug("get_ui_user_preference, username: %s, key: %s", username, key)
        except Exception as e:  # pragma: no cover - should never occur, simple security
            logger.warning("Exception: %s", str(e))
            logger.warning("Back trace: %s", traceback.format_exc())
            self.is_connected = False
            return default

        # If no specific key is required, returns all user parameters ...
        if key is None:
            return e

        # Maybe it's a new entry or missing this parameter, bail out
        if not e or key not in e:
            logger.debug("new parameter or not stored preference: %s", key)
            return default

        logger.debug(
            "get_ui_user_preference, username: %s, key: %s = %s",
            username, key, e.get(key)
        )
        return e.get(key)

    def set_ui_user_preference(self, username, key, value):
        '''
        Set a user preferences
        '''
        if not self.available:
            return None

        if not self.is_connected:  # pragma: no cover - always remain connected...
            if not self.open():
                logger.error("error during initialization, no database connection!")
                return None

        if not username:  # pragma: no cover - should never occur, simple security
            logger.warning("error set_ui_user_preference, no username!")
            return None

        try:
            logger.debug(
                "set_ui_user_preference, username: %s, key: %s = %s", username, key, value
            )

            # check if a collection exist for this user
            u = self.db.ui_user_preferences.find_one({'_id': username})
            if not u:
                # no collection for this user? create a new one
                r = self.db.ui_user_preferences.save(
                    {'_id': username, key: value}
                )
            else:
                r = self.db.ui_user_preferences.update_one(
                    {'_id': username}, {'$set': {key: value}}
                )
            # Maybe there was an error ...
            if not r:  # pragma: no cover - should never occur, simple security
                logger.error("set_ui_user_preference, error: %s", r)
        except Exception as e:  # pragma: no cover - should never occur, simple security
            logger.warning("Exception: %s", str(e))
            logger.warning("Back trace: %s", traceback.format_exc())
            self.is_connected = False

        return None

    def get_ui_common_preference(self, key, default=None):
        '''
        Get all users common preferences
        '''
        return self.get_ui_user_preference('global', key=key, default=default)

    def set_ui_common_preference(self, key, value):
        '''
        Set all users common preferences
        '''
        return self.set_ui_user_preference('global', key=key, value=value)

    def get_user_bookmarks(self, username):
        ''' Returns the user bookmarks. '''
        return json.loads(self.get_ui_user_preference(username, 'bookmarks') or '[]')

    def get_common_bookmarks(self):
        ''' Returns the common bookmarks. '''
        return json.loads(self.get_ui_common_preference('bookmarks') or '[]')
