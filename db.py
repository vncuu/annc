import discord
from discord.ext import commands
from discord import app_commands
import json
import traceback

class ServerInfoCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="db", description="Shows server information.")
    @app_commands.describe(
        server_id="The ID of the server to display information for.",
        ephemeral="Whether the message should be visible only to you (True) or everyone (False). Defaults to False."
    )
    async def db(self, interaction: discord.Interaction, server_id: str, ephemeral: bool = False):
        """
        Displays detailed information about the server stored in the database.
        """
        try:
            # Ensure server_id is treated as a string
            server_id = str(server_id)
            
            # Try to load server data
            try:
                with open('database/server_data.json', 'r') as f:
                    data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                data = {}

            # Check if the server ID exists in the data
            if server_id not in data:
                await interaction.response.send_message(f"Server with ID {server_id} not found in the database.", ephemeral=True)
                return

            # Retrieve the server data
            server_info = data[server_id]

            # Create an embed to display the server information
            embed = discord.Embed(title=f"Server Information for {server_info['server_name'] or 'Unknown'}", color=discord.Color(0xc9a0ec))
            embed.add_field(name="Server ID", value=server_info['server_id'], inline=True)
            embed.add_field(name="Server Name", value=server_info.get('server_name', 'N/A'), inline=True)
            embed.add_field(name="Boosts", value=server_info.get('boosts', 'N/A'), inline=True)
            embed.add_field(name="Member Count", value=server_info.get('member_count', 'N/A'), inline=True)
            embed.add_field(name="Bot Count", value=server_info.get('bot_count', 'N/A'), inline=True)
            embed.add_field(name="Owner Name", value=server_info.get('owner_name', 'N/A'), inline=True)
            embed.add_field(name="Verification Level", value=server_info.get('verification_level', 'N/A'), inline=True)

            # Send the embed message with server info
            await interaction.response.send_message(embed=embed, ephemeral=ephemeral)

        except Exception as e:
            # Print the error to the console
            print(f"Error in /db command: {e}")
            traceback.print_exc()
            await interaction.response.send_message("An error occurred while processing your request.", ephemeral=True)

    @db.error
    async def db_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """
        Handles errors during the execution of the `db` command.
        """
        if isinstance(error, app_commands.AppCommandError):
            await interaction.response.send_message("An unexpected error occurred while fetching data.", ephemeral=True)

    async def cog_load(self):
        """
        Called when the cog is loaded.
        """
        print(f"{self.__class__.__name__} cog loaded.")

    async def cog_unload(self):
        """
        Called when the cog is unloaded.
        """
        print(f"{self.__class__.__name__} cog unloaded.")

async def setup(bot):
    """
    Setup function to add the cog to the bot.
    """
    try:
        await bot.add_cog(ServerInfoCommand(bot))
        print("ServerInfoCommand cog added successfully!")
    except Exception as e:
        print(f"Error loading ServerInfoCommand: {e}")
