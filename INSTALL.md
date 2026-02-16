# Installation Guide

## Quick Start (3 Steps)

### Step 1: Install Python
Ensure you have Python 3.8 or higher installed:

```bash
python --version
# Should show: Python 3.8.x or higher
```

If not installed, download from: https://www.python.org/downloads/

### Step 2: Install Dependencies

Navigate to the project directory and run:

```bash
pip install -r requirements.txt
```

**Note**: This will install all required packages:
- customtkinter (GUI framework)
- selenium (web automation)
- requests (HTTP requests)
- beautifulsoup4 (HTML parsing)
- pandas (data processing)
- And more...

### Step 3: Run the Application

```bash
python main.py
```

## Alternative: Demo Mode

If you want to test the core functionality without installing all dependencies:

```bash
python demo.py
```

This runs a limited version with basic blocks to verify the engine works.

## Detailed Installation

### Windows Installation

1. **Install Python**:
   - Download from python.org
   - During installation, check "Add Python to PATH"

2. **Install dependencies**:
   ```cmd
   pip install -r requirements.txt
   ```

3. **Install ChromeDriver** (for web automation):
   ```cmd
   pip install webdriver-manager
   ```
   Or download manually from: https://chromedriver.chromium.org/

4. **Run**:
   ```cmd
   python main.py
   ```

### Linux/Mac Installation

1. **Install Python** (usually pre-installed):
   ```bash
   python3 --version
   ```

2. **Create virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Mac/Linux
   # venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run**:
   ```bash
   python main.py
   ```

## Troubleshooting

### Issue: "No module named 'customtkinter'"

**Solution**:
```bash
pip install customtkinter
```

### Issue: "No module named 'selenium'"

**Solution**:
```bash
pip install selenium webdriver-manager
```

### Issue: "tkinter module not found"

**Solution** (Linux):
```bash
sudo apt-get install python3-tk
```

**Solution** (Mac):
```bash
brew install python-tk
```

### Issue: ChromeDriver errors

**Solution 1**: Install webdriver-manager
```bash
pip install webdriver-manager
```

**Solution 2**: Update Chrome browser to latest version

**Solution 3**: Manually install ChromeDriver
- Download from: https://chromedriver.chromium.org/
- Place in system PATH

### Issue: GUI doesn't appear

**Possible causes**:
1. **No display environment**: 
   - Are you running on a server without GUI?
   - Try running on a machine with display

2. **tkinter not installed**:
   ```bash
   # Test tkinter
   python -c "import tkinter"
   ```

3. **CustomTkinter issue**:
   ```bash
   pip install --upgrade customtkinter
   ```

### Issue: Import errors

**Solution**: Ensure you're in the project directory
```bash
cd visual_automation_tool
python main.py
```

### Issue: Permission denied

**Solution** (Linux/Mac):
```bash
chmod +x main.py
python main.py
```

## Dependency Installation by Component

### Core Requirements (Minimal)
```bash
pip install customtkinter pillow
```

### Web Automation
```bash
pip install selenium webdriver-manager
```

### HTTP/API Testing
```bash
pip install requests urllib3
```

### Data Processing
```bash
pip install pandas beautifulsoup4 lxml
```

### All Dependencies
```bash
pip install -r requirements.txt
```

## Verification

Test that everything is installed correctly:

```bash
python -c "import customtkinter; import selenium; import requests; print('✓ All dependencies installed!')"
```

## Running Without Installation

If you can't install dependencies, you can still explore the code:

1. **View the architecture**:
   ```bash
   cat ARCHITECTURE.md
   ```

2. **Read the code**:
   ```bash
   # Core engine
   cat core/block_engine.py
   
   # GUI
   cat gui/main_window.py
   
   # Blocks
   cat blocks/web_automation.py
   ```

3. **Run demo mode** (limited dependencies):
   ```bash
   python demo.py
   ```

## Docker Installation (Advanced)

Create a Dockerfile:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3-tk \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

CMD ["python", "main.py"]
```

Build and run:
```bash
docker build -t visual-automation-tool .
docker run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix visual-automation-tool
```

## Development Setup

For development with hot-reload and testing:

1. **Install dev dependencies**:
   ```bash
   pip install pytest pytest-cov black flake8
   ```

2. **Run tests**:
   ```bash
   pytest tests/
   ```

3. **Code formatting**:
   ```bash
   black .
   ```

4. **Linting**:
   ```bash
   flake8 .
   ```

## Virtual Environment (Recommended)

Using a virtual environment keeps dependencies isolated:

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py

# Deactivate when done
deactivate
```

## Package as Executable (Optional)

To create a standalone executable:

```bash
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile --windowed main.py

# Executable will be in dist/ folder
```

## Network/Proxy Issues

If you're behind a proxy:

```bash
pip install --proxy=http://user:password@proxy:port -r requirements.txt
```

Or set environment variables:
```bash
export HTTP_PROXY="http://proxy:port"
export HTTPS_PROXY="https://proxy:port"
```

## Minimum System Requirements

- **OS**: Windows 7+, macOS 10.12+, Linux (any modern distro)
- **RAM**: 512MB minimum, 2GB recommended
- **Disk**: 200MB for application + dependencies
- **Display**: Any resolution (1920x1080 recommended)
- **Python**: 3.8 or higher

## Getting Help

If you encounter issues:

1. **Check the log file**: `automation_tool.log`
2. **Read error messages carefully**
3. **Verify Python version**: `python --version`
4. **Check installed packages**: `pip list`
5. **Try demo mode**: `python demo.py`

## Success Indicators

You'll know installation succeeded when:

1. ✓ No errors during `pip install`
2. ✓ `python main.py` shows the banner
3. ✓ GUI window appears
4. ✓ Block palette shows available blocks
5. ✓ Can drag blocks to canvas

## Next Steps

After successful installation:

1. Read [QUICKSTART.md](QUICKSTART.md)
2. Try the sample workflow in `examples/`
3. Create your first automation
4. Explore the documentation

Happy automating! 🚀
