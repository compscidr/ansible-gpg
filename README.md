# ansible-gpg

Ansible module to import and remove GPG-keys using keybase.io or files.

Based on the work by [Brandon Kalinowski](https://github.com/brandonkal/ansible-gpg) and [Thelonius Kort](https://github.com/tnt). Updated so that this can be published
to ansible-galaxy.

With this module, managing gpg keys is very simple. Just specify the keybase username and either the key email or key fingerprint. You can also import keys from files.

The ansible fetch_url method is used for secure download of public keys over https.

When using `key_file`, the `key_id` is automatically determined from the file.

In addition to adding keybase.io functionality, this module also now automatically marks added keys as ultimately trusted, enabling the provisioned machine to encrypt files for the imported users.

See my four part encryption series for more on how Keybase improves on the GPG standard:

https://brandonkalinowski.com/tag/encryption/

## Example Playbook

```YAML
---
- name: GPG Module Examples
  hosts: vagrant
  gather_facts: false
  roles:
    - role: compscidr.gpg
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
    tags:
      - file

  - name: Import Private GPG Key from file
    gpg:
      key_file: privatekey.asc
      key_type: private
      state: latest
    tags:
      - private

  - name: Remove GPG Key
    gpg:
      keybase_user: gpgtools
      key_id: team@gpgtools.org
      state: absent
```

### Options

| name         |   default    | description                                                                                                                                                           |
| ------------ | :----------: | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| keybase_user |     null     | The Username to fetch on Keybase. The module will download https://keybase.io/<keybase_user>/pgp_keys.asc automatically when specified. Requires key_id to be defined |
| key_id       |     null     | The id of the key to be fetched and imported. Only applicable to public keys. Either key_file or key_id is required.                                                  |
| key_file     |     null     | Filename of key to be imported. Must be on remote machine, not local. Either key_file or key_id is required.                                                          |
| key_type     |   'public'   | What type of key to import. Only applicable to key_file                                                                                                               |
| bin_path     | /usr/bin/gpg | Location of remote gpg binary                                                                                                                                         |
| state        |  'present'   | Desired state 'present', 'latest', or 'absent'                                                                                                                        |

[Strange behaviors](https://gist.github.com/tnt/eedaed9a6cc75130b9cb) occur when used with [insane keys](https://gist.github.com/tnt/70b116c72be11dc3cc66). But this is a gpg problem.

### Usage

Simply copy `gpg.py` to `playbook_dir/library/gpg.py` or clone the repository and add the path to the library via `ansible.cfg` or the environment variable.
