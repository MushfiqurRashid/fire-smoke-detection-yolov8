# Contributing to Fire and Smoke Detection System

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites
- Python 3.11+
- Git
- Virtual environment setup

### Setup Development Environment

1. **Fork the Repository**
   ```bash
   # Click the Fork button on GitHub
   ```

2. **Clone Your Fork**
   ```bash
   git clone https://github.com/yourusername/fire-smoke-detection-yolov8.git
   cd fire-smoke-detection-yolov8
   ```

3. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\Activate.ps1
   ```

4. **Install Development Dependencies**
   ```bash
   pip install -e ".[dev]"
   pip install pytest pytest-cov black flake8 isort mypy
   ```

## Development Workflow

### Creating a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### Code Style Guidelines

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

#### Formatting
```bash
# Format code with Black
black .

# Sort imports with isort
isort .

# Check style with flake8
flake8 . --max-line-length=100
```

#### Type Hints
Always include type hints for function parameters and return types:

```python
def detect_fire(image: np.ndarray, confidence: float = 0.60) -> Dict[str, Any]:
    """Detect fire in image."""
    pass
```

#### Docstrings
Use Google-style docstrings:

```python
def predict(self, image_path: str) -> Dict:
    """
    Run prediction on image.
    
    Args:
        image_path: Path to image file
        
    Returns:
        Detection results with detections and alerts
        
    Raises:
        FileNotFoundError: If image not found
        ValueError: If image format invalid
    """
    pass
```

### Testing

#### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov=app --cov-report=html

# Run specific test file
pytest tests/test_config.py -v

# Run specific test
pytest tests/test_config.py::test_config_default -v
```

#### Writing Tests

```python
import pytest
from src.config import Config

def test_config_loads():
    """Test config loading."""
    config = Config()
    assert config.get("dataset.path") == "./data"

@pytest.fixture
def sample_image():
    """Create sample test image."""
    return Image.new('RGB', (640, 640))

def test_detection(sample_image):
    """Test detection on sample image."""
    predictor = FireSmokePredictor()
    result = predictor.predict_image(sample_image)
    assert result["status"] == "success"
```

### Commit Messages

Follow conventional commit format:

```
feat: add new feature description
fix: fix bug description
docs: update documentation
style: format code
refactor: refactor code structure
test: add or update tests
chore: update dependencies
```

Examples:
```bash
git commit -m "feat: add confidence calibration for fire detection"
git commit -m "fix: resolve webcam streaming lag in streamlit app"
git commit -m "docs: update API endpoint documentation"
```

### Pull Request Process

1. **Update Your Branch**
   ```bash
   git pull origin main
   git rebase main
   ```

2. **Push Your Changes**
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create Pull Request**
   - Go to GitHub and create PR from your fork to main repository
   - Fill in the PR template with description of changes
   - Reference any related issues (#123)

4. **PR Requirements**
   - [ ] Code follows style guidelines
   - [ ] Tests pass locally and in CI
   - [ ] New tests added for new functionality
   - [ ] Documentation updated
   - [ ] No merge conflicts

## Areas for Contribution

### High Priority
- [ ] Improve model accuracy (mAP > 0.90)
- [ ] Add multi-modal detection (thermal + RGB)
- [ ] Optimize inference speed
- [ ] Add mobile app support
- [ ] Implement SMS/Email alerts

### Medium Priority
- [ ] Add more comprehensive logging
- [ ] Improve error handling
- [ ] Add performance benchmarks
- [ ] Create tutorials and guides
- [ ] Add example datasets

### Documentation
- Update README with new features
- Add API documentation examples
- Create troubleshooting guides
- Write deployment guides
- Add tutorial notebooks

## Reporting Issues

When reporting bugs, include:

1. **Description**: Clear description of the issue
2. **Steps to Reproduce**: Steps to reproduce the problem
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Environment**: OS, Python version, installed packages
6. **Screenshots**: If applicable

## Code Review Process

- Code will be reviewed for:
  - Correctness and logic
  - Code quality and style
  - Test coverage
  - Documentation completeness
  - Performance implications

- Feedback will be provided constructively
- Multiple rounds of review may be needed

## Community Guidelines

- Be respectful and inclusive
- Provide constructive feedback
- Help others in the community
- Share knowledge and learnings
- Report issues responsibly

## Legal

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

- Open an issue for questions
- Start a discussion for feature ideas
- Contact maintainers for other inquiries

---

**Thank you for contributing to making fire detection systems better!** 🔥
