import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import traceback

class DBAddCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def load_server_data(self):
        """
        Load and return the server data from the server_data.json file.
        """
        try:
            os.makedirs('database', exist_ok=True)  # Ensure the 'database' directory exists
            # Load the existing server data from the JSON file
            with open('database/server_data.json', 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}  # Return an empty dict if the file doesn't exist or is invalid

    async def save_server_data(self, server_data):
        """
        Save the updated server data to the server_data.json file.
        """
        with open('database/server_data.json', 'w') as file:
            json.dump(server_data, file, indent=4)

    async def is_beta_user(self, interaction: discord.Interaction):
        """
        Check if the user is a beta user. Returns True if they are a beta user, else raises CheckFailure.
        """
        # Load the current beta users
        beta_users = await self.load_beta_data()

        # Check if the user ID is in the list of beta users
        if interaction.user.id not in beta_users:
            raise app_commands.CheckFailure("You do not have permission to use this command.")
        return True

    @app_commands.command(name="add_db", description="Add or update server data (beta feature).")
    @app_commands.describe(
        server_id="The ID of the server (this field is mandatory).",
        server_name="The name of the server (optional).",
        owner_id="The ID of the server owner (optional).",
        region="The region of the server (optional).",
        boosts="The boost count of the server (optional).",
        member_count="The number of members in the server (optional).",
        bot_count="The number of bots in the server (optional).",
        owner_name="The name of the server owner (optional).",
        verification_level="The verification level of the server (optional)."
    )
    @app_commands.check(lambda interaction: interaction.client.get_cog('DBAddCommand').is_beta_user(interaction))  # Ensure user is a beta user
    async def add_db(self, interaction: discord.Interaction, server_id: int, server_name: str = None, owner_id: int = None, region: str = None,
                     boosts: int = None, member_count: int = None, bot_count: int = None, owner_name: str = None, verification_level: str = None):
        """
        Adds or updates the server data in the server_data.json file and displays the server information in an embed.
        """
        try:
            # Load the current server data
            server_data = await self.load_server_data()

            # Prepare the new server data to be added or updated
            server_info = {
                "server_name": server_name,
                "owner_id": owner_id,
                "region": region,
                "boosts": boosts,
                "member_count": member_count,
                "bot_count": bot_count,
                "owner_name": owner_name,
                "verification_level": verification_level
            }

            # If the server ID exists in the data, update it
            if server_id in server_data:
                # Merge the new data with the existing data
                server_data[server_id].update({k: v for k, v in server_info.items() if v is not None})
                await interaction.response.send_message(f"Server data for server ID {server_id} updated successfully.", ephemeral=True)
            else:
                # If it's a new server, create a new entry
                server_data[server_id] = server_info
                await interaction.response.send_message(f"Server data for server ID {server_id} added successfully.", ephemeral=True)

            # Save the updated server data to the file
            await self.save_server_data(server_data)

            # Create an embed to display the server information
            embed = discord.Embed(title=f"Server Information for {server_info['server_name'] or 'Unknown'}", color=discord.Color(0xc9a0ec))
            embed.add_field(name="Server ID", value=server_id, inline=True)
            embed.add_field(name="Server Name", value=server_info.get('server_name', 'N/A'), inline=True)
            embed.add_field(name="Boosts", value=server_info.get('boosts', 'N/A'), inline=True)
            embed.add_field(name="Member Count", value=server_info.get('member_count', 'N/A'), inline=True)
            embed.add_field(name="Bot Count", value=server_info.get('bot_count', 'N/A'), inline=True)
            embed.add_field(name="Owner Name", value=server_info.get('owner_name', 'N/A'), inline=True)
            embed.add_field(name="Verification Level", value=server_info.get('verification_level', 'N/A'), inline=True)

            # Send the embed as a follow-up message
            await interaction.followup.send(embed=embed)

        except Exception as e:
            print(f"Error in /add_db command: {e}")
            traceback.print_exc()
            await interaction.response.send_message("An error occurred while processing your request. Check the bot's logs for details.", ephemeral=True)

    @add_db.error
    async def add_db_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """
        Handle errors for the add_db command.
        """
        if isinstance(error, app_commands.CheckFailure):
            # Handle permission-related errors
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        else:
            # Handle other types of errors
            print(f"Unexpected error: {error}")
            await interaction.response.send_message("An unexpected error occurred.", ephemeral=True)

    async def cog_load(self):
        """
        This function is called when the cog is loaded into the bot.
        """
        print(f"{self.__class__.__name__} cog loaded.")

    async def cog_unload(self):
        """
        This function is called when the cog is unloaded from the bot.
        """
        print(f"{self.__class__.__name__} cog unloaded.")

async def setup(bot):
    """
    This function adds the cog to the bot during startup.
    """
    await bot.add_cog(DBAddCommand(bot))
    print("DBAddCommand cog added successfully!")
