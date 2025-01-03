# ansible-gpg
[![Static Badge](https://img.shields.io/badge/Ansible_galaxy-Download-blue)](https://galaxy.ansible.com/ui/standalone/roles/compscidr/gpg/)
[![ansible lint](https://github.com/compscidr/ansible-gpg/actions/workflows/check.yml/badge.svg)](https://github.com/compscidr/ansible-gpg/actions/workflows/check.yml)
[![ansible lint rules](https://img.shields.io/badge/Ansible--lint-rules%20table-blue.svg)](https://ansible.readthedocs.io/projects/lint/rules/)

Ansible module to import and remove GPG-keys using keybase.io or files.

Based on the work by [Brandon Kalinowski](https://github.com/brandonkal/ansible-gpg) and [Thelonius Kort](https://github.com/tnt). Updated so that this can be published
to ansible-galaxy.

With this module, managing gpg keys is very simple. Just specify the keybase username and either the key email or key fingerprint. You can also import keys from files.

The ansible fetch_url method is used for secure download of public keys over https.

When using `key_file`, the `key_id` is automatically determined from the file.

In addition to adding keybase.io functionality, this module also now automatically marks added keys as ultimately trusted, enabling the provisioned machine to encrypt files for the imported users.

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

## installation via galaxy:
`ansible-galaxy install compscidr.gpg`

## installation via galaxy / requirements
Add the following to `requirements.yml`
```
roles:
- name: compscidr.gpg
```
Then run
`ansible-galaxy install -r requirements.yml`

## installation via git / requirements
Add the following to your `requirements.yml` file:
```
# from github
- src: https://github.com/compscidr/ansible-gpg
  name: compscidr.gpg
```
Then run
`ansible-galaxy install -r requirements.yml`

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
