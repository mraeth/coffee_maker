# Pour-Over Coffee Maker

A smart scale and automated pour-over coffee brewing system running on Raspberry Pi.

## Overview

This project consists of two main components:

1. **Smart Scale** - Real-time monitoring of weight and temperature during pour-over coffee brewing, accessible via a web interface on your phone
2. **Automated Pouring** (planned) - Machine control for automated water pouring based on recipe parameters

## Hardware

- Raspberry Pi
- Load cell (weighing sensor)
- Temperature probe
- (Future) Pump/servo for automated pouring

## Features

- Real-time weight and temperature monitoring
- Web-based dashboard accessible from any device on the network
- Configurable brewing recipes (coffee amount, ratio)
- Target weight calculation and visual indicators
- Data logging with CSV export

## Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/coffee_maker.git
cd coffee_maker

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Running the Web Interface

```bash
python test_webserver.py
```

Access the dashboard at `http://<raspberry-pi-ip>:8060` from your phone or computer.

### Production Deployment

For production use on the Raspberry Pi:

```bash
gunicorn test_webserver:server -b 0.0.0.0:8060
```

## Project Structure

```
coffee_maker/
├── test_webserver.py    # Main web application
├── plot_data.py         # Data analysis utilities
├── data/                # Saved brewing session data
├── requirements.txt     # Python dependencies
└── README.md
```

## Configuration

Edit the following parameters in `test_webserver.py`:

```python
recipe = 60          # g/l (coffee to water ratio)
coffee_amount = 20   # grams of coffee
```

## Roadmap

- [ ] Hardware integration (load cell, temperature sensor)
- [ ] Automated pouring control
- [ ] Recipe management
- [ ] Brewing profiles and presets


