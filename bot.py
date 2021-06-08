# bot.py
import os
import time

import discord
import asyncio
from dotenv import load_dotenv
from re import search
import requests
from random import randint, randrange
import json
from loggingChannel import sendLog

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
apikey = os.getenv('TENOR_API_KEY')

intents = discord.Intents.all()
client = discord.Client(intents=intents)


class User:
    def __init__(self, name, coding, myid, timer):
        self.name = name
        self.coding = coding
        self.myid = myid
        self.timer = timer


users = []
MAX_TIME = 1801  # 1801
TIME_RESET_AT = 300
timeReset = 0
channel = ""


@client.event
async def on_ready():
    # Vars
    global users
    global MAX_TIME
    global TIME_RESET_AT
    global timeReset
    global channel

    users.append(User('Geoffery10', False, '<@253710834553847808>', 0))
    users.append(User('Connor', False, '<@251488731750465536>', 0))

    channel = client.get_channel(786751239613579305)  # work-time
    loggingchannel = client.get_channel(789224794334953474)

    # Loaded
    print(f'{client.user} has connected to Discord!')
    print(await sendLog(log=(f'I\'ve reconnected to Discord!'), client=client))
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="your Health"))

    # Check for coding activity
    while True:
        for user in users:
            if user.coding:
                seconds = user.timer % (24 * 3600)
                hour = seconds // 3600
                seconds %= 3600
                minutes = seconds // 60
                seconds %= 60
                user.timer = user.timer + 1
                print("Timer:", user.timer)
                if user.timer >= MAX_TIME:
                    await channel.send(
                        'Hey onii-san %s, you should take a break. It\'s been about %d minutes.' % (
                            user.myid, minutes), tts=True)
                    await sendGif(channel, "cute anime girl", random=True)
                    user.timer = 0
                elif user.timer == int(MAX_TIME / 2):
                    await channel.send(
                        'Hello onii-san %s, you are about half way to your next break.' % user.myid,
                        tts=True)
                '''
                else:
                    if timeReset >= TIME_RESET_AT:
                        timer = 0
                        timeReset = 0
                    else:
                        timeReset = timeReset + 1
                '''
            await asyncio.sleep(1)


async def sendGif(channel, search_term, random):
    # gif start
    lmt = 50
    url = "https://api.tenor.com/v1/search?q="
    if random:
        url = "https://api.tenor.com/v1/random?q="
        lmt = 1
    r = requests.get(url + ("%s&key=%s&limit=%s" % (search_term, apikey, lmt)))
    if r.status_code == 200:
        # load the GIFs using the urls for the smaller GIF sizes
        top_gifs = json.loads(r.content)
        # print(top_gifs)
        selected_gif = top_gifs['results'][randrange(lmt)]
        print(await sendLog(log=("Gif selected " + selected_gif["url"]), client=client))
        await channel.send(selected_gif["url"])
    else:
        top_8gifs = None


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Vars
    global users
    global MAX_TIME
    global TIME_RESET_AT
    global timeReset
    global channel

    mentions = message.mentions
    if len(mentions) > 0:
        if mentions[0].id == 786698404927504385:
            if search("^!quit", message.content.lower()) and message.channel == client.get_channel(789190323326025789):
                await client.logout()
            else:
                if search("^!punch", message.content.lower()) and mentions[0].id == client.user.id:
                    await sendGif(message.channel, "crying anime girl", random=False)
                else:
                    await sendGif(message.channel, "cute anime girl", random=True)
                print(await sendLog(log=("Sent by: " + message.author.name + "\tID: " + str(message.author.id)),
                                    client=client))

    if search(("/(^.*\soof$)|(^oof\s.*)|(^oof$)|(^.*\soof\s.*$)/i"), message.content.lower()):
        if randint(0, 9) >= 6:
            await sendGif(message.channel, "oof", False)
            print(await sendLog(log=("Sent by: " + message.author.name + "\tID: " + str(message.author.id)), client=client))

    if message.author.id == 253710834553847808 or message.author.id == 251488731750465536:
        if message.author.id == 253710834553847808:
            user = users[0]
        else:
            user = users[1]
        if search("^!code", message.content):
            print(await sendLog(log=f"Started/Stopped Code Timer for: {user.name}\tID: {str(message.author.id)}",
                                client=client))
            # Start timer
            if user.coding:
                user.timer = 0
                user.coding = False
                await message.channel.send('Alright %s I stopped your break timer.' % user.myid)
            else:
                user.coding = True
                user.timer = 0
                await message.channel.send('Okay %s I started your break timer!' % user.myid)
                print("The Half Timer is set to:", int(MAX_TIME / 2))
                print("The Final Timer is set to:", MAX_TIME)
            try:
                await message.delete()
            except:
                print(await sendLog(log=("Failed to delete " + message.content), client=client))

        if search("^!time", message.content):
            # Get timer
            seconds = user.timer % (24 * 3600)
            hour = seconds // 3600
            seconds %= 3600
            minutes = seconds // 60
            seconds %= 60
            secondsMAX = MAX_TIME % (24 * 3600)
            hourMAX = secondsMAX // 3600
            secondsMAX %= 3600
            minutesMAX = secondsMAX // 60
            secondsMAX %= 60
            if minutes > 0:
                await message.channel.send('Your time is %d mins out of %d mins' % (minutes, minutesMAX))
            else:
                await message.channel.send('Your time is %d secs out of %d mins' % (seconds, minutesMAX))
            await sendGif(message.channel, "cute anime tired", random=True)
            try:
                await message.delete()
            except:
                print(await sendLog(log=("Failed to delete " + message.content), client=client))


client.run(TOKEN)
