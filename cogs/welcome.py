import discord
from discord import app_commands
from discord.ext import commands
from .database import get_settings, update_setting

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        settings = await get_settings(self.bot.db, member.guild.id)
        if not settings["welcome_dm_enabled"]:
            return
        message = settings["welcome_dm_message"]
        message = message.replace("{user}", member.mention)
        message = message.replace("{username}", member.name)
        message = message.replace("{user_id}", str(member.id))
        message = message.replace("{server}", member.guild.name)
        message = message.replace("{server_id}", str(member.guild.id))
        message = message.replace("{member_count}", str(member.guild.member_count))
        try:
            await member.send(message)
        except discord.Forbidden:
            pass

    welcome = app_commands.Group(name="welcome", description="Configure welcome messages.")

    @welcome.command(name="enable", description="Enable welcome DMs.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def enable(self, interaction):
        await update_setting(self.bot.db, interaction.guild.id, "welcome_dm_enabled", 1)
        await interaction.response.send_message("✅ Welcome DMs enabled.")

    @welcome.command(name="disable", description="Disable welcome DMs.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def disable(self, interaction):
        await update_setting(self.bot.db, interaction.guild.id, "welcome_dm_enabled", 0)
        await interaction.response.send_message("✅ Welcome DMs disabled.")

    @welcome.command(name="message", description="Set the welcome DM text.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def message(self, interaction, text: str):
        await update_setting(self.bot.db, interaction.guild.id, "welcome_dm_message", text)
        await interaction.response.send_message("✅ Welcome DM updated.")

    @welcome.command(name="preview", description="Preview the welcome DM.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def preview(self, interaction):
        settings = await get_settings(self.bot.db, interaction.guild.id)
        text = settings["welcome_dm_message"]
        for key, value in {
            "{user}": interaction.user.mention,
            "{username}": interaction.user.name,
            "{user_id}": str(interaction.user.id),
            "{server}": interaction.guild.name,
            "{server_id}": str(interaction.guild.id),
            "{member_count}": str(interaction.guild.member_count),
        }.items():
            text = text.replace(key, value)
        await interaction.response.send_message(text, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Welcome(bot))
