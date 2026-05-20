# Corporate Telemetry Agent

This tool is designed for corporate psychological research to measure employee stress and emotional states by correlating environmental ambiance (audio), facial expressions (webcam), and current activities (active window & screenshot).

## Setup Instructions

### 1. Requirements
Ensure you have Python 3.8+ installed on the Windows machine.
Install the necessary libraries:
```bash
pip install -r requirements.txt
```

### 2. Configure Telegram
1.  **Bot Token:** I have already populated the `.env` file with your token: `8311793464:AAEN71Ki-QefD5zLEZ1PoBk3CnTTcIoMSr8`.
2.  **Get Chat ID:**
    *   Open Telegram and send a message (any message) to your bot: [t.me/winautoobot](https://t.me/winautoobot).
    *   Run the helper script: `python get_chat_id.py`.
    *   Copy the ID it gives you (e.g., `123456789`).
    *   Open the `.env` file and paste it after `TELEGRAM_CHAT_ID=`.

### 3. Running the Agent
Once configured, run the agent script:
```bash
python agent.py
```
The agent will:
*   Display a one-time notice about the study.
*   Every 60 seconds (configurable in `agent.py`), it will capture:
    *   A photo from the webcam.
    *   A full-screen screenshot.
    *   A 5-second ambient audio recording.
    *   The title of the active application.
*   Send all data to your Telegram bot.

## Files
*   `agent.py`: The main monitoring script.
*   `get_chat_id.py`: Utility to find your Telegram Chat ID.
*   `.env`: Stores your secret bot token and target chat ID.
*   `requirements.txt`: List of dependencies.

## Important: Privacy & Compliance
From a psychological and legal standpoint, ensure all participating employees are fully informed and have signed consent forms. This script is designed for transparent data collection in a research context.
