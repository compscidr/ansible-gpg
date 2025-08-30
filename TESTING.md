# Molecule Testing

This repository uses [Molecule](https://molecule.readthedocs.io/) for testing the Ansible role functionality.

## What is Molecule?

Molecule is a testing framework designed to aid in the development and testing of Ansible roles. It provides support for testing with multiple instances, operating systems and distributions, virtualization providers, test frameworks and testing scenarios.

## Test Structure

The molecule tests are located in the `molecule/` directory with the following structure:

```
molecule/
└── default/
    ├── molecule.yml     # Configuration for the test scenario
    ├── converge.yml     # Playbook that tests the role
    └── verify.yml       # Validation tests
```

### Test Scenarios

- **default**: Basic functionality test that verifies:
  - The role can be included without errors
  - GPG is installed in the test environment
  - Role structure is correct (tasks, meta files exist)
  - Test key file handling

## Running Tests Locally

### Prerequisites

1. Install Python dependencies:
```bash
pip install molecule[docker] molecule-docker ansible-lint
```

2. Ensure Docker is running (for containerized tests)

### Run Tests

```bash
# Run all molecule tests
molecule test

# Run syntax check only
molecule syntax

# Run just the converge step (useful for development)
molecule converge

# Run verification tests
molecule verify

# List available scenarios
molecule list
```

## Continuous Integration

The molecule tests run automatically in GitHub Actions on:
- Every push to main branch
- Every pull request
- Weekly schedule (to catch regressions)

See `.github/workflows/molecule.yml` for the CI configuration.

## Test Environment

The tests run in a Ubuntu 20.04 Docker container with:
- GPG installed for testing GPG operations
- Basic system packages required by the role

## Extending Tests

To add new test scenarios:

1. Create a new directory under `molecule/` (e.g., `molecule/custom-scenario/`)
2. Add the required files (`molecule.yml`, `converge.yml`, `verify.yml`)
3. Update the GitHub Actions workflow to include the new scenario

To modify existing tests:
- Edit `converge.yml` to test different role configurations
- Edit `verify.yml` to add new validation checks
- Edit `molecule.yml` to change test environment settings