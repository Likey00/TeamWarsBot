import discord
from discord.ext import commands
import json

class CoreCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """Displays when bot is ready"""
        # Uses self.bot.user to output discord tag of bot
        print(f'Logged on as {self.bot.user}')

    
    @commands.command()
    async def help(self, ctx):
        """Displays information about all commands in the bot"""

        # Create the embed, set up the title and description, as well as scarlet red color
        embed = discord.Embed(
            title="Help", description="RUCS24 Commands", color=0xFF0000
        )

        # Stores cog name and maps to all the functions
        cogs_dict = {}

        # Go through each command, access its name and docstring, add to embed
        for func in self.bot.walk_commands():
            # Adds the function to cogs_dict based on its cog
            try:
                cogs_dict[func.cog_name.lower()].append((func.name, func.help))
            except:
                cogs_dict[func.cog_name.lower()] = [(func.name, func.help)]

        description = ""

        # Create the description, add all the commands, and send the embed
        for cog in cogs_dict.keys():
            description += cog + "\n"

        embed = discord.Embed(title="Cog List", description=description, color=0xFF0000)
        await ctx.send(embed=embed)
        await ctx.send("Type the name of the cog you want to get help for!")

        def check(m):
            """Quick check to make sure only the person who requested help can respond"""
            return m.channel == ctx.channel and m.author == ctx.author

        # Wait for user cog choice
        msg = await self.bot.wait_for("message", check=check)

        # If they had an invalid cog, exit the function
        if msg.content.lower() not in cogs_dict.keys():
            await ctx.send("Not a valid cog")
            return

        # Add all commands for their chosen cog and output
        embed = discord.Embed(title=msg.content.capitalize(), description="Help")

        for command in cogs_dict[msg.content.lower()]:
            embed.add_field(name="-" + command[0], value=command[1], inline=False)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(CoreCog(bot))
