"""
    Tor2web
    Copyright (C) 2012 Hermes No Profit Association - GlobaLeaks Project

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

"""

:mod:`Tor2Web`
=====================================================

.. automodule:: Tor2Web
   :synopsis: [GLOBALEAKS_MODULE_DESCRIPTION]

.. moduleauthor:: Arturo Filasto' <art@globaleaks.org>
.. moduleauthor:: Giovanni Pellerano <evilaliv3@globaleaks.org>

"""

# -*- coding: utf-8 -*-

import os
import re
import sys
import ConfigParser
from optparse import OptionParser
from storage import Storage

listpattern = re.compile(r'\s*("[^"]*"|.*?)\s*,')

class Config(Storage):
    """
    A Storage-like class which loads each attribute into a portable conf file.
    """
    def __init__(self):
        Storage.__init__(self)
        self._section = 'main'
        self._parser = ConfigParser.ConfigParser()

        parser = OptionParser()
        parser.add_option("-c", "--configfile", dest="configfile", default="/etc/tor2web.conf")
        parser.add_option("-p", "--pidfile", dest="pidfile", default='/var/run/tor2web/t2w.pid')
        parser.add_option("-u", "--uid", dest="uid", default='')
        parser.add_option("-g", "--gid", dest="gid", default='')
        parser.add_option("-n", "--nodaemon", dest="nodaemon", default=False, action="store_true")
        parser.add_option("-d", "--rundir", dest="rundir", default='/var/run/tor2web/')
        parser.add_option("-x", "--command", dest="command", default='start')
        (options, args) = parser.parse_args()

        self._file = options.configfile

        self.__dict__['configfile'] = options.configfile
        self.__dict__['pidfile'] = options.pidfile
        self.__dict__['uid'] = options.uid
        self.__dict__['gid'] = options.gid
        self.__dict__['nodaemon'] = options.nodaemon
        self.__dict__['command'] = options.command
        self.__dict__['nodename'] = 'tor2web'
        self.__dict__['datadir'] = '/home/tor2web'
        self.__dict__['rundir'] = options.rundir
        self.__dict__['logreqs'] = False
        self.__dict__['debugmode'] = False
        self.__dict__['debugtostdout'] = False
        self.__dict__['processes'] = 1
        self.__dict__['requests_per_process'] = 1000000
        self.__dict__['transport'] = 'BOTH'
        self.__dict__['listen_ipv4'] = '127.0.0.1'
        self.__dict__['listen_ipv6'] = None
        self.__dict__['listen_port_http'] = 80
        self.__dict__['listen_port_https'] = 443
        self.__dict__['basehost'] = 'tor2web.org'
        self.__dict__['sockshost'] = '127.0.0.1'
        self.__dict__['socksport'] = 9050
        self.__dict__['socksoptimisticdata'] = True
        self.__dict__['sockmaxpersistentperhost'] = 5
        self.__dict__['sockcachedconnectiontimeout'] = 240
        self.__dict__['sockretryautomatically'] = True
        self.__dict__['cipher_list'] = 'ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384:' \
                                       'ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-SHA256:' \
                                       'ECDHE-RSA-AES256-SHA:DHE-DSS-AES256-SHA:DHE-RSA-AES128-SHA:' \
                                       'DES-CBC3-SHA' # this last one (not FS) is kept only for
                                                      # compatibility reasons :/
        self.__dict__['mode'] = 'BLACKLIST'
        self.__dict__['onion'] = None
        self.__dict__['blockcrawl'] = True
        self.__dict__['overriderobotstxt'] = True
        self.__dict__['disable_banner'] = False
        self.__dict__['smtp_user'] = ''
        self.__dict__['smtp_pass'] = ''
        self.__dict__['smtp_mail'] = ''
        self.__dict__['smtpmailto_exceptions'] = ''
        self.__dict__['smtpmailto_notifications'] = ''
        self.__dict__['smtpdomain'] = ''
        self.__dict__['smtpport'] = 587
        self.__dict__['exit_node_list_refresh'] = 600
        self.__dict__['automatic_blocklist_updates_source'] = ''
        self.__dict__['automatic_blocklist_updates_refresh'] = 600
        self.__dict__['publish_lists'] = False
        self.__dict__['mirror'] = []
        self.__dict__['dummyproxy'] = None

        # Development VS. Production
        localpath = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), "..", "data"))
        if os.path.exists(localpath):
            self.__dict__['sysdatadir'] = localpath
        else:
            self.__dict__['sysdatadir'] = '/usr/share/tor2web'

        self.load()

    def load(self):
        try:
            if (not os.path.exists(self._file) or
                not os.path.isfile(self._file) or
                not os.access(self._file, os.R_OK)):
                print "Tor2web Startup Failure: cannot open config file (%s)" % self._file
                exit(1)
        except Exception:
            print "Tor2web Startup Failure: error while accessing config file (%s)" % self._file
            exit(1)

        try:

            self._parser.read([self._file])

            for name in self._parser.options(self._section):
                self.__dict__[name] = self.parse(name)

        except Exception as e:
            print e
            raise Exception("Tor2web Error: invalid config file (%s)" % self._file)

    def splitlist(self, line):
        return [x[1:-1] if x[:1] == x[-1:] == '"' else x
            for x in listpattern.findall(line.rstrip(',') + ',')]

    def parse(self, name):
        try:

           value = self._parser.get(self._section, name)
           if value.isdigit():
                value = int(value)
           elif value.lower() in ('true', 'false'):
                value = value.lower() == 'true'
           elif value.lower() in ('', 'none'):
                value = None
           elif value[0] == "[" and value[-1] == "]":
                value = self.splitlist(value[1:-1])

           return value

        except ConfigParser.NoOptionError:
            # if option doesn't exists returns None
            return None

    def __getattr__(self, name):
        return self.__dict__.get(name, None)

    def __setattr__(self, name, value):
        self.__dict__[name] = value

        # keep an open port with private attributes
        if name.startswith("_"):
            return

        try:

            # XXX: Automagically discover variable type
            self._parser.set(self._section, name, value)

        except ConfigParser.NoOptionError:
            raise NameError(name)

    def t2w_file_path(self, path):
        if os.path.exists(os.path.join(self.datadir, path)):
            return os.path.join(self.datadir, path)
        else:
            return os.path.join(self.sysdatadir, path)

