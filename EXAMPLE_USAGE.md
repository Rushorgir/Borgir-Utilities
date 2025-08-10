# Example usage of the Dynamic VC Bot

## Step-by-step setup example:

# 1. Install dependencies
# pip install -r requirements.txt

# 2. Set up your bot token in config.json:
{
    "token": "your_actual_bot_token_here"
}

# 3. Run the bot
# python dynamic_vc_bot.py

# 4. In Discord, use these commands:

# Add a VC hub (requires Manage Channels permission)
/add-vc-hub channel:#General limit:10

# List current VC hubs  
/list-vc-hubs

# Remove a VC hub
/remove-vc-hub channel:#General

# Clean up any orphaned channels (Admin only)
/cleanup-temp-channels

## How it works:
# 1. User joins the "General" voice channel (which is now a VC hub)
# 2. Bot creates "Username's Channel" in the same category
# 3. User gets moved to their new channel automatically  
# 4. Others can join "Username's Channel" manually
# 5. When everyone leaves, the channel gets deleted automatically