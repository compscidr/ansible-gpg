# ansible-gpg

Ansible module to import and remove GPG-keys using keybase.io or files.

Based on the work by [Thelonius Kort](https://github.com/tnt), this was an interesting challenge for a Javascript developer. With this module, managing gpg keys is very simple. Just specify the keybase username and either the key email or key fingerprint. You can also import keys from files.

The ansible fetch_url method is used for secure download of public keys over https.

In addition to adding keybase.io functionality, this module also now automatically marks added keys as ultimately trusted, enabling the provisioned machine to encrypt files for the imported users.

See my four part encryption series for more on how Keybase improves on the GPG standard:

https://brandonkalinowski.com/tag/encryption/

## Example Playbook

```YAML
---
- name: GPG Module Examples
  hosts: vagrant
  gather_facts: false
  tasks:

  - name: Import GPG key from keybase
    gpg:
      keybase_user: brandonkal
      state: present
      key_id: F33344CEF855F4FE4C2C55820E9D2E07D3D89BDD
      # Key ID can be fingerprint as above or email address
    tags:
      - keybase

  - name: Import Fake Keybase key | Fails
    gpg:
      keybase_user: jijd
      state: present
    tags:
      - fake

  - name: Copy GPG File
    copy:
      src: publickey.asc
      dest: publickey.asc
    tags:
      - file

  - name: Import Public GPG Key from file
    gpg:
      key_file: publickey.asc
      key_id: you@email.com
    tags:
      - file

  - name: Import Private GPG Key from file
    gpg:
      key_file: privatekey.asc
      key_id: you@email.com
      key_type: private
      state: latest
    tags:
      - private

  - name: Remove GPG Key
    gpg:
      key_id: you@email.com
      state: absent
```

### Options

| name         |   default    | description                                                                                                                             |
| ------------ | :----------: | --------------------------------------------------------------------------------------------------------------------------------------- |
| keybase_user |     null     | The Username to fetch on Keybase. The module will download https://keybase.io/<keybase_user>/pgp_keys.asc automatically when specified. |
| key_id       |     null     | The id of the key to be fetched and imported. Only applicable to public keys. Either key_file or key_id is required.                    |
| key_file     |     null     | Filename of key to be imported. Must be on remote machine, not local. Either key_file or key_id is required.                            |
| key_type     |   'public'   | What type of key to import. Only applicable to key_file                                                                                 |
| bin_path     | /usr/bin/gpg | Location of remote gpg binary                                                                                                           |
| state        |  'present'   | Desired state 'present', 'latest', or 'absent'                                                                                          |

[Strange behaviors](https://gist.github.com/tnt/eedaed9a6cc75130b9cb) occur when used with [insane keys](https://gist.github.com/tnt/70b116c72be11dc3cc66). But this is a gpg-problem.

### Usage

Simply copy `gpg.py` to `playbook_dir/library/gpg.py` or clone the repository and add the path to the library via `ansible.cfg` or the environment variable.

# License

MIT License:

Copyright 2018 Brandon Kalinowski

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
