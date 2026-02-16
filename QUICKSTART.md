# Quick Start Guide

Get started with Visual Automation Tool in 5 minutes!

## Installation

1. **Install Python 3.8+** (if not already installed)

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Install Browser Driver (for web automation):**

For Chrome:
```bash
# Windows
# Download from: https://chromedriver.chromium.org/

# Linux/Mac with pip
pip install webdriver-manager
```

## First Workflow

### Example 1: Simple Web Scraping

1. Run the application:
```bash
python main.py
```

2. Create your first workflow:
   - Drag "Open Browser" from palette to canvas
   - Drag "Navigate to URL" and connect it to Open Browser
   - Double-click "Navigate to URL" and enter: `https://example.com`
   - Drag "Delay" and connect it
   - Drag "Close Browser" and connect it

3. Click "▶️ Run" to execute!

### Example 2: API Testing

1. Drag "GET Request" to canvas
2. Double-click and configure:
   - URL: `https://api.github.com/users/github`
3. Drag "Print/Log" and connect to GET Request
4. Run and check console output

### Example 3: Using Variables

1. Drag "Set Variable" to canvas
   - Variable name: `my_url`
   - Value: `https://example.com`

2. Drag "Get Variable" 
   - Variable name: `my_url`

3. Connect Get Variable → Navigate to URL

## Common Workflows

### Web Form Automation

```
Open Browser → Navigate → Find Element (input field) 
→ Fill Input → Find Element (button) → Click → Delay → Close Browser
```

### API Data Processing

```
GET Request → Parse JSON → Set Variable → Print/Log
```

### Conditional Logic

```
GET Request → If/Else (check status) → Print Success or Print Error
```

## Keyboard Shortcuts

- `Delete` - Remove selected block
- `Ctrl+S` - Save project
- `Ctrl+O` - Open project
- `Ctrl+N` - New project

## Tips

1. **Always close browsers** - Add "Close Browser" at the end of web automation
2. **Use delays wisely** - Add small delays between actions for stability
3. **Validate first** - Use "✓ Validate" before running complex workflows
4. **Save frequently** - Use "💾 Save" to avoid losing work
5. **Check logs** - View `automation_tool.log` for detailed execution info

## Troubleshooting

**Problem**: Blocks won't connect
- **Solution**: Ensure output and input port types match

**Problem**: Browser automation fails
- **Solution**: Install ChromeDriver and ensure Chrome is installed

**Problem**: "Element not found" error
- **Solution**: Increase timeout parameter or verify selector

**Problem**: JSON parse error
- **Solution**: Verify API returns valid JSON format

## Next Steps

- Read [DEVELOPMENT.md](DEVELOPMENT.md) to create custom blocks
- Check [examples/](examples/) folder for sample workflows
- Explore advanced features in README.md

## Getting Help

- Check the log file: `automation_tool.log`
- Review block descriptions in the palette
- Use "❓ Help" menu in the application

Happy automating! 🎉
