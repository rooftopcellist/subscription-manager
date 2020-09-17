from __future__ import print_function, division, absolute_import

# Copyright (c) 2016 Red Hat, Inc.
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
import logging
import sys
import six
import decorator
import dbus.service
import json
import re

from rhsmlib.dbus import exceptions
from rhsmlib.dbus import dbus_utils
from rhsmlib.client_info import DBusSender

log = logging.getLogger(__name__)

__all__ = [
    'dbus_get_sender_cmd_line',
    'dbus_set_sender_cmd_line',
    'dbus_handle_exceptions',
    'dbus_handle_sender',
    'dbus_service_method',
    'dbus_service_signal'
]


def dbus_get_sender_cmd_line(sender, bus=None):
    """
    Try to get command line of sender
    :param sender: sender
    :param bus: bus
    :return:
    """
    if bus is None:
        bus = dbus.SystemBus()
    cmd_line = dbus_utils.command_of_sender(bus, sender)
    if cmd_line is not None and type(cmd_line) == str:
        # Store only first argument of command line (no argument including username or password)
        cmd_line = cmd_line.split()[0]
    return cmd_line


def dbus_set_sender_cmd_line(sender, cmd_line=None, bus=None):
    """
    This method set sender's command line in the singleton object
    :return: None
    """
    dbus_sender = DBusSender()
    if cmd_line is None:
        dbus_sender.cmd_line = dbus_get_sender_cmd_line(sender, bus)
    else:
        dbus_sender.cmd_line = cmd_line
    log.debug("D-Bus sender: %s (cmd-line: %s)" % (sender, dbus_sender.cmd_line))


def dbus_reset_sender_cmd_line():
    """
    Reset sender's command line
    :return: None
    """
    dbus_sender = DBusSender()
    dbus_sender.cmd_line = None


@decorator.decorator
def dbus_handle_sender(func, *args, **kwargs):
    """
    Decorator to handle sender argument
    :param func: method with implementation of own logic of D-Bus method
    :param args: arguments of D-Bus method
    :param kwargs: keyed arguments of D-Bus method
    :return: result of D-Bus method
    """

    sender = None
    # Get sender from arguments
    if 'sender' in kwargs:
        sender = kwargs['sender']
    elif len(args) > 0:
        sender = args[-1]

    if sender is not None:
        dbus_set_sender_cmd_line(sender)

    try:
        return func(*args, **kwargs)
    finally:
        dbus_reset_sender_cmd_line()


@decorator.decorator
def dbus_handle_exceptions(func, *args, **kwargs):
    """
    Decorator to handle exceptions, log them, and wrap them if necessary.
    """

    try:
        return func(*args, **kwargs)
    except Exception as err:
        log.exception(err)
        trace = sys.exc_info()[2]

        severity = "error"
        # Remove "HTTP error (...): " string from the messages:
        pattern = '^HTTP error \x28.*\x29: '
        err_msg = re.sub(pattern, '', str(err))
        # Modify severity of some exception here
        if "Ignoring request to auto-attach. It is disabled for org" in err_msg:
            severity = "warning"
        if hasattr(err, 'severity'):
            severity = err.severity
        # Raise exception string as JSON string. Thus it can be parsed and printed properly.
        error_msg = json.dumps(
            {
                "exception": type(err).__name__,
                "severity": severity,
                "message": err_msg
            }
        )
        six.reraise(exceptions.RHSM1DBusException, exceptions.RHSM1DBusException(error_msg), trace)


def dbus_service_method(*args, **kwargs):
    # Tell python-dbus that "sender" will be the keyword to use for the sender unless otherwise
    # defined.
    kwargs.setdefault("sender_keyword", "sender")
    return dbus.service.method(*args, **kwargs)


def dbus_service_signal(*args, **kwargs):
    """
    Decorator used for signal
    :param args:
    :param kwargs:
    :return:
    """
    return dbus.service.signal(*args, **kwargs)
