# Setup Guide

This guide provides detailed setup instructions for the IFT-LLM framework.

## System Requirements

- **Operating System**: Linux, macOS, or Windows (with WSL recommended)
- **Python**: 3.8 or higher
- **Memory**: At least 4GB RAM recommended
- **Disk Space**: ~500MB for framework + benchmarks

## Step-by-Step Installation

### 1. Install System Dependencies

#### Yosys (Required)

Yosys is used for Verilog parsing and module hierarchy extraction.

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install yosys
```

**macOS:**
```bash
brew install yosys
```

**From Source:**
```bash
git clone https://github.com/YosysHQ/yosys.git
cd yosys
make
sudo make install
```

Verify installation:
```bash
yosys -V
```

### 2. Python Environment Setup

#### Create Virtual Environment

```bash
# Navigate to project directory
cd ift_llm_final

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows
```

#### Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. API Configuration

The framework supports multiple LLM providers. Choose one and configure accordingly.

#### Option A: Azure OpenAI

1. Obtain API credentials from Azure Portal:
   - API Key
   - Endpoint URL
   - Deployment name

2. Create configuration file:
   ```bash
   cp configs/azure_config_template.env .env
   ```

3. Edit `.env`:
   ```bash
   AZURE_OPENAI_API_KEY=your_actual_api_key
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   OPENAI_API_TYPE=azure
   OPENAI_API_VERSION=2024-02-01
   ```

4. Load environment variables:
   ```bash
   export $(cat .env | xargs)
   ```

#### Option B: OpenRouter

1. Get API key from [OpenRouter](https://openrouter.ai/)

2. Create configuration file:
   ```bash
   cp configs/openrouter_config_template.env .env
   ```

3. Edit `.env`:
   ```bash
   OPENROUTER_API_KEY=your_actual_api_key
   OPENROUTER_API_BASE=https://openrouter.ai/api/v1
   ```

4. Load environment variables:
   ```bash
   export $(cat .env | xargs)
   ```

### 4. Verify Installation

Run a simple test:

```bash
# Test Python imports
python -c "from src.core.analyzer import HardwareIFTAnalyzer; print('✓ Imports successful')"

# Test Yosys
yosys -p "help" > /dev/null 2>&1 && echo "✓ Yosys working"

# Check environment variables
python -c "import os; print('✓ API configured' if os.getenv('AZURE_OPENAI_API_KEY') or os.getenv('OPENROUTER_API_KEY') else '✗ API not configured')"
```

### 5. Run Your First Analysis

Try analyzing a sample design:

```bash
# If you have benchmarks available
python examples/analyze_design.py \
    ../automate/sequential \
    counter_module \
    --label true \
    --output test_result.json
```

## Troubleshooting

### Common Issues

#### 1. Yosys not found

**Error**: `yosys: command not found`

**Solution**: 
- Verify Yosys is installed: `which yosys`
- Check PATH: `echo $PATH`
- Reinstall Yosys or add to PATH

#### 2. Import errors

**Error**: `ModuleNotFoundError: No module named 'langchain_openai'`

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### 3. API authentication errors

**Error**: `AuthenticationError` or `Invalid API key`

**Solution**:
- Verify API key in `.env` file
- Ensure environment variables are loaded: `echo $AZURE_OPENAI_API_KEY`
- Re-export variables: `export $(cat .env | xargs)`

#### 4. Yosys parsing errors

**Error**: `ERROR: Yosys failed to parse Verilog`

**Solution**:
- Check Verilog syntax
- Ensure all included files are present
- Try analyzing a simpler design first

### Platform-Specific Notes

#### Windows

- Use WSL (Windows Subsystem for Linux) for best compatibility
- If using native Windows, install Yosys from source or use pre-built binaries
- Use PowerShell or Git Bash for commands

#### macOS

- Install Homebrew if not already installed
- Use `python3` explicitly instead of `python`
- May need to install Xcode Command Line Tools

## Advanced Configuration

### Custom LLM Parameters

Modify analyzer initialization:

```python
analyzer = HardwareIFTAnalyzer(
    llm_provider="azure",
    model="gpt-4",          # or "gpt-4o", "gpt-3.5-turbo"
    temperature=0.2         # 0.0 = deterministic, 1.0 = creative
)
```

### Environment Variables

Additional optional variables:

```bash
# Timeout for LLM requests (seconds)
export LLM_TIMEOUT=300

# Maximum retries for failed requests
export LLM_MAX_RETRIES=3

# Enable debug logging
export DEBUG=true
```

## Next Steps

- Read the [Usage Guide](USAGE.md) for detailed examples
- Explore [IFT Techniques](IFT_TECHNIQUES.md) for methodology details
- Check [API Reference](API_REFERENCE.md) for programmatic usage

## Getting Help

If you encounter issues:

1. Check this troubleshooting section
2. Review the [FAQ](FAQ.md)
3. Search existing issues on GitHub
4. Open a new issue with:
   - Error messages
   - Your environment (OS, Python version, etc.)
   - Steps to reproduce

