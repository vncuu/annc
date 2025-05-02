import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import traceback

class BetaCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Ensure OWNER_IDS is a list of integers from the environment variable
        self.owner_ids = list(map(int, os.getenv('OWNER_IDS', '').split(',')))
        print(f"Owner IDs: {self.owner_ids}")  # Debugging: Check the list of owner IDs

    async def load_beta_data(self):
        """
        Load and return the list of beta users from the JSON file.
        """
        try:
            os.makedirs('database', exist_ok=True)  # Ensure the 'database' directory exists
            # Load the existing beta users from the JSON file
            with open('database/beta.json', 'r') as file:
                return json.load(file).get('users', [])
        except (FileNotFoundError, json.JSONDecodeError):
            return []  # Return an empty list if the file doesn't exist or is invalid

    async def save_beta_data(self, beta_users):
        """
        Save the updated list of beta users to the JSON file.
        """
        beta_data = {'users': beta_users}
        with open('database/beta.json', 'w') as file:
            json.dump(beta_data, file, indent=4)

    async def is_owner(self, interaction: discord.Interaction):
        """
        Check if the user is an owner. Returns True if they are an owner, else raises CheckFailure.
        """
        if interaction.user.id not in self.owner_ids:
            raise app_commands.CheckFailure("You do not have permission to use this command.")
        return True

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

    @app_commands.command(name="beta", description="[OWNER] Adds a user ID to the beta user list.")
    @app_commands.describe(user_id="The ID of the user to add to the beta list.")
    @app_commands.check(lambda interaction: interaction.client.get_cog('BetaCommand').is_owner(interaction))  # Only owners can use this
    async def beta(self, interaction: discord.Interaction, user_id: str):
        """
        Adds a user ID to the beta user list in database/beta.json.
        """
        try:
            user_id_int = int(user_id)

            # Load the current beta users
            beta_users = await self.load_beta_data()

            # Check if the user ID is already in the list
            if user_id_int in beta_users:
                await interaction.response.send_message(f"User ID {user_id} is already in the beta user list.", ephemeral=True)
                return

            # Add the new user ID to the list and save it
            beta_users.append(user_id_int)
            await self.save_beta_data(beta_users)

            await interaction.response.send_message(f"User ID {user_id} has been added to the beta user list.", ephemeral=True)

        except ValueError:
            await interaction.response.send_message("Invalid user ID. Please enter a valid number.", ephemeral=True)
        except Exception as e:
            print(f"Error in /beta command: {e}")
            traceback.print_exc()
            await interaction.response.send_message("An error occurred while processing your request. Check the bot's logs for details.", ephemeral=True)

    @beta.error
    async def beta_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """
        Handle errors for the beta command.
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
    await bot.add_cog(BetaCommand(bot))
    print("BetaCommand cog added successfully!")
