#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Ansible module jdc.network.hosts_file"""

DOCUMENTATION = r"""
---
module: hosts_file
short_description: Manage the hosts file
description:
  - The M(jdc.network.hosts_file) module helps managing the contents of the V(/etc/hosts) file.
options:
  hostsfile:
    description: Define the hosts file
    type: str
    default: "/etc/hosts"
  debuglog:
    description: defined log file for debugging
    type: str
  state:
    description: state choices absent or present
    default: "present"
    type: str
    choices:
      - absent
      - present
  definitions:
    description: List of dicts
    type: list
    elements: raw
  defaults:
    description: add the default entries
    default: false
    type: bool
author:
  - John van Zantvoort (@jvzantvoort) <john@vanzantvoort.org>
"""

EXAMPLES = r"""
- name: add pietje
  jdc.network.hosts_file:
    hostsfile: /tmp/lala
    definitions:
      - ipaddress: 172.0.0.100
        hostnames:
          - pietje
          - lala
          - lala.lala
      - ipaddress: 172.0.0.101
        hostnames:
          - fred

- name: remove lala
  jdc.network.hosts_file:
    hostsfile: /tmp/lala
    state: absent
    definitions:
      - ipaddress: 172.0.0.100
        hostnames:
          - lala
"""

RETURN = r"""
---
hostsfile:
    description: the path to C(/etc/hosts)
    type: str
    returned: always
    sample: '/etc/hosts'
"""

# pylint: disable=C0103
__metaclass__ = type

import re
import os
import json
import socket
import struct
from datetime import datetime

from ansible.module_utils.basic import AnsibleModule


# from ansible.module_utils.common.text.converters import to_bytes, to_text

__author__ = "jvzantvoort"
__copyright__ = "John van Zantvoort"
__email__ = "john@vanzantvoort.org"
__license__ = "MIT"
__version__ = "1.0.1"

# https://stackoverflow.com/questions/53497/regular-expression-that-matches-valid-ipv6-addresses
IPV4SEG = r"(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])"
IPV4ADDR = r"(?:(?:" + IPV4SEG + r"\.){3,3}" + IPV4SEG + r")"
IPV6SEG = r"(?:(?:[0-9a-fA-F]){1,4})"
IPV6GROUPS = (
    r"(?:" + IPV6SEG + r":){7,7}" + IPV6SEG,
    r"(?:" + IPV6SEG + r":){1,7}:",
    r"(?:" + IPV6SEG + r":){1,6}:" + IPV6SEG,
    r"(?:" + IPV6SEG + r":){1,5}(?::" + IPV6SEG + r"){1,2}",
    r"(?:" + IPV6SEG + r":){1,4}(?::" + IPV6SEG + r"){1,3}",
    r"(?:" + IPV6SEG + r":){1,3}(?::" + IPV6SEG + r"){1,4}",
    r"(?:" + IPV6SEG + r":){1,2}(?::" + IPV6SEG + r"){1,5}",
    IPV6SEG + r":(?:(?::" + IPV6SEG + r"){1,6})",
    r":(?:(?::" + IPV6SEG + r"){1,7}|:)",
    r"fe80:(?::" + IPV6SEG + r"){0,4}%[0-9a-zA-Z]{1,}",
    r"::(?:ffff(?::0{1,4}){0,1}:){0,1}[^\s:]" + IPV4ADDR,
    r"(?:" + IPV6SEG + r":){1,4}:[^\s:]" + IPV4ADDR,
)
# IPV6ADDR = '|'.join(['(?:{})'.format(g) for g in IPV6GROUPS[::-1]])
IPV6ADDR = "|".join([f"(?:{g})" for g in IPV6GROUPS[::-1]])


# pylint: disable=R0902
class HostsFile:
    """Manage the hosts file

    :param hostsfile: Path to hosts file
    :param debuglog: Path to logfile
    :param state: present or absent
    :param definitions: hosts definitions

    :type debuglog: str
    :type hostsfile: str
    :type state: str
    :type definitions: list
    """

    def __init__(self, **kwargs):

        self.hostsfile = kwargs.get("hostsfile", "/etc/hosts")
        self.debuglog = kwargs.get("debuglog")
        self.state = kwargs.get("state")
        self.definitions = kwargs.get("definitions")

        self.pattern_ipv4 = re.compile(IPV4ADDR)
        self.pattern_ipv6 = re.compile(IPV6ADDR)
        self.ipv4 = {}
        self.ipv6 = {}
        self.result = {"changed": False, "hostsfile": self.hostsfile}

    @staticmethod
    def uniq(names):
        """create a uniq list"""
        retv = set()
        for element in names:
            retv.add(element)
        return sorted(list(retv))

    @staticmethod
    def ip2int(addr):
        """convert an ip address to an integer"""
        return struct.unpack("!I", socket.inet_aton(addr))[0]

    @staticmethod
    def int2ip(addr):
        """convert an integer to an ip address"""
        return socket.inet_ntoa(struct.pack("!I", addr))

    @property
    def changed(self):
        """return the changed state"""
        return self.result.get("changed")

    @changed.setter
    def changed(self, state):
        """set the changed state"""
        if self.result.get("changed") != state:
            self.log(f"changed state set to {state}")
            self.result["changed"] = state
        return state

    def log(self, msg, pretty_print=False):
        """log a message

        :param msg: message
        :type msg: str
        :param pretty_print: pretty print message
        :type pretty_print: bool
        """

        if self.debuglog is None:
            return

        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        with open(self.debuglog, "a", encoding="utf8") as logh:
            if pretty_print:
                msg = json.dumps(msg, sort_keys=True, indent=4, separators=(",", ": "))

            for line in msg.split("\n"):
                logh.write(f"{timestamp} {line}\n")

    def remove_elements(self, srclist, *prune_list):
        """
        remove elements

        :param srclist: source list
        :param prune_list: elements to remove
        :return: new list
        """
        for rm_elem in prune_list:
            tmplist = []
            for src in srclist:
                if rm_elem.lower() == src.lower():
                    self.log(f"remove element {rm_elem}")
                    self.changed = True
                else:
                    tmplist.append(src)
            srclist = tmplist
        return self.uniq(srclist)

    def add_elements(self, srclist, *add_list):
        """
        add elements

        :param srclist: source list
        :param add_list: elements to add
        :return: new list
        """
        for add_elem in add_list:
            add_elem = add_elem.lower()
            if add_elem in srclist:
                continue
            self.log(f"add element {add_elem}")
            srclist.append(add_elem)
            self.changed = True
        return self.uniq(srclist)

    def add_line(self, line):
        """
        add line

        :param line: line
        """
        cols = line.lower().split()
        ipaddr = cols.pop(0)
        self.add_entry(ipaddr, *cols)

    def readfile(self):
        """read hosts file"""
        if not os.path.exists(self.hostsfile):
            self.log("hostsfile does not exists")
            return

        with open(self.hostsfile, encoding="utf8") as ifh:
            for line in ifh.readlines():

                if "#" in line:
                    line = line.split("#")[0]
                line = line.strip()

                if line:
                    self.add_line(line)

        # reset to default
        self.changed = False

    def is_ipv4(self, ipaddr):
        """

        :param ipaddr:
        :return:
        """
        match = self.pattern_ipv4.match(ipaddr)

        if match is None:
            return False
        return True

    def is_ipv6(self, ipaddr):
        """

        :param ipaddr:
        :return:
        """
        match = self.pattern_ipv6.match(ipaddr)

        if match is None:
            return False
        return True

    def add_entry(self, ipaddr, *hosts):
        """

        :param ipaddr:
        :param hosts:
        :return:
        """
        hosts_str = ", ".join(list(hosts))
        self.log(f"add_entry({ipaddr}, {hosts_str})")
        match4 = self.pattern_ipv4.match(ipaddr)
        match6 = self.pattern_ipv6.match(ipaddr)

        if match4 is not None:
            nipaddr = self.ip2int(ipaddr)
            names = self.ipv4.get(nipaddr, [])
            self.ipv4[nipaddr] = self.add_elements(names, *hosts)

        elif match6 is not None:
            names = self.ipv6.get(ipaddr, [])
            self.ipv6[ipaddr] = self.add_elements(names, *hosts)

        else:
            raise Exception("invalid address: {ipaddr}")

    def remove_entry(self, ipaddr, *hosts):
        """

        :param ipaddr:
        :param hosts:
        :return:
        """
        hosts_str = ", ".join(list(hosts))
        self.log(f"remove_entry({ipaddr}, {hosts_str})")
        names = []
        if self.is_ipv4(ipaddr):
            nipaddr = self.ip2int(ipaddr)
            names = self.ipv4.get(nipaddr, [])
            self.ipv4[nipaddr] = self.remove_elements(names, *hosts)

        elif self.is_ipv6(ipaddr):
            names = self.ipv6.get(ipaddr, [])
            self.ipv6[ipaddr] = self.remove_elements(names, *hosts)

        else:
            raise Exception(f"invalid address: {ipaddr}")

    def write(self, ofh):
        """write hosts file

        :param ofh: output file handle
        :type ofh: file
        """
        ofh.write("# Ansible managed\n")

        for ipaddr in sorted(self.ipv6):
            names = " ".join(self.ipv6.get(ipaddr, []))
            if names:
                ofh.write(f"{ipaddr:<15} {names}\n")

        for ipaddr in sorted(self.ipv4):
            names = " ".join(self.ipv4.get(ipaddr, []))
            if names:
                intip = self.int2ip(ipaddr)
                ofh.write(f"{intip:<15} {names}\n")

    def add_defaults(self):
        self.add_entry("::1", "ip6-localhost", "ip6-loopback")
        self.add_entry("::1", "localhost", "localhost.localdomain")
        self.add_entry("::1", "localhost6", "localhost6.localdomain6")
        self.add_entry("fe00::0", "ip6-localnet", "ip6-mcastprefix")
        self.add_entry("ff02::1", "ip6-allnodes")
        self.add_entry("ff02::2", "ip6-allrouters")
        self.add_entry("127.0.0.1", "localhost", "localhost.localdomain")
        self.add_entry("127.0.0.1", "localhost4", "localhost4.localdomain4")

    def main(self, **kwargs):
        """
        :param hostsfile: Path to hosts file
        :param debuglog: Path to logfile
        :param state: present or absent
        :param defaults: Add default entries
        :param definitions: hosts definitions

        """
        self.log("start")
        self.readfile()
        defaults = kwargs.get("defaults", False)

        if defaults:
            self.add_defaults()

        for row in self.definitions:
            hostnames = row.get("hostnames")
            ipaddress = row.get("ipaddress")

            if self.state == "present":
                self.add_entry(ipaddress, *hostnames)
            else:
                self.remove_entry(ipaddress, *hostnames)

        if self.changed:
            with open(self.hostsfile, "w", encoding="utf8") as ofh:
                self.write(ofh)

        return self.result


def main():
    """main"""
    module = AnsibleModule(
        argument_spec=dict(
            hostsfile=dict(type="str", default="/etc/hosts"),
            debuglog=dict(type="str"),
            state=dict(type="str", default="present", choices=["absent", "present"]),
            definitions=dict(type="list", elements="raw"),
            defaults=dict(type="bool", default=False),
        ),
        supports_check_mode=True,
    )

    hostf = HostsFile(
        hostsfile=module.params["hostsfile"],
        debuglog=module.params["debuglog"],
        state=module.params["state"],
        definitions=module.params["definitions"],
    )

    result = hostf.main()

    module.exit_json(**result)


if __name__ == "__main__":
    main()
