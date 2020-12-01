import discord
from discord.ext import commands
import json
import aiohttp
import asyncio

class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._loop = asyncio.get_event_loop()
        self._session = aiohttp.ClientSession(loop=self._loop)


    @commands.command()
    @commands.has_role("Bot Commander")
    async def set_tourney(self, ctx, code):
        """Update the tourney currently serviced by the bot, takes in tourney url code (part after challonge.com/)"""

        # Simply loads config, updates tourney, and dumps it back
        with open('config.json', 'r') as f:
            config = json.load(f)

        config['tourney'] = code
        config['captains'] = {}

        with open('config.json', 'w') as f:
            json.dump(config, f)

        await ctx.send("Tourney updated!")

    @commands.command()
    @commands.has_role("Bot Commander")
    async def remove(self, ctx, *args):
        """Removes the specified team from the bracket"""
        team = ' '.join(args)

        with open('config.json', 'r') as f:
            config = json.load(f)

        if team not in config['captains']:
            await ctx.send("Sorry, that's not a valid team name!")
            return

        participant_id = config['captains'][team][1]

        try:
            async with self._session.delete(f'https://{config["username"]}:{config["apiKey"]}@api.challonge.com/v1/tournaments/{config["tourney"]}/participants/{participant_id}.json') as resp:
                pass
        except:
            await ctx.send("Sorry, something went wrong! Try again")
            return

        config['captains'].pop(team)

        with open('config.json', 'w') as f:
            json.dump(config, f)

        await ctx.send(f'{team} successfully deleted!')

    @commands.command()
    @commands.has_role("Bot Commander")
    async def start(self, ctx):
        """Starts the tournament"""
        with open('config.json', 'r') as f:
            config = json.load(f)

        try:
            async with self._session.post(f'https://{config["username"]}:{config["apiKey"]}@api.challonge.com/v1/tournaments/{config["tourney"]}/start.json') as resp:
                pass
        except:
            await ctx.send("Sorry, something went wrong! Try again")
            return

        await ctx.send("Tournament started!")

    @commands.command()
    @commands.has_role("Bot Commander")
    async def reset(self, ctx):
        """Resets the tournament"""
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        try:
            async with self._session.post(f'https://{config["username"]}:{config["apiKey"]}@api.challonge.com/v1/tournaments/{config["tourney"]}/reset.json') as resp:
                pass
        except:
            await ctx.send("Sorry, something went wrong! Try again")
            return

        await ctx.send("Tournament reset!")


def setup(bot):
    bot.add_cog(AdminCog(bot))
