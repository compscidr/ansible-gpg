#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# © Adapted for Keybase.io and style by Brandon Kalinowski
# © Original Code by Thelonius Kort - MIT License

import re
import string
from ansible.module_utils.basic import *
from ansible.module_utils.urls import fetch_url

DOCUMENTATION = '''
---
module: gpg
version_added: 2.0
short_description:  Manages import and removal of GPG-keys
description:
     - Imports, refreshes, and deletes GnuPG keys. Just specify the keybase
       username and either the key email or key fingerprint.
       You can also import keys from files.
options:
  keybase_user:
    description:
      - The Username to fetch on Keybase. The module will download
        https://keybase.io/<keybase_user>/pgp_keys.asc automatically when specified.
  key_id:
    description:
      - The id of the key to be fetched and imported.
        Only applicable to public keys. Either key_file or key_id is required.
    required: false
    default: null
  key_file:
    description:
      - Filename of key to be imported. Must be on remote machine, not local.
        Either key_file or key_id is required.
        Can also be used with delete, module will extract the fingerprint from the provided key file and
        delete the matching key from the key-chain.
    required: false
    default: null
  key_type:
    description:
      - What type of key to import. Only applicable to key_file
    required: true
    choices: [ "private", "public" ]
    default: "public"
  bin_path:
    description:
      - "Location of GPG binary"
    require: false
    default: /usr/bin/gpg
  state:
    description:
      - Whether to import (C(present), C(latest)), or remove (C(absent)) a key.
    required: false
    choices: [ "present", "latest", "absent" ]
    default: "present"
notes: []
requirements: [ gpg ]
author: Brandon Kalinowski
'''

EXAMPLES = '''
- name: Import GPG key from keybase
    gpg:
      keybase_user: brandonkal
      state: present
      key_id: F33344CEF855F4FE4C2C55820E9D2E07D3D89BDD
      # Key ID can be fingerprint as above or email address

- name: Import Public GPG Key from file
    gpg:
      key_file: publickey.asc
      key_id: you@email.com

- name: Remove GPG Key
    gpg:
      keybase_user: gpgtools
      key_id: team@gpgtools.com
      state: absent
'''


class SafeDict(dict):
    def __missing__(self, key):
        return '{' + key + '}'


# http://stackoverflow.com/a/33621609/659298
class SafeFormatter(string.Formatter):
    def __init__(self, default='{{{0}}}'):
        self.default = default

    def get_value(self, key, args, kwds):
        if isinstance(key, str):
            return kwds.get(key, self.default.format(key))
        string.Formatter.get_value(key, args, kwds)


class GpgImport(object):

    def __init__(self, module):
        self.m = module
        self.debuglist = []
        self._setup_creds()
        self._execute_task()

    def _debug(self, msg):
        # named 'debuglist' to avoid 'self.debug()' attempting to work.
        self.debuglist.append(msg)

    def trust_all(self):
        self._debug('Checking Trust')
        res = self._execute_command('check-trust')
        self._debug('check trust: %s' % (str(res['stdout'])))
        gpg_output = res['stdout']
        pattern = re.findall('fpr:::::::::([0-9A-F]+):', gpg_output)
        # Create list with all keys marked as trusted:
        trusted = ":6:\n".join(pattern) + ":6:"
        res = self._execute_command('import-trust', data=trusted)
        self._debug('import trust: %s' % (str(res['stdout'])))

    def get_keybase(self):
        url = 'https://keybase.io/' + self.m.params["keybase_user"] + '/pgp_keys.asc'
        rsp, info = fetch_url(self.m, url=url, timeout=10, method='GET')

        # Check for errors first
        # Exceptions in fetch_url may result in a status -1, ensure error in all cases.
        if info['status'] == -1:
            self.m.fail_json(msg=info['msg'], url=url)

        elif info['status'] != 200:
            self.m.fail_json(
                msg="Request failed",
                status_code=info['status'],
                response=info['msg'], url=url
            )
        else:
            # Required for python3
            remote_key = to_native(rsp.read())
            return remote_key

    def _execute_task(self):
        key_present = False

        if self.keybase_user:
            if self.key_id:
                res = self._execute_command('check')
                self._debug('keybase check: %s' % (str(res)))
                key_present = res['rc'] == 0
                self.changed = False
            else:
                self.m.fail_json(msg='key_id is required when keybase_user is defined!')

        if self.key_file:
            filekey = self._get_key_from_file()
            if self.key_type == 'public' and filekey:
                # rerun the original setup with this key in the commands
                self._setup_creds(filekey)
                res = self._execute_command('check-public')
                self._debug('checkpublic: %s' % (str(res)))
                key_present = res['rc'] == 0

            elif self.key_type == 'private' and filekey:
                # rerun the original setup with this key in the commands
                self._setup_creds(filekey)
                res = self._execute_command('check-private')
                self._debug('checkprivate: %s' % (str(res)))
                key_present = res['rc'] == 0

        if key_present and self.state == 'absent':
            res = self._execute_command('delete')
            self.changed = res['rc'] == 0
        elif key_present and self.state == 'latest' and self.keybase_user:
            res = self._execute_command('keybase', data=self.get_keybase())
            self.changed = re.search('gpg:\s+unchanged: 1\n', res['stderr']) is None
        elif not key_present and self.state in ('present', 'latest'):
            if self.key_type == 'private' and self.key_file:
                self._debug('importing private key file')
                res = self._execute_command('import-key')
            elif self.keybase_user:
                self._debug('importing Keybase public keys for ' + self.keybase_user)
                res = self._execute_command('keybase', data=self.get_keybase())
            elif self.key_type == 'public':
                self._debug('importing public key file')
                res = self._execute_command('import-key')
            self.changed = res['rc'] == 0
        else:
            self.changed = False
            res = {'rc': 0}

        if res['rc'] != 0:
            self._debug(res)
            self.m.fail_json(msg=self.log_dic, debug=self.debuglist)

        # Check if a change has occurred and mark all keys as trusted
        if self.changed and self.state != 'absent':
            self.trust_all()

    def _setup_creds(self, key_override=None):
        for k, v in self.m.params.items():
            setattr(self, k, v)
        if key_override:
            self.key_id = key_override

        self.commands = {
            'check':   '{bin_path} {check_mode} --list-keys {key_id}',
            'delete':  '{bin_path} {check_mode} --batch --yes --delete-secret-and-public-keys {key_id}',
            'check-private':  '{bin_path} {check_mode} --list-secret-keys {key_id}',
            'check-public':  '{bin_path} {check_mode} --list-public-keys {key_id}',
            'import-key': '{bin_path} {check_mode} --batch --fast-import {key_file}',
            'keybase': '{bin_path} {check_mode} --batch --fast-import',
            'check-trust': '{bin_path} {check_mode} --list-keys --fingerprint --with-colons',
            'import-trust': '{bin_path} {check_mode} --fast-ownertrust',
        }
        command_data = {
            'check_mode': '--dry-run' if self.m.check_mode else '',
            'bin_path': self.m.get_bin_path(self.bin_path, True),
            'key_id': self.key_id,
            'key_file': self.key_file
        }
        # sort of a brilliant way of late-binding/double-formatting given here:
        # http://stackoverflow.com/a/17215533/659298
        for c, l in self.commands.items():
            sf = SafeFormatter()
            self.commands[c] = sf.format(l, **command_data)
        self._debug('set up commands: %s' % (str(self.commands)))

    def _execute_command(self, cmd, data=''):
        self._debug('command: %s' % (str(self.commands[cmd])))
        if data:
            raw_res = self.m.run_command(self.commands[cmd], data=data)
        else:
            raw_res = self.m.run_command(self.commands[cmd])
        return self._legiblify(cmd, raw_res)

    def _legiblify(self, sec, res):
        """turn tuple to dict and preserve it for debugging"""
        if not hasattr(self, 'log_dic'):
            self.log_dic = {}
        rdic = dict([k, res[i]] for i, k in enumerate(('rc', 'stdout', 'stderr')))
        return rdic

    def _get_key_from_file(self):
        keycmd = '%s --with-colons --with-fingerprint %s'
        bp = self.m.get_bin_path(self.bin_path, True)
        print(bp, self.key_file)
        keycmd_expanded = keycmd % (bp, self.key_file)
        self.changed = False
        raw_res = self.m.run_command(keycmd_expanded)
        keyinfo = raw_res[1]
        self._debug('keyinfo: %s' % (str(keyinfo)))
        keysearch = re.search(r'fpr:{9}([0-9A-F]{40}):', keyinfo, re.MULTILINE)

        if keysearch and keysearch.group(1):
            self._debug('keysearch groups: %s' % (str(keysearch.groups())))
            return keysearch.group(1)
        return None


def main():
    module = AnsibleModule(
        argument_spec=dict(
            keybase_user=dict(type='str'),
            key_id=dict(required=False, type='str'),
            key_type=dict(default='public', choices=['private', 'public']),
            key_file=dict(required=False, type='str'),
            bin_path=dict(default='/usr/bin/gpg', type='str'),
            state=dict(default='present', choices=['latest', 'absent', 'present']),
        ),
        supports_check_mode=True,
        required_one_of=[['keybase_user', 'key_file']],
    )

    gkm = GpgImport(module)

    result = {
        'log_dic': gkm.log_dic,
        'changed': gkm.changed,
        'debug': gkm.debuglist,
    }

    module.exit_json(**result)


main()
