# Contributing to BluOS Integration

Thank you for your interest in contributing to the BluOS Home Assistant integration! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## How to Contribute

### Reporting Bugs

Before creating a bug report:
1. Check the existing issues to avoid duplicates
2. Verify you're using the latest version
3. Test with the latest Home Assistant version

When creating a bug report, include:
- Home Assistant version
- BluOS integration version
- BluOS device model and firmware version
- Detailed steps to reproduce
- Expected vs actual behavior
- Relevant logs (enable debug logging)
- Screenshots if applicable

### Suggesting Enhancements

Enhancement suggestions are welcome! Please:
1. Check existing feature requests first
2. Provide a clear use case
3. Explain why this would be useful to others
4. Consider implementation complexity

### Pull Requests

1. **Fork the Repository**
   ```bash
   git clone https://github.com/pimlo/bluos.git
   cd bluos
   ```

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

3. **Make Your Changes**
   - Follow the existing code style
   - Add comments for complex logic
   - Update documentation if needed
   - Test your changes thoroughly

4. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```

5. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Provide a clear description
   - Reference any related issues
   - Explain what you changed and why

## Development Setup

### Prerequisites

- Home Assistant development environment
- BluOS device for testing
- Python 3.11 or later
- Git

### Local Development

1. **Clone the Repository**
   ```bash
   git clone https://github.com/pimlo/bluos.git
   ```

2. **Copy to Home Assistant**
   ```bash
   cp -r custom_components/bluos /path/to/homeassistant/config/custom_components/
   ```

3. **Enable Debug Logging**
   Add to `configuration.yaml`:
   ```yaml
   logger:
     default: info
     logs:
       custom_components.bluos: debug
   ```

4. **Restart Home Assistant**
   ```bash
   ha core restart
   ```

5. **Check Logs**
   ```bash
   tail -f /config/home-assistant.log | grep bluos
   ```

## Code Style

### Python

- Follow PEP 8 style guide
- Use type hints where possible
- Maximum line length: 88 characters (Black formatter)
- Use meaningful variable and function names
- Add docstrings to all functions and classes

### Example

```python
"""Module description."""
from typing import Any

def example_function(param: str) -> dict[str, Any]:
    """
    Brief description of function.
    
    Args:
        param: Description of parameter
        
    Returns:
        Description of return value
    """
    return {"result": param}
```

### Imports

Order imports as follows:
1. Standard library
2. Third-party libraries
3. Home Assistant imports
4. Local imports

```python
import logging
from typing import Any

import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN
```

## Testing

### Manual Testing

Before submitting a PR, test:
1. Installation (fresh install)
2. Configuration (config flow)
3. All media player controls
4. Grouping/ungrouping
5. Multiple devices
6. Error scenarios
7. Removal of integration

### Test Scenarios

- [ ] Invalid IP address
- [ ] Unreachable device
- [ ] Network timeout
- [ ] Device powered off
- [ ] Firmware incompatibility
- [ ] Multiple simultaneous commands
- [ ] Rapid group/ungroup operations

## Documentation

### When to Update Documentation

Update documentation when:
- Adding new features
- Changing existing behavior
- Fixing bugs that affect usage
- Improving setup process

### Documentation Files

- `README.md` - Main documentation
- `SETUP_GUIDE.md` - Installation instructions
- `EXAMPLES.md` - Usage examples
- `QUICK_REFERENCE.md` - Service reference
- `CHANGELOG.md` - Version history

### Changelog Format

```markdown
## [Version] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes to existing features

### Fixed
- Bug fixes

### Removed
- Removed features
```

## Commit Messages

### Format

```
type(scope): Brief description

Detailed description if needed

Fixes #issue_number
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```
feat(grouping): Add support for stereo pairs

Added ability to configure stereo pairs through the integration.
This allows users to create left/right channel configurations.

Fixes #42
```

```
fix(api): Handle XML parsing errors gracefully

Added try/catch for XML parsing to prevent crashes when
device returns malformed responses.

Fixes #38
```

## Release Process

1. **Update Version**
   - Update `manifest.json` version
   - Update `CHANGELOG.md`

2. **Create Release Branch**
   ```bash
   git checkout -b release/v1.x.x
   ```

3. **Test Thoroughly**
   - Run all manual tests
   - Verify HACS compatibility
   - Check documentation

4. **Merge to Main**
   ```bash
   git checkout main
   git merge release/v1.x.x
   ```

5. **Tag Release**
   ```bash
   git tag -a v1.x.x -m "Release version 1.x.x"
   git push origin v1.x.x
   ```

6. **Create GitHub Release**
   - Go to GitHub releases
   - Create new release from tag
   - Copy changelog content
   - Publish release

## Getting Help

- **Questions**: Open a discussion on GitHub
- **Issues**: Create an issue with details
- **Chat**: (To be set up - Discord/Matrix)

## Recognition

Contributors will be:
- Listed in release notes
- Mentioned in README.md
- Added to GitHub contributors

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to the BluOS integration! 🎵
