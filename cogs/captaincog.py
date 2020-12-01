import discord
from discord.ext import commands
import json
import aiohttp
import asyncio

class CaptainCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._loop = asyncio.get_event_loop()
        self._session = aiohttp.ClientSession(loop=self._loop)

    @commands.command()
    async def confirm(self, ctx, *args):
        """Final stage of registration, only the team captain must -confirm Team Name"""
        team = ' '.join(args)

        with open('config.json', 'r') as f:
            config = json.load(f)

        if 'captains' not in config:
            config['captains'] = {}

        
        try:
            async with self._session.post(f'https://{config["username"]}:{config["apiKey"]}@api.challonge.com/v1/tournaments/{config["tourney"]}/participants.json', json={"name":team}) as resp:
                resp_json = await resp.json()
                if 'errors' in resp_json and 'Name has already been taken' in resp_json['errors']:
                    await ctx.send("Sorry, something went wrong! Check if the team was already confirmed and try again")
                    return

                config['captains'][team] = [ctx.author.id, resp_json['participant']['id']]

        except:
            await ctx.send("Sorry, something went wrong! Try again")
            return

        with open('config.json', 'w') as f:
            json.dump(config, f)

        await ctx.send(f'{team} successfully added!')


    @commands.command()
    async def captain(self, ctx, *args):
        """See the captain of the given team"""
        team = ' '.join(args)

        with open('config.json', 'r') as f:
            config = json.load(f)

        if team not in config['captains']:
            await ctx.send("Sorry, that's not a valid team name!")
            return

        user = self.bot.get_user(int(config['captains'][team][0]))

        embed = discord.Embed(title='Captain of ' + team, description=user.mention, color=0x0080ff)
        await ctx.channel.send(embed=embed)


def setup(bot):
    bot.add_cog(CaptainCog(bot))

