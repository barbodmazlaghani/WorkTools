# Vehicle Data Auto-Downloader

This script automates the downloading of vehicle data excels from a specified API. It maintains a state to track previously downloaded data for each vehicle and ensures that data is downloaded only for the periods that have not been covered since the last download.

## Features

- Automatic fetching of vehicle data via API.
- Periodic updates based on vehicle activity within the last six months.
- Error logging to facilitate debugging and maintenance.
- State management to prevent re-downloading of data.

## Requirements

- Python 3.6 or higher
- `requests` library
- `json` library for parsing and saving state
- Access to the target API with a valid authorization token

## Installation

1. Clone this repository.
2. Install required Python libraries:

   ```bash
   pip install requests
