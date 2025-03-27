Here's a comprehensive `README.md` for your IP Information Fetcher application, tailored for DPhish:

```markdown
# IP Information Fetcher

https://dphish.com/

*Network Intelligence Tool by DPhish*

## Overview

A Python-based tool that fetches detailed information about IP addresses using the ipinfo.io API. Designed for security analysts and network administrators at DPhish to quickly gather intelligence about IP addresses.

## Features

- Batch processing of multiple IP addresses
- Detailed error logging and reporting
- Rate-limited concurrent requests
- Clean command-line interface
- Comprehensive logging

## Requirements

- Python 3.8+
- pip package manager

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/dphish/ip-info-fetcher.git
cd ip-info-fetcher
```

### 2. Create and activate virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate  # Linux/MacOS
.\venv\Scripts\activate   # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the project root:

```bash
echo "API_TOKEN=your_ipinfo_token_here" > .env
```

## Usage

```bash
python ip_info_fetcher.py
```

### Command Examples

- Lookup single IP:
  ```
  > 8.8.8.8
  ```

- Lookup multiple IPs (comma or space separated):
  ```
  > 1.1.1.1, 8.8.8.8, 9.9.9.9
  ```

- Exit the application:
  ```
  > exit
  ```

## Configuration

Edit `constants.py` to modify:
- API endpoint
- Request timeout
- Concurrent request limits

## Logging

Application logs are stored in:
```
logs/ip_info.log
```

Logs include:
- Successful API requests
- Error conditions
- Performance metrics

## Troubleshooting

**No log files created?**
- Verify `logs` directory exists and is writable
- Check application has proper permissions

**API errors?**
- Verify your ipinfo.io token is valid
- Check your API quota

## License

Proprietary software - © 2025 DPhish. All rights reserved.

## Support

For technical support, contact:
- Email: 
- Internal Ticket System: 
```

### Key Features of This README:

1. **Branding**: Clearly identifies the tool as a DPhish product
2. **Installation Steps**: Detailed from environment setup to first run
3. **Usage Examples**: Shows both simple and advanced usage
4. **Troubleshooting**: Common issues and solutions
5. **Support Information**: Directs to proper support channels
6. **Logging Details**: Explains where to find operational logs
7. **Configuration Notes**: Points to where settings can be adjusted

The placeholder logo URL can be replaced with your actual company logo. You may also want to add:
- Screenshots of the tool in action
- More detailed API documentation
- Company-specific compliance or security notes
- Internal architecture overview for developer reference

Would you like me to add any DPhish-specific policies or procedures to the documentation?