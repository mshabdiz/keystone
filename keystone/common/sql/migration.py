# Copyright 2012 OpenStack Foundation
# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import sys

from migrate.versioning import api as versioning_api

from keystone.common.sql import migration_helpers
from keystone import config


CONF = config.CONF


try:
    from migrate.versioning import exceptions as versioning_exceptions
except ImportError:
    try:
        # python-migration changed location of exceptions after 1.6.3
        # See LP Bug #717467
        from migrate import exceptions as versioning_exceptions
    except ImportError:
        sys.exit('python-migrate is not installed. Exiting.')


def migrate_repository(version, current_version, repo_path):
    if version is None or version > current_version:
        result = versioning_api.upgrade(CONF.database.connection,
                                        repo_path, version)
    else:
        result = versioning_api.downgrade(
            CONF.database.connection, repo_path, version)
    return result


def db_sync(version=None, package=None):
    if version is not None:
        try:
            version = int(version)
        except ValueError:
            raise Exception(_('version should be an integer'))
    repo_path = migration_helpers.find_migrate_repo(package=package)
    current_version = db_version(package=package)
    return migrate_repository(version, current_version, repo_path)


def db_version(package=None):
    repo_path = migration_helpers.find_migrate_repo(package=package)
    try:
        return versioning_api.db_version(CONF.database.connection, repo_path)
    except versioning_exceptions.DatabaseNotControlledError:
        return db_version_control(version=0, package=package)


def db_version_control(version=None, package=None):
    repo_path = migration_helpers.find_migrate_repo(package=package)
    versioning_api.version_control(CONF.database.connection, repo_path,
                                   version)
    return version
