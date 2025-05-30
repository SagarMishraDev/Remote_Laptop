# Remote Laptop Control Bot 🤖💻

A Python-based Telegram bot that lets you remotely control your laptop through chat commands. Perfect for quick access, troubleshooting, or when you forget files at home!

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![Telegram API](https://img.shields.io/badge/Telegram%20Bot%20API-v20.0-blue)](https://core.telegram.org/bots/api)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

![Demo](https://i.imgur.com/JQh6W7r.png) *(Example screenshot command)*

## ✨ Features

- **📸 Screen Capture**: Take and receive screenshots instantly
- **📂 File Browser**: Navigate directories and download files
- **📊 System Monitoring**: Check CPU/RAM/Disk stats
- **⏻ Power Control**: Shutdown/restart remotely
- **🔒 Secure**: End-to-end encrypted + user whitelisting
- **🚀 Lightweight**: <50MB RAM usage

## 🛠️ Installation

### Prerequisites
- Python 3.11+
- Telegram account

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/SagarMishraDev/remote-laptop-bot.git
   cd remote-laptop-bot

2. Install dependencies:
   pip install -r requirements.txt

3. Configure Bot
   .Create bot via @BotFather

   .Copy API token

   .Edit config.py:

   TOKEN = "YOUR_BOT_TOKEN"  # From BotFather
   ALLOWED_USERS = [123456789]  # Your Telegram ID

4. Run Bot
   bash
   python bot.py

🛠️ Usage Guide
   Basic Commands
    /start - Initialize bot
    /help - Show command list
    /sysinfo - Check CPU/RAM/Disk
    /files ~/Documents - Browse files

📂 File Structure
    
    ├── bot.py            # Main application
    ├── config.py         # Configuration
    ├── commands/         # Modular commands
    │   ├── files.py
    │   ├── system.py
    │   └── power.py
    ├── requirements.txt
    └── README.md

🔍 Troubleshooting

    ImportError: No module named 'telegram'	" pip install python-telegram-bot "

    Pillow required	" pip install pillow "

    Bot not responding	" Check token in config.py "    

📜 License
        Distributed under the MIT License. See LICENSE for details.

💡 Pro Tip: For always-on access, run the bot on a Raspberry Pi!

🏗 System Architecture:

┌─────────────┐    /screenshot    ┌─────────────┐  
│  User Phone │ ────────────────> │ Telegram    │  
└─────────────┘                   └──────┬──────┘  
                                         │  
                                   Routes Command  
                                         ↓  
┌─────────────┐  pyautogui.screenshot() ┌─────────────┐  
│ Python      │ ──────────────────────> │ Your        │  
│ Server      │ <────────────────────── │ Laptop      │  
└──────┬──────┘    Returns image data   └─────────────┘  
       │  
  Sends Image  
       ↓  
┌─────────────┐  
│  User Phone │ <─(Receives screenshot)  
└─────────────┘  

✉️ Contact: @sagarmishra9111 | 📝 Report Issue
