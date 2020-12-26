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

        if 'idToName' not in config:
            config['idToName'] = {}

        base_url = f'https://{config["username"]}:{config["apiKey"]}@api.challonge.com/v1/tournaments'
        
        try:
            async with self._session.post(f'{base_url}/{config["tourney"]}/participants.json', json={"name":team}) as resp:
                resp_json = await resp.json()
                if 'errors' in resp_json and 'Name has already been taken' in resp_json['errors']:
                    await ctx.send("Sorry, something went wrong! Check if the team was already confirmed and try again")
                    return

                config['captains'][team] = [ctx.author.id, resp_json['participant']['id']]
                config['idToName'][int(resp_json['participant']['id'])] = team

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


    @commands.command()
    async def update(self, ctx, *args):
        """Add a win for a given team"""
        team = ' '.join(args)

        with open('config.json', 'r') as f:
            config = json.load(f)

        if 'eliminated' not in config:
            config['eliminated'] = []

        if 'channel' not in config:
            await ctx.send("There is no match channel set! Ask an admin to set it using -set_match_channel!")
            return

        if team not in config['captains']:
            await ctx.send("Sorry, that's not a valid team name!")
            return

        if team in config['eliminated']:
            await ctx.send("Sorry, that team already lost! If there is a conflict ask an admin to reopen the match!")
            return
        
        team_id = config['captains'][team][1]
        match_id = config['nameToMatch'][team]
        base_url = f'https://{config["username"]}:{config["apiKey"]}@api.challonge.com/v1/tournaments'

        async with self._session.put(f'{base_url}/{config["tourney"]}/matches/{match_id}.json?match[scores_csv]=0-0&match[winner_id]={team_id}') as resp:
            resp_json = await resp.json()
            config['eliminated'].append(config['idToName'][str(resp_json['match']['loser_id'])])

        async with self._session.get(f'{base_url}/{config["tourney"]}/matches.json?state=open&participant_id={team_id}') as resp:
            resp_json = await resp.json()

        if len(resp_json):
            team1 = config['idToName'][str(resp_json[0]['match']['player1_id'])]
            team2 = config['idToName'][str(resp_json[0]['match']['player2_id'])]
            cap1 = self.bot.get_user(int(config['captains'][team1][0]))
            cap2 = self.bot.get_user(int(config['captains'][team2][0]))
            channel = discord.utils.get(ctx.guild.text_channels, name=config['channel'])

            if channel == None:
                await ctx.send("Match channel not found!")
                return

            config['nameToMatch'][team1] = resp_json[0]['match']['id']
            config['nameToMatch'][team2] = resp_json[0]['match']['id']

            await channel.send(f'{team1} ({cap1.mention}) vs {team2} ({cap2.mention})')

        else:
            await ctx.send("No new matches at this time. Thanks for updating!")

        with open('config.json', 'w') as f:
            json.dump(config, f)


def setup(bot):
    bot.add_cog(CaptainCog(bot))

