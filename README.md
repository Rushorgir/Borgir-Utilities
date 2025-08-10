# Dynamic Voice Channels Discord Bot

A Discord bot that creates temporary voice channels when users join a "VC Hub" channel. Built with discord.py 2.3.2.

## Features

- **Dynamic Voice Channels**: When a user joins a VC hub, a new temporary channel is created and the user is moved to it
- **Automatic Cleanup**: Empty temporary channels are automatically deleted
- **User Limits**: Set user limits for temporary channels created from each hub
- **Slash Commands**: Modern slash commands for easy management
- **Persistent Storage**: SQLite database to store VC hub configurations
- **Permission Controls**: Only users with "Manage Channels" permission can manage VC hubs

## Commands

### `/add-vc-hub channel: [limit:]`
Adds a voice channel as a VC hub. When users join this channel, a temporary channel will be created.
- `channel`: The voice channel to make into a VC hub
- `limit`: (optional) User limit for temporary channels created from this hub

### `/remove-vc-hub channel:`
Removes a voice channel from being a VC hub.
- `channel`: The voice channel to remove from VC hubs

### `/list-vc-hubs`
Lists all VC hubs configured in the current server.

### `/cleanup-temp-channels` (Admin only)
Manually clean up orphaned temporary channels.

## Setup Instructions

### 1. Prerequisites
- Python 3.8 or higher
- A Discord application/bot token

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Bot Token
Choose one of these methods:

#### Method A: Environment Variable
```bash
export DISCORD_BOT_TOKEN="your_bot_token_here"
```

#### Method B: Configuration File
Edit `config.json`:
```json
{
    "token": "your_bot_token_here"
}
```

#### Method C: .env File
Create `.env` file:
```
DISCORD_BOT_TOKEN=your_bot_token_here
```

### 4. Discord Bot Setup

#### Creating the Bot
1. Go to https://discord.com/developers/applications
2. Click "New Application" and give it a name
3. Go to "Bot" section in the sidebar
4. Click "Add Bot"
5. Copy the bot token (this is your `DISCORD_BOT_TOKEN`)

#### Bot Permissions
Your bot needs these permissions:
- View Channels
- Manage Channels
- Connect
- Move Members
- Use Slash Commands

Use this permissions integer: `16785408`

#### Invite URL
Generate an invite URL with the required permissions:
```
https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_CLIENT_ID&permissions=16785408&scope=bot%20applications.commands
```

Replace `YOUR_BOT_CLIENT_ID` with your bot's client ID from the Discord Developer Portal.

### 5. Run the Bot
```bash
python dynamic_vc_bot.py
```

## How It Works

1. **Setup**: Use `/add-vc-hub` to designate a voice channel as a "VC Hub"
2. **Creation**: When someone joins the VC Hub, a new temporary voice channel is created in the same category
3. **Movement**: The user is automatically moved to the new temporary channel
4. **Others can join**: Other users can manually join the temporary channel
5. **Cleanup**: When everyone leaves the temporary channel, it's automatically deleted

## Example Usage

```
1. Create a voice channel called "ðŸŽ™ï¸ VC Hub"
2. Run: /add-vc-hub channel:#ðŸŽ™ï¸ VC Hub limit:5
3. When users join "ðŸŽ™ï¸ VC Hub", a temporary channel like "John's Channel" is created
4. The user is moved to "John's Channel" automatically
5. When everyone leaves "John's Channel", it's automatically deleted
```

## Database

The bot uses SQLite to store:
- VC hub configurations (which channels are hubs and their settings)
- Active temporary channels tracking

The database file (`dynamic_vc_bot.db`) is created automatically when the bot first runs.

## Troubleshooting

### Common Issues

1. **Bot not responding to slash commands**
   - Make sure the bot has "Use Slash Commands" permission
   - Wait a few minutes after inviting the bot for commands to sync
   - Try running the bot and check console for sync messages

2. **"Missing Permissions" errors**
   - Ensure the bot role is above other roles it needs to manage
   - Check that the bot has "Manage Channels" and "Move Members" permissions
   - Make sure the bot can access the voice channels and categories

3. **Temporary channels not being created**
   - Verify the channel is properly added as a VC hub with `/list-vc-hubs`
   - Check bot permissions in the category where channels should be created
   - Look at console output for error messages

4. **Database errors**
   - Make sure the bot has write permissions in its directory
   - Check that the database file isn't corrupted
   - Try deleting `dynamic_vc_bot.db` to reset (will lose VC hub configurations)

### Logs and Debugging
The bot outputs helpful information to the console including:
- When channels are created/deleted
- Permission errors
- Database operations
- Command usage

## File Structure
```
discord-bot/
â”œâ”€â”€ dynamic_vc_bot.py      # Main bot file
â”œâ”€â”€ config.json            # Bot configuration
â”œâ”€â”€ requirements.txt       # Python dependencies
â”œâ”€â”€ .env.example          # Environment variables template
â”œâ”€â”€ .gitignore            # Git ignore file
â”œâ”€â”€ README.md             # This file
â””â”€â”€ dynamic_vc_bot.db     # SQLite database (created automatically)
```

## Advanced Configuration

### Custom Channel Names
The bot creates channels with the format `{user}'s Channel`. You can modify this in the `on_voice_state_update` function:

```python
temp_channel_name = f"{member.display_name}'s Channel"
```

### Channel Permissions
Temporary channels inherit permissions from the VC hub channel. You can modify the `overwrites` parameter when creating channels.

### Database Location
By default, the database is stored as `dynamic_vc_bot.db` in the same directory as the bot. You can change this by modifying the connection string in the `init_database` method.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the console output for error messages
3. Create an issue in the repository with details about your problem