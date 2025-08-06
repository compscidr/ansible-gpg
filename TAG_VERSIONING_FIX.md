# Fix for Ansible Galaxy Version Comparison Issue

## Problem Description

Ansible Galaxy cannot install this role without explicitly specifying a version due to incompatible version formats:

```
[WARNING]: - compscidr.gpg was NOT installed successfully: Unable to compare role versions (0.0.1, 0.0.2, 0.0.3, 0.0.4, 0.0.5, 0.0.6, 0.0.7, v0.0.8, 0.0.9, 0.0.10, 0.0.11) to determine
the most recent version due to incompatible version formats. Please contact the role author to resolve versioning conflicts, or specify an explicit role version to install.
```

## Root Cause

The issue is caused by inconsistent tag naming:
- Most tags follow the pattern: `0.0.1`, `0.0.2`, `0.0.3`, etc. (without "v" prefix)
- One problematic tag: `v0.0.8` (with "v" prefix)

This inconsistency prevents Ansible Galaxy from properly comparing versions to determine the latest release.

## Analysis

- Both `v0.0.8` and `0.0.9` point to the same commit: `10573e764a2c33470e22e017c8cf540cf02ca502`
- The `v0.0.8` tag was likely created when a release was made from a branch named `v0.0.8` instead of `0.0.8`
- Since both tags reference the same commit, the `v0.0.8` tag is redundant

## Solution

**Option 1: Automated Fix (Recommended)**

Run the provided script:
```bash
./fix-tag-versioning.sh
```

**Option 2: Manual Fix**

1. Verify the tags point to the same commit:
   ```bash
   git show v0.0.8 --no-patch --format="%H %s"
   git show 0.0.9 --no-patch --format="%H %s"
   ```

2. Delete the problematic tag:
   ```bash
   # Delete from remote repository
   git push --delete origin v0.0.8
   
   # Delete from local repository  
   git tag --delete v0.0.8
   ```

3. Verify the fix:
   ```bash
   git tag --list --sort=-version:refname
   ```

## Expected Result

After applying the fix:
- All tags will follow the consistent `x.y.z` format
- Version sorting will work correctly: `0.0.11` → `0.0.10` → `0.0.9` → `0.0.7` → ...
- Ansible Galaxy will be able to determine the most recent version automatically

## Testing the Fix

You can test that the fix works by installing the role without specifying a version:

```yaml
# Before fix (fails):
roles:
  - name: compscidr.gpg

# After fix (should work):
roles:
  - name: compscidr.gpg  # Will automatically use latest version
```

Or explicitly test version resolution:
```bash
ansible-galaxy role install compscidr.gpg
```

## Prevention

To prevent this issue in the future:
- Always use consistent tag naming (e.g., `x.y.z` without prefixes)
- Create releases from branches named with the same format as the desired tag
- Use GitHub's release interface which typically handles tag creation consistently