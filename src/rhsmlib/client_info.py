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
This module holds information about current state of client application
like sender of D-bus method, current subscription-manager command (register,
attach, ...), dnf command, etc.
"""


from rhsmlib.utils import Singleton


class DBusSender(Singleton):
    """
    This class holds information about current sender of D-Bus method
    """

    def __init__(self):
        self._cmd_line = None

    @property
    def cmd_line(self):
        return self._cmd_line

    @cmd_line.setter
    def cmd_line(self, cmd_line):
        self._cmd_line = cmd_line
