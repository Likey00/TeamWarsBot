import json
from discord.ext import commands

bot = commands.Bot(command_prefix = '-', help_command=None)

features = ['core', 'captain', 'admin']

for feature in features:
    bot.load_extension(f'cogs.{feature}cog');

with open('config.json', 'r') as f:
    config = json.load(f)

bot.run(config['token'])
