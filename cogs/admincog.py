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
        config['idToName'] = {}
        config['nameToMatch'] = {}
        config['eliminated'] = []

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
        base_url = f'https://{config["username"]}:{config["apiKey"]}@api.challonge.com/v1/tournaments'

        try:
            async with self._session.delete(f'{base_url}/{config["tourney"]}/participants/{participant_id}.json') as resp:
                pass
        except:
            await ctx.send("Sorry, something went wrong! Try again")
            return

        config['captains'].pop(team)
        config['idToName'].pop(str(participant_id))

        with open('config.json', 'w') as f:
            json.dump(config, f)

        await ctx.send(f'{team} successfully deleted!')

    @commands.command()
    @commands.has_role("Bot Commander")
    async def start(self, ctx):
        """Starts the tournament"""
        with open('config.json', 'r') as f:
            config = json.load(f)

        base_url = f'https://{config["username"]}:{config["apiKey"]}@api.challonge.com/v1/tournaments'

        try:
            async with self._session.post(f'{base_url}/{config["tourney"]}/start.json') as resp:
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

        base_url = f'https://{config["username"]}:{config["apiKey"]}@api.challonge.com/v1/tournaments'
        
        try:
            async with self._session.post(f'{base_url}/{config["tourney"]}/reset.json') as resp:
                pass
        except:
            await ctx.send("Sorry, something went wrong! Try again")
            return

        await ctx.send("Tournament reset!")


    @commands.command()
    @commands.has_role("Bot Commander")
    async def make_matches(self, ctx):
        """Outputs all the initial matches"""
        with open('config.json', 'r') as f:
            config = json.load(f)

        if 'nameToMatch' not in config:
            config['nameToMatch'] = {}

        base_url = f'https://{config["username"]}:{config["apiKey"]}@api.challonge.com/v1/tournaments'

        async with self._session.get(f'{base_url}/{config["tourney"]}/matches.json') as resp:
            resp_json = await resp.json()

            for entry in resp_json:
                if entry["match"]["state"] != "open":
                    continue

                team1_id = str(entry["match"]["player1_id"])
                team2_id = str(entry["match"]["player2_id"])
                team1 = config['idToName'][team1_id]
                team2 = config['idToName'][team2_id]

                config['nameToMatch'][team1] = entry["match"]["id"]
                config['nameToMatch'][team2] = entry["match"]["id"]

                cap1 = self.bot.get_user(int(config['captains'][team1][0]))
                cap2 = self.bot.get_user(int(config['captains'][team2][0]))
                    
                await ctx.send(f'{team1} ({cap1.mention}) vs {team2} ({cap2.mention})')


        with open('config.json', 'w') as f:
            json.dump(config, f)

    @commands.command()
    @commands.has_role("Bot Commander")
    async def set_match_channel(self, ctx, channel_name):
        """Sets up the channel where matches are announced given channel name"""
        with open('config.json', 'r') as f:
            config = json.load(f)

        config['channel'] = channel_name

        with open('config.json', 'w') as f:
            json.dump(config, f)

        await ctx.send("Successfully updated match channel!")

def setup(bot):
    bot.add_cog(AdminCog(bot))
