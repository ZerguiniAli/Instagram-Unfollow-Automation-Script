# Instagram Mass Unfollower

This Python script automates the process of unfollowing accounts on Instagram using Selenium WebDriver.

## Features
- Logs into your Instagram account.
- Navigates to your following list.
- Unfollows accounts in batches with randomized delays to avoid detection.
- Takes periodic breaks for a human-like behavior.
- Handles pop-ups and errors effectively.

## Requirements
- Python 3.x
- Google Chrome browser
- ChromeDriver (managed automatically by `webdriver-manager`)

## Installation
1. Clone this repository or download the script.
2. Install the required dependencies:
   ```sh
   pip install selenium webdriver-manager
   ```

## Usage
1. Open the script and replace the following placeholders with your Instagram credentials:
   ```python
   INSTAGRAM_USERNAME = "YOUR_USERNAME"
   INSTAGRAM_PASSWORD = "YOUR_PASSWORD"
   ```
2. Run the script:
   ```sh
   python script.py
   ```

## Configuration Options
- `MAX_UNFOLLOWS`: Maximum number of accounts to unfollow.
- `UNFOLLOWS_PER_BATCH`: Number of unfollows per batch.
- `BATCH_PAUSE`: Time range (in seconds) for pauses between batches.
- `UNFOLLOW_PAUSE`: Time range (in seconds) for pauses between unfollows.
- `LONG_BREAK_INTERVAL`: Number of unfollows before taking a long break.
- `LONG_BREAK_DURATION`: Duration range (in seconds) for long breaks.

## Notes
- This script automates interactions with Instagram, which may violate Instagram's terms of service. Use at your own risk.
- Consider using a secondary account to test before running on your main account.
- Excessive usage may result in temporary or permanent bans from Instagram.

## Disclaimer
This software is for educational purposes only. The developer is not responsible for any misuse or account bans.
