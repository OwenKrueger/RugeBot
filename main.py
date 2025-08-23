import discord
from discord.ext import commands
import random
import datetime
import calendar
import os
from dotenv import load_dotenv

# load ENV variables
load_dotenv('live.env')
client_secret = os.environ.get("CLIENT_SECRET")
bot_id = int(os.environ.get("BOT_ID"))
recruiting_criminals_channel_id = int(os.environ.get("RECRUITING_CRIMINALS_CHANNEL_ID"))
horde_guilds_channel_id = int(os.environ.get("HORDE_GUILDS_CHANNEL_ID"))

description = '''Keeping the mean streets of Orgrimmar safe by apprehending one criminal at a time'''

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

#replace with database/config file or something
sticky_channels_dict = {1373779217090875432}

bot = commands.Bot(command_prefix='?', description=description, intents=intents)

# Detects if someone is bumping ealy
async def post_limit_warden(message):
    if hasattr(message.channel, 'parent') and str(message.channel.parent) == "horde-guilds" and message.author.id != bot_id:
        channel = bot.get_channel(message.channel.id)
        #grab the last two messages in the channel history - one of them is this message
        async for historyMessage in channel.history(limit=2):
            #dont check the message that triggered the event - we want to look at the previous message
            if message.id != historyMessage.id:
                #if the last message in this channel is younger than the reset time - we have a violation - send a message to the report channel, and link to that message
                if historyMessage.created_at.timestamp() >= await get_weekly_reset_timestamp():
                    # TODO: create a function to build links for code reuse
                    reporting_channel = bot.get_channel(recruiting_criminals_channel_id)
                    res = "Criminal Scum Detected - Early Bump \n"
                    res += "https://discord.com/channels/"+str(message.guild.id)+"/"+str(message.channel.id)+"/"+str(message.id)
                    await reporting_channel.send(res)

async def get_weekly_reset_timestamp():
    #timestamp - TODO: This is using EST - but discord uses utc-0 for all timestamps.
    today = datetime.date.today()

    day_of_week = today.weekday()
    days_to_last_tuesday = (day_of_week - calendar.TUESDAY)

    last_tuesday = today - datetime.timedelta(days=days_to_last_tuesday)
    last_tuesday_midnight = datetime.datetime.combine(last_tuesday, datetime.time.min)
    weekly_reset_timestamp = last_tuesday_midnight.timestamp()
    return weekly_reset_timestamp

# detects if someone has two threads    
async def forum_limit_warden(message):
    # check that the post is within the horde-guilds section
    if hasattr(message.channel, 'parent') and str(message.channel.parent) == "horde-guilds" and message.author.id != bot_id:
        channel = bot.get_channel(horde_guilds_channel_id)
        # grab the thread associated with horde-guilds
        for thread in channel.threads:
            # check if the thread this message is being posted to is not the only thread owned by this user
            if thread.owner_id == message.author.id and thread.id != message.channel.id:
                res = "Criminal Scum Detected - Double Post \n"
                res += "https://discord.com/channels/"+str(message.guild.id)+"/"+str(thread.id)
                res += "\nhttps://discord.com/channels/"+str(message.guild.id)+"/"+str(message.channel.id)
                reporting_channel = bot.get_channel(recruiting_criminals_channel_id)
                await reporting_channel.send(res)
                #if we hit a sucessfull criminal there is no need to continue
                break

#setup event handlers for each message sent to the server
@bot.event
async def on_message(message):
    await post_limit_warden(message)
    await forum_limit_warden(message)

    # TODO: refactor and implement sticky channel feature
    if message.channel.id in sticky_channels_dict:
        if message.author.id != bot_id:
            channel = bot.get_channel(message.channel.id)
            async for message in channel.history(limit=5):
                if message.author.id == bot_id:
                    await message.delete()
            await channel.send("Sticky!");

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


@bot.command()
async def add(ctx, left: int, right: int):
    """Adds two numbers together."""
    await ctx.send(left + right)


@bot.command()
async def roll(ctx, dice: str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await ctx.send('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await ctx.send(result)


@bot.command(description='For when you wanna settle the score some other way')
async def choose(ctx, *choices: str):
    """Chooses between multiple choices."""
    await ctx.send(random.choice(choices))


@bot.command()
async def repeat(ctx, times: int, content='repeating...'):
    """Repeats a message multiple times."""
    for i in range(times):
        await ctx.send(content)


@bot.command()
async def joined(ctx, member: discord.Member):
    """Says when a member joined."""
    await ctx.send(f'{member.name} joined {discord.utils.format_dt(member.joined_at)}')


@bot.group()
async def cool(ctx):
    """Says if a user is cool.

    In reality this just checks if a subcommand is being invoked.
    """
    if ctx.invoked_subcommand is None:
        await ctx.send(f'No, {ctx.subcommand_passed} is not cool')


@cool.command(name='bot')
async def _bot(ctx):
    """Is the bot cool?"""
    await ctx.send('Yes, the bot is cool.')

bot.run(client_secret) 