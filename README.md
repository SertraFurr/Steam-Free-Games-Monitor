# Steam Free Games Monitor

A Python script that monitors Steam for free games and sends notifications via Discord webhook and/or custom API endpoint.

## Features

- 🎮 Automatically detects new free games on Steam
- 💬 Discord webhook notifications with embedded game info
- 🌐 Optional custom API endpoint integration
- ⚙️ Configurable via JSON file

## Requirements

```bash
pip install requests beautifulsoup4
```

## Configuration

Create a `config.json` file:

```json
{
  "DEBUG_MODE": false,
  "post_data": {
    "discord_webhook": "YOUR_DISCORD_WEBHOOK_URL_HERE",
    "website_api_url": "YOUR_API_URL_HERE"
  },
  "webhook_data": {
    "username": "Game Tracker",
    "mention_everyone": false,
    "mention_role_id": null
  }
}
```

### Configuration Options

- `DEBUG_MODE`: Enable/disable debug output
- `discord_webhook`: Your Discord webhook URL (optional)
- `website_api_url`: Your custom API endpoint URL (optional)
- `username`: Discord bot username for notifications
- `mention_everyone`: Mention @everyone in Discord (true/false)
- `mention_role_id`: Specific role ID to mention instead of everyone

**Note:** You must set at least one of `discord_webhook` or `website_api_url`.

## Usage

```bash
python main.py
```

The script will:
1. Check Steam for free games every 60 seconds
2. Send notifications when new free games are found
3. Track seen games to avoid duplicate notifications

## Example Discord Notification

The bot sends embedded messages with:
- Game title and Steam store link
- Price information
- Game thumbnail/header image
- Timestamp

## Disclaimer

The author is not responsible for any misuse or consequences of using this script. Use at your own risk and in accordance with Steam's and Discord's terms of service.

## License

MIT
