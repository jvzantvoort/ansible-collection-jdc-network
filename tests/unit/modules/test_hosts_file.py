# -*- coding: utf-8 -*-
""" Unit tests for hosts_file module """

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import os
import tempfile
import shutil
import unittest
import re
import copy
from io import StringIO 
from pprint import pformat

from unittest.mock import mock_open, patch

import hosts_file
HEADER = '''# Ansible managed
::1             ip6-localhost ip6-loopback localhost localhost.localdomain localhost6 localhost6.localdomain6
fe00::0         ip6-localnet ip6-mcastprefix
ff02::1         ip6-allnodes
ff02::2         ip6-allrouters
127.0.0.1       localhost localhost.localdomain localhost4 localhost4.localdomain4
'''

class TestHostsFile(unittest.TestCase):

    def test_uniq(self):
        """test uniq function"""
        src = ['a', 'b', 'b', 'c']
        dst = ['a', 'b', 'c']
        obj = hosts_file.HostsFile()
        ref = obj.uniq(src)
        self.assertEqual("a b c", " ".join(ref))

    def test_ip2int(self):
        obj = hosts_file.HostsFile()
        ref = obj.ip2int("192.168.1.10")
        self.assertEqual(3232235786, ref)

    def test_int2ip(self):
        obj = hosts_file.HostsFile()
        ref = obj.int2ip(3232235786)
        self.assertEqual("192.168.1.10", ref)

    def test_write(self):
        output = StringIO()
        obj = hosts_file.HostsFile()
        obj.add_defaults()
        obj.write(output)
        contents = output.getvalue()
        output.close()
        lines1 = contents.split("\n")
        lines2 = HEADER.split("\n")
        for i, x in enumerate(lines1):
            self.assertEqual(x, lines2[i])

    def test_add_elements(self):
        obj = hosts_file.HostsFile()
        data = obj.add_elements(["192.168.1.2"], "a", "b")
        self.assertEqual(" ".join(data), "192.168.1.2 a b")
        data = obj.add_elements(["192.168.1.2"], "a", "b", "b")
        self.assertEqual(" ".join(data), "192.168.1.2 a b")

    def test_remove_elements(self):
        obj = hosts_file.HostsFile()
        data = obj.remove_elements(["192.168.1.2", "a", "b", "c"], "a", "b")
        self.assertEqual(" ".join(data), "192.168.1.2 c")




if __name__ == "__main__":
    unittest.main()
