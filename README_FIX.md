# Quick Fix for Ansible Galaxy Issue

## 🎯 Quick Solution

**Run this single command to fix the issue:**

```bash
./fix-tag-versioning.sh
```

## 📝 What This Fixes

Your Ansible role shows this error when users try to install it:

```
[WARNING]: - compscidr.gpg was NOT installed successfully: Unable to compare role versions 
(0.0.1, 0.0.2, 0.0.3, 0.0.4, 0.0.5, 0.0.6, 0.0.7, v0.0.8, 0.0.9, 0.0.10, 0.0.11) 
to determine the most recent version due to incompatible version formats.
```

**Problem:** One tag has a different format (`v0.0.8` vs `0.0.8`)  
**Solution:** Remove the inconsistent tag  
**Result:** Users can install your role without specifying a version

## ✅ After Running the Fix

Users will be able to do:
```yaml
# This will work instead of failing
roles:
  - name: compscidr.gpg
```

For more details, see [TAG_VERSIONING_FIX.md](TAG_VERSIONING_FIX.md)