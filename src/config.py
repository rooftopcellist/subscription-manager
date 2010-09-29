#
# This module has been originally modified and enhanced from Red Hat Update Agent's config module.
#
# Copyright (c) 2010 Red Hat, Inc.
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
#

import ConfigParser


DEFAULT_CONFIG_DIR = "/etc/rhsm"
DEFAULT_CONFIG_PATH = "%s/rhsm.conf" % DEFAULT_CONFIG_DIR

DEFAULTS = {
        'hostname': 'localhost',
        'prefix': '/candlepin',
        'port': '8443',
        'ca_cert_dir': '/etc/rhsm/ca/',
        }

def initConfig(config_file=None):

    global CFG
    # If a config file was specified, assume we should overwrite the global config
    # to use it. This should only be used in testing. Could be switch to env var?
    if config_file:
        CFG = ConfigParser.ConfigParser(defaults=DEFAULTS)
        CFG.read(config_file)
        return CFG

    # Normal application behavior, just read the default file if we haven't
    # already:
    try:
        CFG = CFG
    except NameError:
        CFG = None
    if CFG == None:
        CFG = ConfigParser.ConfigParser(defaults=DEFAULTS)
        CFG.read(DEFAULT_CONFIG_PATH)
    return CFG
