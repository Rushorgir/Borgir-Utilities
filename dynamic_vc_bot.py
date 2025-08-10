import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import asyncio
import json
import os
from typing import Optional

# Bot configuration
class DynamicVCBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.voice_states = True
        intents.guilds = True
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)

        # Initialize database
        self.init_database()

        # Store temporary channels and their data
        self.temp_channels = {}  # {temp_channel_id: {'hub_id': hub_id, 'creator_id': user_id}}

    def init_database(self):
        """Initialize SQLite database for storing VC hub configurations"""
        self.conn = sqlite3.connect('dynamic_vc_bot.db')
        self.cursor = self.conn.cursor()

        # Create table for VC hubs
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS vc_hubs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL UNIQUE,
                user_limit INTEGER DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create table for temporary channels tracking
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS temp_channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id INTEGER NOT NULL UNIQUE,
                hub_id INTEGER NOT NULL,
                creator_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (hub_id) REFERENCES vc_hubs (channel_id)
            )
        """)

        self.conn.commit()

    async def setup_hook(self):
        """Setup hook called when bot starts"""
        await self.tree.sync()
        print(f"Synced slash commands for {self.user}")

    def is_vc_hub(self, channel_id: int) -> Optional[tuple]:
        """Check if a channel is a VC hub and return its data"""
        self.cursor.execute("SELECT channel_id, user_limit FROM vc_hubs WHERE channel_id = ?", (channel_id,))
        result = self.cursor.fetchone()
        return result if result else None

    def add_temp_channel(self, temp_channel_id: int, hub_id: int, creator_id: int):
        """Add temporary channel to database"""
        self.cursor.execute(
            "INSERT OR REPLACE INTO temp_channels (channel_id, hub_id, creator_id) VALUES (?, ?, ?)",
            (temp_channel_id, hub_id, creator_id)
        )
        self.conn.commit()
        self.temp_channels[temp_channel_id] = {'hub_id': hub_id, 'creator_id': creator_id}

    def remove_temp_channel(self, temp_channel_id: int):
        """Remove temporary channel from database"""
        self.cursor.execute("DELETE FROM temp_channels WHERE channel_id = ?", (temp_channel_id,))
        self.conn.commit()
        if temp_channel_id in self.temp_channels:
            del self.temp_channels[temp_channel_id]

    def is_temp_channel(self, channel_id: int) -> bool:
        """Check if a channel is a temporary channel"""
        return channel_id in self.temp_channels

    async def close(self):
        """Close database connection when bot shuts down"""
        self.conn.close()
        await super().close()

bot = DynamicVCBot()

@bot.event
async def on_ready():
    """Event triggered when bot is ready"""
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')

    # Load existing temporary channels from database
    bot.cursor.execute("SELECT channel_id, hub_id, creator_id FROM temp_channels")
    for temp_channel_id, hub_id, creator_id in bot.cursor.fetchall():
        bot.temp_channels[temp_channel_id] = {'hub_id': hub_id, 'creator_id': creator_id}

    print(f'Loaded {len(bot.temp_channels)} temporary channels from database')

@bot.event
async def on_voice_state_update(member, before, after):
    """Handle voice state changes - main logic for dynamic VC creation/deletion"""

    # User joined a channel
    if after.channel and after.channel.id != getattr(before.channel, 'id', None):
        hub_data = bot.is_vc_hub(after.channel.id)

        if hub_data:
            hub_channel_id, user_limit = hub_data

            try:
                # Create temporary voice channel in the same category as the hub
                category = after.channel.category

                # Generate a unique name for the temp channel
                temp_channel_name = f"{member.display_name}'s Channel"

                # Create the temporary channel
                overwrites = after.channel.overwrites
                temp_channel = await after.channel.guild.create_voice_channel(
                    name=temp_channel_name,
                    category=category,
                    user_limit=user_limit,
                    overwrites=overwrites
                )

                # Move the user to the temporary channel
                await member.move_to(temp_channel)

                # Add to tracking
                bot.add_temp_channel(temp_channel.id, hub_channel_id, member.id)

                print(f"Created temporary channel '{temp_channel_name}' for {member.display_name}")

            except discord.errors.Forbidden:
                print(f"Missing permissions to create voice channel in {after.channel.guild.name}")
            except Exception as e:
                print(f"Error creating temporary channel: {e}")

    # User left a channel
    if before.channel and bot.is_temp_channel(before.channel.id):
        # Check if the temporary channel is now empty
        if len(before.channel.members) == 0:
            try:
                # Delete the empty temporary channel
                temp_channel_name = before.channel.name
                await before.channel.delete(reason="Temporary channel empty")

                # Remove from tracking
                bot.remove_temp_channel(before.channel.id)

                print(f"Deleted empty temporary channel '{temp_channel_name}'")

            except discord.errors.NotFound:
                # Channel was already deleted
                bot.remove_temp_channel(before.channel.id)
            except Exception as e:
                print(f"Error deleting temporary channel: {e}")

# Slash Commands
@bot.tree.command(name="add-vc-hub", description="Add a voice channel as a VC hub")
@app_commands.describe(
    channel="The voice channel to make into a VC hub",
    limit="User limit for created temporary channels (optional)"
)
async def add_vc_hub(interaction: discord.Interaction, channel: discord.VoiceChannel, limit: Optional[int] = None):
    """Add a voice channel as a VC hub"""

    # Check if user has manage channels permission
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("âŒ You need 'Manage Channels' permission to use this command.", ephemeral=True)
        return

    # Validate limit
    if limit is not None and (limit < 1 or limit > 99):
        await interaction.response.send_message("âŒ User limit must be between 1 and 99.", ephemeral=True)
        return

    try:
        # Check if channel is already a VC hub
        if bot.is_vc_hub(channel.id):
            await interaction.response.send_message(f"âŒ {channel.name} is already a VC hub.", ephemeral=True)
            return

        # Add to database
        bot.cursor.execute(
            "INSERT INTO vc_hubs (guild_id, channel_id, user_limit) VALUES (?, ?, ?)",
            (interaction.guild.id, channel.id, limit)
        )
        bot.conn.commit()

        limit_text = f" (limit: {limit})" if limit else " (no limit)"
        await interaction.response.send_message(f"âœ… Added {channel.name} as a VC hub{limit_text}")

    except sqlite3.IntegrityError:
        await interaction.response.send_message(f"âŒ {channel.name} is already a VC hub.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"âŒ Error adding VC hub: {e}", ephemeral=True)

@bot.tree.command(name="remove-vc-hub", description="Remove a VC hub")
@app_commands.describe(channel="The voice channel to remove from VC hubs")
async def remove_vc_hub(interaction: discord.Interaction, channel: discord.VoiceChannel):
    """Remove a voice channel from VC hubs"""

    # Check if user has manage channels permission
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("âŒ You need 'Manage Channels' permission to use this command.", ephemeral=True)
        return

    try:
        # Check if channel is a VC hub
        if not bot.is_vc_hub(channel.id):
            await interaction.response.send_message(f"âŒ {channel.name} is not a VC hub.", ephemeral=True)
            return

        # Remove from database
        bot.cursor.execute("DELETE FROM vc_hubs WHERE channel_id = ?", (channel.id,))
        bot.conn.commit()

        if bot.cursor.rowcount > 0:
            await interaction.response.send_message(f"âœ… Removed {channel.name} from VC hubs")
        else:
            await interaction.response.send_message(f"âŒ {channel.name} was not found in VC hubs.", ephemeral=True)

    except Exception as e:
        await interaction.response.send_message(f"âŒ Error removing VC hub: {e}", ephemeral=True)

@bot.tree.command(name="list-vc-hubs", description="List all VC hubs in this server")
async def list_vc_hubs(interaction: discord.Interaction):
    """List all VC hubs in the current server"""

    try:
        # Get all VC hubs for this guild
        bot.cursor.execute(
            "SELECT channel_id, user_limit FROM vc_hubs WHERE guild_id = ?",
            (interaction.guild.id,)
        )
        hubs = bot.cursor.fetchall()

        if not hubs:
            await interaction.response.send_message("ðŸ“ No VC hubs configured in this server.", ephemeral=True)
            return

        # Build embed
        embed = discord.Embed(
            title="ðŸŽ™ï¸ VC Hubs",
            description="Voice channels that create temporary channels",
            color=discord.Color.blue()
        )

        for channel_id, user_limit in hubs:
            channel = interaction.guild.get_channel(channel_id)
            if channel:
                limit_text = f" (limit: {user_limit})" if user_limit else " (no limit)"
                embed.add_field(
                    name=f"#{channel.name}",
                    value=f"ID: {channel_id}{limit_text}",
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"Deleted Channel",
                    value=f"ID: {channel_id} (channel no longer exists)",
                    inline=False
                )

        await interaction.response.send_message(embed=embed)

    except Exception as e:
        await interaction.response.send_message(f"âŒ Error listing VC hubs: {e}", ephemeral=True)

# Error handling for commands
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Handle slash command errors"""
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("âŒ You don't have permission to use this command.", ephemeral=True)
    elif isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"âŒ Command is on cooldown. Try again in {error.retry_after:.2f} seconds.", ephemeral=True)
    else:
        await interaction.response.send_message("âŒ An error occurred while processing the command.", ephemeral=True)
        print(f"Command error: {error}")

# Run the bot
if __name__ == "__main__":
    # Load token from environment variable or config file
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')

    if not TOKEN:
        # Try to load from config.json
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                TOKEN = config.get('token')
        except FileNotFoundError:
            print("Error: No token found. Set DISCORD_BOT_TOKEN environment variable or create config.json")
            exit(1)

    if not TOKEN:
        print("Error: No bot token provided")
        exit(1)

    bot.run(TOKEN)