#!/usr/bin/env python

from argparse import SUPPRESS
from basecommand import BaseCommand
from os import getenv
from os.path import exists as pexists
from shutil import copy
import tempfile
import subprocess
import os


from controlfiles import ControlFile, ChangelogFile


class CommandChangelog(BaseCommand):
    key = 'changelog'

    @classmethod
    def build_argparse(cls, subparser):
        parser = subparser.add_parser(cls.key, help='build QPKG')
        parser.add_argument('--' + cls.key, help=SUPPRESS)
        #parser.add_argument('-i', '--increase', action='store_true',
        #                    default=True,
        #                    help='Increase version number and edit it')
        parser.add_argument('-m', '--message', default=None, nargs="*",
                            help='log message')
        parser.add_argument('--custom-version', default=None,
                            help='version')
        parser.add_argument('-q', '--quiet', action="store_true",
                            default=False)

    def append(self, fields):
        pass

    def parse(self, dest='./'):
        return ChangelogFile(dest)

    def run(self):
        #debug(pprint.pformat(self.parse('./QNAP/control').packages))
        control = ControlFile()
        changelog = ChangelogFile()
        kv = {'package_name': control.source['source']}
        if self._args.message is not None:
            kv['messages'] = self._args.message
        if self._args.custom_version is not None:
            kv['version'] = self._args.custom_version
        kv['author'] = getenv('QPKG_NAME')
        kv['email'] = getenv('QPKG_EMAIL')
        entry = changelog.format(**kv)
        fid, filename = tempfile.mkstemp()
        os.close(fid)
        fd = open(filename, "w")
        fd.write(entry)
        if pexists(changelog.filename):
            with open(changelog.filename, 'r') as fread:
                fd.writelines(fread)
        fd.close()

        subprocess.check_call(['sensible-editor', filename])
        if not self._args.quiet and pexists(changelog.filename):
            yn = raw_input('Overwrite ' + changelog.filename + '? (Y/n) ')
            if yn.lower() == 'n':
                return 0
        copy(filename, changelog.filename)
        return 0


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
