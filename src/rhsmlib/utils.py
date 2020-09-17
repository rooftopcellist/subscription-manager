from __future__ import print_function, division, absolute_import

# Copyright (c) 2017 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public License,
# version 2 (GPLv2). There is NO WARRANTY for this software, express or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. You should have received a copy of GPLv2
# along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.
#
# Red Hat trademarks are not licensed under GPLv2. No permission is
# granted to use or replicate Red Hat trademarks that are incorporated
# in this software or its documentation.

"""
This module includes several utils that could be used by several client
applications.
"""


class Singleton(object):
    """
    Singleton and parent for singletons
    """
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        """
        Function called, when new instance of Singleton is requested
        """
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
        else:
            cls.__init__ = lambda *_args, **_kwargs: None

        return cls._instance
