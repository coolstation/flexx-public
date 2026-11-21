#!/bin/env python

# The main Flexx discrod bot...

import json
import random
import datetime
import asyncio,threading
import os, sys, signal
import subprocess
from http.server import ThreadingHTTPServer
import urllib.parse
import byond.topic
import discord
from discord.ext import commands
import helpers
import markov
from bridg import BridgeServer
import intertwingle

# boot up activities

h = helpers.Helpers()
h.logger("Starting up.", "Info")
# settings and api keys oh my
conf_file = open("config//config_secret.json", "rt+")
config = json.load(conf_file)
conf_file.close()
# create the markov chainer
m = markov.MarkovChainer(2)
h.markov_startup(m)
# create the bot object
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$',intents=intents)

################################################################################
# on_ready: fired when the bot is connected, the API is responding, etc.
################################################################################

@bot.event
async def on_ready():
    print("Vaporwave George FLEXtanza has logged the fuck in.")
    h.logger("Startup: The bot is alive with the sounds of music. Connected to Discord API on "
             + str(datetime.datetime.now()), "Disc")

    # horrible global var stuff
    intertwingle.setLoop(asyncio.get_running_loop())
    intertwingle.setLogger(h)

    # Clear our announce lockout flags
    # 2026-11-21 (Tamber): I don't think I ever made any of this work, lmao.
    intertwingle.resetAnnounceFlags()

    # Channels for game event-log and ahelp/mentor-helps.
    # These have to be specified by giving the ID of the respective channel. Sorry -.-
    config = intertwingle.getConfig()
    if "butt_events" in config:
        bot.eventsLog = bot.get_channel(int(config['butt_events']))
        h.logger('Events log channel: {0}'.format(bot.eventsLog.name), "Disc")
    else:
        bot.eventsLog = None
    if "ahelp_zone" in config:
        bot.ahelpZone = bot.get_channel(int(config['ahelp_zone']))
        h.logger('Admin channel: {0}'.format(bot.ahelpZone.name), "Disc")
    else:
        bot.ahelpZone = None
    if "mhelp_zone" in config:
        bot.mhelpZone = bot.get_channel(int(config['mhelp_zone']))
        h.logger('Mentor channel: {0}'.format(bot.mhelpZone.name), "Disc")
    else:
        bot.mhelpZone = None

    if "jetsam_chan" in config:
        bot.jetsam_chan = bot.get_channel(int(config['jetsam_chan']))
        h.logger('Jetsam channel: {0}'.format(bot.jetsam_chan.name))

    if "playtest_chan" in config:
        bot.playtest_chan = bot.get_channel(int(config['playtest_chan']))
        h.logger('Playtest channel: {0}'.format(bot.playtest_chan.name))

    if "codre_chan" in config:
        bot.codre_chan = bot.get_channel(int(config['codre_chan']))
        h.logger('Codre channel: {0}'.format(bot.codre_chan.name))

    if "the_team" in config:
        bot.the_team = config['the_team']

    if "codre_id" in config:
        bot.codre_id = config['codre_id']

    if "mentaurs" in config:
        bot.mentaurs = config['mentaurs']

    if "status_server_address_dev" in config:
        bot.status_server_address_dev = config['status_server_address_dev']

    if "status_server_port_dev" in config:
        bot.status_server_port_dev = config['status_server_port_dev']

    if "status_server_address_pud" in config:
        bot.status_server_address_pud = config['status_server_address_pud']

    if "status_server_port_pud" in config:
        bot.status_server_port_pud = config['status_server_port_pud']


    h.logger("Annoy the secret coders channel on returning", "Disc")
    await bot.jetsam_chan.send(random.choice(["sup nerds",
                                              "am back",
                                              "is this videogames?",
                                              "im coder"]))

#-------------------------------------------------------------------------------
#                 on_disconnect: Just a debugging/logging thing.
#-------------------------------------------------------------------------------
@bot.event
async def on_disconnect():
    h.logger("The bot has disconnected from discord... This could be because the script failed in a fatal way, "
             "or a connection issue", "Warn")

################################################################################
#                              Commands
################################################################################

@bot.command(brief='Test command, please ignore',
             help="I don't really know what you want from me.")
async def test(ctx, arg):
    # Quick loopback test item.
    await ctx.message.add_reaction('\N{THUMBS UP SIGN}')
    await ctx.send(arg)

#-------------------------------------------------------------------------------
# Shut the bot down to pick up code changes n stuff.
#-------------------------------------------------------------------------------
@bot.command(name='naptime', brief="Shuts down the bot",
             help="Nerd use only. Shuts down the flexx process. He should be back within a couple of minutes.",
             usage="")
async def naptime(ctx):
    role=discord.utils.get(ctx.guild.roles, id = int(bot.the_team))
    if role in ctx.author.roles:
        h.logger("bot shutdown requested", "Disc")
        await ctx.message.reply("Aww, okay.")
        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')
        await asyncio.sleep(5) # give time for the reply to make it thru
        await bot.jetsam_chan.send("shutting down")
        await DOINK()
    else:
        await ctx.message.reply("YOUR NOT MY MOM!")
        await ctx.message.add_reaction('\U0001F595')

async def DOINK():
    os.kill(os.getpid(), signal.SIGHUP)

#-------------------------------------------------------------------------------
# Change/check the 'order' of Flexx's word association.
#-------------------------------------------------------------------------------
@bot.command(name='order', brief="Change/check order value for markov chain",
             help="Nerd use only. Changes/checks the value that determines the distance between words Flexx processes.",
             usage="")
async def order_req(ctx, *args):
    """Sends request to Flexx to change his order value"""
    role=discord.utils.get(ctx.guild.roles, id = int(bot.the_team))
    if role in ctx.author.roles:
        if args:
            h.logger("order change requested", "Disc")
            await ctx.message.reply("orders received")
            await ctx.message.add_reaction('\N{THUMBS UP SIGN}')
            await asyncio.sleep(5)
            await bot.jetsam_chan.send("changing order")
            await order_set(int(args[0]))
        else:
            h.logger("order check requested", "Disc")
            await ctx.message.add_reaction('\N{THUMBS UP SIGN}')
            await asyncio.sleep(5)
            order = await order_get()
            await ctx.message.reply(f"I'm feeling about a {order}, doc")
    else:
        await ctx.message.reply("YOUR NOT MY MOM!")
        await ctx.message.add_reaction('\U0001F595')

async def order_set(order):
    """Calls Flexx's order setter"""
    try:
        m.set_order(order)
    except ValueError:
        h.logger("Failed to change order, value <= 1", "Disc")

async def order_get():
    """Calls Flexx's order getter"""
    return m.get_order()
#-------------------------------------------------------------------------------
# Clean up the log file.
#-------------------------------------------------------------------------------
@bot.command(name='flush', brief="Clean up the log file",
             help="Removes log entries older than 14 days.",
             usage="")
async def flush(ctx):
    role=discord.utils.get(ctx.guild.roles, id = int(bot.the_team))
    if role in ctx.author.roles:
        await ctx.message.reply("On it!")
        h.log_flusher()
        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')
        await bot.jetsam_chan.send("Flushing my logs!")
    else:
        await ctx.message.reply("If it's yellow let it mellow or whatever")
        await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')

#-------------------------------------------------------------------------------
# Have Flexx D.C. perform the art of chiropractic.
#-------------------------------------------------------------------------------
@bot.command(name='crack', brief='Spinal manipulation',
             help='Flexx will perform the art of chiropractic upon',
              usage="")
async def crack(ctx):
    await ctx.message.reply(random.choice(["alright hold still...this is mostly safe",
                                           "you already signed that waiver, yeah?",
                                           "just relax pal let ol' flexxy grease your pain",
                                           "ah yeah dude your cartilagenous feng shui is all, like, congested, i think",
                                           "aw yeah this is your lucky day i got my magnets and everything",
                                           "whoa shgit buddy youre full of thebans!!! let me help you out"]))
    await ctx.message.add_reaction('\N{BONE}')
    async with ctx.channel.typing():
        await asyncio.sleep(random.randint(3,6))
    await ctx.send(random.choice(["don't worry, i went to the Palmer School",
                                  "hey i learned this one from a goast",
                                  "a bee taught me this little number...",
                                  "this technique was revealed to me in a dream",
                                  "hey uh, you got insurance for like, going to the real doctors too, right? Just asking, No reason,",
                                  "the philosophy of chiropractic knowledge is founded upon the knowledge of the manner in which a vital functions are performed by innate in health and disease when controlling intelligence is able to transmit mental impulses to all parts of the body free and unobstructed we have normal action which is health",
                                  "life is like the expression of spirit through matter so to make life manifest requires the union of spirit and body or something"]))
    async with ctx.channel.typing():
        await asyncio.sleep(random.randint(3,6))
    # Nick scrundling

    if ctx.author.nick is None:
        name_nick = ctx.author.name
        h.logger(name_nick + " has no nickname!", "Disc")
        #ctx.author.edit(nick = name_nick)

    target_nick = ctx.author.nick
    spinedex = random.randint(1,(len(target_nick)-1))
    new_nick = target_nick[:spinedex] + (random.choice(["-", " ", ";", ":", "_", ",", "~"])) + target_nick[spinedex:]
    try:
        await ctx.author.edit(nick=new_nick, reason="because funny")
    except:
        # Failed to change nick. Probably because of permissions.
        await ctx.send(random.choice(["...mama mia, them's some strong bones!",
                                              "ow my fingers, what the hell?!",
                                              "look, i'm gonna be straight with ya, i think i broke something",
                                              "THAT AINT RIGHT!",
                                              "oh ow ow ouch fuck... call a doctor, i think i pulled something"]))
    else:
        # Success
        await ctx.send(random.choice(["***CRACK!!!***",
                                      "***CRONCH!!!***",
                                      "***CRACK!!!***",
                                      "***CRUNK!!!***",
                                      "***CRACK!!!***"]))
        async with ctx.channel.typing():
            await asyncio.sleep(random.randint(2,4))
        await ctx.send(random.choice(["there ya go, good as new",
                                      "hey your neck was 100 percent doin that before",
                                      "feels pretty great huh, if not i'll just do it again until it does",
                                      "oh fuck",
                                      "whoops",
                                      "ope- i mean, belissimo!",
                                      "shit wait oh god hey you're not dead are you",
                                      "5000 credits please"]))

#-------------------------------------------------------------------------------
# Shut the dreamdaemon server instance down right now.
#-------------------------------------------------------------------------------
@bot.command(name='kill', brief="Shuts down DreamDaemon instance.",
             help="Nerd use only. Hard shuts down the DreamDaemon process. The server should restart automatically within a couple of minutes.",
             usage="")
@commands.cooldown(1, 150) # 1 use every 2.5 minutes
async def dm_kill(ctx):
    role=discord.utils.get(ctx.guild.roles, id = int(bot.codre_id))
    if role in ctx.author.roles:
        h.logger("Dreamworld shutdown requested", "Disc")
        # fire up pgrep. Check for a process named *exactly* "DreamDaemon".
        greppy = await asyncio.create_subprocess_exec("/usr/bin/pgrep", "-x", "DreamDaemon", stdout=asyncio.subprocess.PIPE)
        (reslut, garbo) = await greppy.communicate() # unused garbo var to throw away part of the return.
        h.logger("Taking an axe to proc: '{0}'".format(int(reslut)), "Disc")
        # There's a non-breaking space below.
        await ctx.message.reply(" \n**BORN TO DIE**\nWORLD IS A FUCK\nKill Em All 1989\nI am trash man\n{0} dead cops".format(int(reslut)))
        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')
        await bot.jetsam_chan.send("killing dreamdaemon")
        await asyncio.sleep(5)
        os.kill(int(reslut), signal.SIGKILL)
    else:
        await ctx.message.reply(random.choice(["*bounces up and down* kill! kill! KILL! KILL! **KILL**!",
                                               "Nah. don't feel like it.",
                                               "How bout I just squosh u?",
                                               "make me",
                                               "do it urself asshole",
                                               # you can get anythin you want, at Alice's Restaurant~
                                               "...and we was both jumpin up and down yellin \"KILL, KILL!\", an the sargent came over, pinned a medal on me, sent me down the hall an said \"yer our boy!\".\nDidn't feel too good about it."]))
        await ctx.message.add_reaction('\U0001F595')

#-------------------------------------------------------------------------------
# Call the fusilli build-script. If success, then it's juicy; if
# there's a failure, it returns the error code from the script, which
# should give a hint as to where it failed.  Limited to coder dweebs
# only.
# 1: git pull failed
# 2: DreamMaker failed
# 3: NPM failure
# 4: *Grunt*
# 5: zip for RSC
# 6: rsync: browser assets to CDN
# 7: rsync: RSC to CDN
#
# On error, upload the build log file to #secret-coders
# -------------------------------------------------------------------------------
@bot.command(name='build', brief="Update the game server to the latest coad.",
             help="Codre use only. Fires off the script to fetch and build the latest game code, to be ready to run for the next round.",
             usage="")
@commands.max_concurrency(1, wait=False)
async def build(ctx):
    role = discord.utils.get(ctx.guild.roles, id = int(bot.codre_id))
    if role in ctx.author.roles:
        h.logger("Running build-script", "Disc")
        await ctx.send("alright gimme a minute.")
        async with ctx.channel.typing():
            reslut = await asyncio.create_subprocess_exec("/home/ss13/coolstructure/buildfusilli.sh")
            await reslut.wait()
            if reslut.returncode == 0:
                await ctx.message.reply("codemeat doneness: " + random.choice(["medium-rare.",
                                                                               "about medium.",
                                                                               "a little rare.",
                                                                               "pittsburgh blue.",
                                                                               "medium well. (that's good)",
                                                                               "medium well. (that's bad)",
                                                                               "hotdog.",
                                                                               "mince.",
                                                                               "donk.",
                                                                               "not well.",
                                                                               "not bad?",
                                                                               "well done.",
                                                                               "holo-foil ultra-rare!!1!",
                                                                               "undone.",
                                                                               "special.",
                                                                               "wet.",
                                                                               "sopping.",
                                                                               "greezy.",
                                                                               "skunked up",
                                                                               "spoghetti? spagtetinie??",
                                                                               "dripping wet...",
                                                                               "hammed up!",
                                                                               "passably crispy?",
                                                                               "compleat.",
                                                                               "it's all subjective, right?",
                                                                               "poached.",
                                                                               "right out of the can.",
                                                                               "balled up.",
                                                                               "normal.",
                                                                               "abnormal.",
                                                                               "congratulations.",
                                                                               "boner pills",
                                                                               "boaner pills"]))
                await ctx.message.add_reaction('\N{THUMBS UP SIGN}')
            else:
                await ctx.message.reply(random.choice(["ah fuck it's waaay overdone... no good... ",
                                                       "...what did it ever do to you?",
                                                       "...you sure yer not British, bud? 'cause *wow*...",
                                                       "oh my favorite... charcoal...",
                                                       "...\n . . .\n *holy fuck*",
                                                       "Im not eating that...",
                                                       "...well done \U0001F62C"]))
                await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')
                rtcode = reslut.returncode
                what_happen = "Okay, so, what happened was:\n"
                what_happen += "Git fetch {0}\n".format(("went ok","fucked up")[rtcode==1])
                if rtcode > 1:
                    what_happen += "DME compile {0}\n".format(("fucken aced","sucked")[rtcode==2])
                if rtcode > 2:
                    what_happen += "NPM {0}\n".format(("did its thing","blew up")[rtcode==3])
                if rtcode > 3:
                    what_happen += "Grunt: {0}\n".format(("\N{THUMBS UP SIGN}","\U0001F4A9")[rtcode==4])
                if rtcode > 4:
                    what_happen += "Zip{0}\n".format(("ped up!"," caught some hairs. ow.")[rtcode==5])
                if rtcode > 5:
                    what_happen += "Assets {0}\n".format(("made it down the tube","got stuck")[rtcode==6])
                if rtcode > 6:
                    what_happen += "RSC {0}\n".format(("also made it down the tube","got stuck. get a plunger!")[rtcode==7])

                what_happen += "(I send the full log to the printer in the coders closet, if u kno what I mean)"

                await ctx.message.reply(what_happen)

                # upload to secret-coders

                await bot.codre_chan.send(file=discord.File("/home/ss13/coolserv/buildlog.txt"),
                                      content="okay, well, heres what I think went wrong...")
                # reset cooldown.
                ctx.command.reset_cooldown(ctx)
    else:
        await ctx.send(random.choice(["fuck off i don't know you.",
                                      "what, gonna give me some legos too?",
                                      "yeah, sure, maybe when you sign the checks."
                                      ]))
        await ctx.message.add_reaction('\U0001F595')
        # reset cooldown
        ctx.command.reset_cooldown(ctx)

#-------------------------------------------------------------------------------
# Call the webserver update script. If success, then it's juicy; if
# there's a failure, it returns the error code from the script, which
# should give a hint as to where it failed.  Limited to coder dweebs
# only.
# 1: git pull failed
# 2: rsync failed
# -------------------------------------------------------------------------------
@bot.command(aliases=['gweb','updatesite','gowebgo','buildweb'], brief="Update the website.",
             help="Propagandist use only. Updates the website.",
             usage="")
@commands.max_concurrency(1, wait=False)
async def buildwebsite(ctx):
    role = discord.utils.get(ctx.guild.roles, id = int(bot.the_team))
    if role in ctx.author.roles:
        h.logger("Running update-script", "Disc")
        await ctx.send("alright gimme a second.")
        async with ctx.channel.typing():
            reslut = await asyncio.create_subprocess_exec("/home/ss13/coolstructure/updatewebsite.sh")
            await reslut.wait()
            if reslut.returncode == 0:
                await ctx.message.reply(random.choice(["zoo wee mama im computer!",
                                                        "load bearing whitespace.",
                                                        "your the sysadmin, not me.",
                                                        "you can do anything, at coolstation space.",
                                                        "oh Fuck Off about you,re shitcoints, ok",
                                                        "web net.",
                                                        "post hog",
                                                        "actually, what you're refering to as gweb is actually GNU/gweb, or as I like to call it, GNU *plus* gweb, merely part of an ecosystem of commands that make up the Giucer Nerd Ubercomp operating system.",
                                                        "pregnant sonic adventure blog",
                                                        "100% tested no virus!!!! "]))
                await ctx.message.add_reaction('\N{THUMBS UP SIGN}')
            else:
                await ctx.message.reply(random.choice(["That went bad.",
                                                       "That went real bad.",
                                                       "Posting is cancelled sorry.",
                                                       "poast hog? roast hog"]))
                await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')
                await ctx.send("String Cheese" + str(reslut.returncode) + " Marmalade")
    else:
        await ctx.send(random.choice(["fuck off i don't know you.",
                                      "I aint gonna update yer sonic mpreg page for ya, dude"]))
        await ctx.message.add_reaction('\U0001F595')
# ------------------------------------------------------------------------------
# Call the discord bot update script. If success, it's all good. If not, uhhh. yeah.
# Limited to codre dweebs.
# return codes:
# 0: all good
# 1: git pull failed
# ------------------------------------------------------------------------------
@bot.command(name='flexxup', brief="Update the bot coad")
@commands.max_concurrency(1, wait=False)
async def flexxbuild(ctx):
    role = discord.utils.get(ctx.guild.roles, id = int(bot.codre_id))
    if role in ctx.author.roles:
        h.logger("Rebuilding the bot.", "Disc")
        async with ctx.channel.typing():
            reslut = await asyncio.create_subprocess_exec("/home/ss13/coolstructure/updateflexx.sh")
            await reslut.wait()
            if reslut.returncode == 0:
                await ctx.message.reply("Feelin' good, doc!")
                await ctx.message.add_reaction('\N{THUMBS UP SIGN}')
                await bot.jetsam_chan.send("updating & restarting botte")
                await asyncio.sleep(5)
                await DOINK()
            else:
                await ctx.message.reply(random.choice(["...you did wash your hands first, right? Like, with soap?",
                                                       "i dont feel so good, doc...",
                                                       "the squidgy bits connected to the red thing, the red thing's attached to your... wrist-watch! ... uhoh"]))
                await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')
    else:
        await ctx.send(random.choice(["fuck off i dont know you",
                                      "put that fucken scalpel down, dude..."]))
        await ctx.message.add_reaction('\U0001F595')

#-------------------------------------------------------------------------------
# Call the script update script.
# Libited to codre dweebs
# return codes:
# 0: all good
# 1: git pull failed
#-------------------------------------------------------------------------------

@bot.command(name='scriptup', brief="Update the infrastructure scripts",
             help="Codre use only. Runs the script to update the scripts, including updating the script that updates the scripts.",
             usage="")
@commands.max_concurrency(1, wait=False)
async def scriptup(ctx):
    role = discord.utils.get(ctx.guild.roles, id = int(bot.codre_id))
    if role in ctx.author.roles:
        h.logger("Updating the infra scripts", "Disc")
        async with ctx.channel.typing():
            reslut = await asyncio.create_subprocess_exec("/home/ss13/coolstructure/updatescripts.sh")
            await reslut.wait()
            if(reslut.returncode==0):
                await ctx.message.reply("Im in \U0001F60E")
                await ctx.message.add_reaction('\N{THUMBS UP SIGN}')
                await bot.jetsam_chan.send("upderted scritps")
            else:
                await ctx.message.reply(random.choice(["I guess they call you Count Zero, 'cause zero of that worked",
                                                       "...scriptdown, dude",
                                                       "Guess not."]))
                await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')
    else:
        await ctx.message.reply(random.choice(["gonna hack the gibson next, huh, ya big goob?",
                                               "No, I don't think I will.",
                                               "HEY, WE GOTTA FOSSIE HERE!"]))
        await ctx.message.add_reaction('\U0001F595')

async def checkstatus_core(server, port, pud_or_dev, ctx):
    h.logger(f"Checking gameserver status {server}:{port}", "Disc")
    async with ctx.channel.typing():
        loop = asyncio.get_running_loop()
        try:
            worldstatus = await loop.run_in_executor(None, byond.topic.queryStatus, server, port)
            if worldstatus:
                gamedesc = "{0} round on {1}, with {2} juicer{3} playing!".format(
                    worldstatus['mode'][0], worldstatus['map_name'][0], worldstatus['players'][0],
                    ("" if (int(worldstatus['players'][0]) == 1) else "s"))
                statusCard = discord.Embed(title = "Things on '{0}'".format(worldstatus['station_name'][0]),
                                           description=gamedesc,
                                           color = discord.Color.blue(),
                                           url=f"https://{pud_or_dev}.coolstation.space/")
                statusCard.set_footer(text=random.choice(intertwingle.getConfig()["taglines"]))
                await ctx.message.reply(embed=statusCard)
                await ctx.message.add_reaction('\N{THUMBS UP SIGN}')
            else:
                await ctx.message.reply("I, uh... can't tell what's going on.")
                await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')
        except:
            await ctx.message.reply("I went to check and something stopped working, and there's some weird noises and stuff.")
            h.logger("Hey! Shit's fucked: {0}".format(sys.exc_info()[1]), "Warn")
            await bot.jetsam_chan.send("Hey, they said I'm excetpional!\n {0}".format(sys.exc_info()[1]))
            await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')


#-------------------------------------------------------------------------------
# Pokes the game server to request the status of the world, via a
# Topic call, and pretty-print it.
# -------------------------------------------------------------------------------
@bot.command(name='status1', brief="Check the status of the game world on the dev server",
             help="And I take a deep breath and I get real high; And I scream at the top of my lungs; What's going on?",
             usage="")
@commands.cooldown(1, 20) # 1 use every 20 seconds
async def checkstatus_dev(ctx):
    await ctx.message.reply("Checking dev server.")
    await checkstatus_core(bot.status_server_address_dev, bot.status_server_port_dev, 'connect', ctx)

@bot.command(name='status2', brief="Check the status of the game world on the live server",
             help="The fuck's going on in here?",
             usage="",
             aliases=['status'])
@commands.cooldown(1, 20)
async def checkstatus_pud(ctx):
    await checkstatus_core(bot.status_server_address_pud, bot.status_server_port_pud, 'play', ctx)

#-------------------------------------------------------------------------------
# Reply to an AHELP from the discord.
#-------------------------------------------------------------------------------
async def ahelp_pm_core(server, port, ctx, args):
    role = discord.utils.get(ctx.guild.roles, id = int(bot.the_team))
    if role not in ctx.author.roles:
        await ctx.message.reply("oh yeah? says WHO?!")
        await ctx.message.add_reaction('\U0001F595')
        return

    message = " ".join(str(x) for x in args[1::1])
    pee_em = {
        'type': 'pm',
        'nick': ctx.author.name,
        'target': args[0],
        'msg': message
    }

    h.logger('discord -> byond ahelp pm: {0} to {1}: "{2}"'.format(ctx.author.name,
                                                                   args[0],
                                                                   message), "Disc")
    loop = asyncio.get_running_loop()
    try:
        reslut = await loop.run_in_executor(None, byond.topic.send,
                                            server, port,
                                            urllib.parse.urlencode(pee_em))
        if reslut == 0:
            ctx.message.reply("Dunno, bud...")
            await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')
        elif "key2" in reslut:
            if reslut["key2"] == "*no client*":
                await ctx.message.reply("They, uh... they said there's no-one there.")
                await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')
        else:
            await ctx.message.add_reaction('\N{THUMBS UP SIGN}')
    except:
        await ctx.message.reply("Hey, so, I went to tell 'em, and something made a real bad noise and I think it's broke")
        await bot.jetsam_chan.send("Hey! Shit's fucked: {0}".format(sys.exc_info()[1]))
        await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')


@bot.command(name='pm1', brief="Send an Admin PM",
             help="Nerd use only. Send an admin PM to some dork on the dev server.",
             usage="<ckey> <message>")
async def ahelp_pm_dev(ctx, *args):
    await ahelp_pm_core(bot.status_server_address_dev, bot.status_server_port_dev, ctx, args)

@bot.command(name='pm2', brief="Send an Admin PM to live server",
             help="Nerd use only. Shout at someone on the live server.",
             usage="<ckey> <message>",
             aliases=['pm'])
async def ahelp_pm_pud(ctx, *args):
    await ahelp_pm_core(bot.status_server_address_pud, bot.status_server_port_pud, ctx, args)



#-------------------------------------------------------------------------------
# Reply to a Mentor Help, from the discrod
#-------------------------------------------------------------------------------

async def mhelp_core(server, port, ctx, args):
    mentaur_role = discord.utils.get(ctx.guild.roles, id = int(bot.mentaurs))
    team_role = discord.utils.get(ctx.guild.roles, id = int(bot.the_team))
    if (mentaur_role not in ctx.author.roles) and (team_role not in ctx.author.roles):
        await ctx.message.reply("You gotta license for mentoring, bud? Gotta have the license!")
        await ctx.message.add_reaction('\U0001F595') # middle finger
        return

    message = " ".join(str(x) for x in args[1::1])
    pee_em = {
        'type': 'mentorpm',
        'nick': ctx.author.name,
        'target': args[0],
        'msg': message
    }
    h.logger('discord -> byond mentorhelp pm: {0} to {1}: "{2}"'.format(ctx.author.name,
                                                                        args[0],
                                                                        message), "Disc")
    loop = asyncio.get_running_loop()
    try:
        reslut = await loop.run_in_executor(None, byond.topic.send,
                                            server, port,
                                            urllib.parse.urlencode(pee_em))
        if reslut == 0:
            await ctx.message.reply("Dunno, bud...")
            await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')
        elif "key2" in reslut:
            if reslut["key2"] == "*no client*":
                await ctx.message.reply("They said there's no-one there, bud...")
                await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')
        else:
            await ctx.message.add_reaction('\N{THUMBS UP SIGN}')
    except:
        await ctx.message.reply("...I think I broke it.")
        await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')
        await bot.jetsam_chan.send("Hey! Shit's fucked: {0}".format(sys.exc_info()[1]))

@bot.command(name='mpm1', brief="Mentor PM",
             help="Mentor team use only. Send a mentor PM to some dork on the dev server.",
             usage="<ckey> <message>")
async def mhelp_dev(ctx, *args):
    await mhelp_core(bot.status_server_address_dev, bot.status_server_port_dev, ctx, args)

@bot.command(name='mpm2', brief="Mentor PM Live",
             help="Mentor team use only. Send a mentor PM to some dork on the live server.",
             usage="<ckey> <message>",
             aliases=['mpm'])
async def mhelp_pud(ctx, *args):
    await mhelp_core(bot.status_server_address_pud, bot.status_server_port_pud, ctx, args)

#-------------------------------------------------------------------------------
# Send an asay message from the discrod
#-------------------------------------------------------------------------------
## warc says this is pointless. i can't argue with that tbh? kept for reference anyway
# async def asay_core(server, port, ctx, args):
#     role = discord.utils.get(ctx.guild.roles, id = int(the_team))
#     if role not in ctx.author.roles:
#         await ctx.message.reply("oh yeah? says WHO?!")
#         await ctx.message.add_reaction('\U0001F595')
#         return

#     #message = " ".join(str(x) for x in args[0:])
#     ah_say = {
#         'type': 'asay',
#         'nick': ctx.author.name,
#         'msg': ctx.message
#     }

#     h.logger('discord -> byond asay: {0} sez: "{1}"'.format(ctx.author.name,
#                                                             ctx.message), "Disc")

#     loop = asyncio.get_running_loop()
#     try:
#         reslut = await loop.run_in_executor(None, byond.topic.send,
#                                             server, port,
#                                             urllib.parse.urlencode(ah_say))
#         if reslut == 0:
#             await ctx.message.reply("Uhhh?")
#             await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')
#         else:
#             await ctx.message.add_reaction('\N{SPEECH BALLOON}')
#     except:
#         await ctx.message.reply("Exceptional!")
#         await bot.get_channel(int(jetsam_chan)).send("Shit's fucked: {0}".format(sys.exc_info()[1]))

# @bot.command(name='asay1', brief="ASay",
#              help="Nerd use only. For chatting shit about you where you can't see it.",
#              usage="<message>")
# async def asay_dev(ctx, *args):
#     await asay_core(status_server_address_dev, status_server_port_dev, ctx, args)

# @bot.command(name='asay2', brief="ASay",
#              help="Nerd use only. For chatting shit about you where you can't see it.",
#              usage="<message>",
#              aliases=['asay'])
# async def asay_pud(ctx, *args):
#     await asay_core(status_server_address_pud, status_server_port_pud, ctx, args)

#-------------------------------------------------------------------------------
# Send an ooc message from the discrod
#-------------------------------------------------------------------------------

async def ooc_send_core(server, port, ctx, args):
    role = discord.utils.get(ctx.guild.roles, id = int(bot.the_team))
    if role not in ctx.author.roles:
        await ctx.message.reply("Bad monkey! No ook for you!")
        await ctx.message.add_reaction('\U0001F595')
        return

    message = " ".join(str(x) for x in args[0::1])
    ook_ook = {
        'type': 'ooc',
        'nick': ctx.author.name,
        'msg': message
    }
    h.logger('discord -> byond ooc: {0} sez: "{1}"'.format(ctx.author.name,
                                                            message), "Disc")

    loop = asyncio.get_running_loop()
    try:
        reslut = await loop.run_in_executor(None, byond.topic.send,
                                            server, port,
                                            urllib.parse.urlencode(ook_ook))
        if reslut == 0:
            await ctx.message.reply("Uhhh?")
            await ctx.message.add_reaction('\N{THUMBS DOWN SIGN}')
        else:
            await ctx.message.add_reaction('\N{SPEECH BALLOON}')
    except:
        await ctx.message.reply("Exceptional!")
        await bot.jetsam_chan.send("Shit's fucked: {0}".format(sys.exc_info()[1]))

@bot.command(name='ooc1', brief="OOC",
             help="Nerd use only. For chatting shit about you where you *can* see it.",
             usage="<message>")
async def ooc_dev(ctx, *args):
    await ooc_send_core(bot.status_server_address_dev, bot.status_server_port_dev, ctx, args)

@bot.command(name='ooc2', brief="OOC",
             help="Nerd use only. For chatting shit about you where you *can* see it.",
             usage="<message>",
             aliases=['ooc'])
async def ooc_pud(ctx, *args):
    await ooc_send_core(bot.status_server_address_pud, bot.status_server_port_pud, ctx, args)


################################################################################
#       Non-command message reception. Heavy lifting done here.
################################################################################
@bot.event
async def on_message(msg):
    await bot.process_commands(msg)
    if msg.author == bot.user:
        return
    if msg.author.bot: # Ignore other bots.
        return
    if msg.content == "flexx.help":
        await msg.channel.send("HELLO JUICERS. I'm Flexx Hard Bangobot. I'm a discord bot built by Micolithe "
                               "and slightly modified by WARC or some shit. For transparency **I am scraping "
                               "all public channels for input** for the markov chainer. I do two main things. Random "
                               "gibberish sentences and replace a random word with juice.")
        return
    if msg.content.casefold() == "based":
        await msg.reply(random.choice(["based on what exactly?","deez nuts","ohio","gyatt","i still dont know what the fantom tax is","i don't get it","what's lil' b got to do with it?","based? based on what, idiot?","sigma","skibidi","woke","get new material"]))
        return

    ## -~- auto ASay Stuff -~-
    if str(msg.channel) == "centcom":
        if str(msg.content).startswith('$'):
            return # Skip a received command
#        h.logger("Received message from the dork zone, to send to game server", "Disc")
        # Package this message up in an asay and send it off to the game server.
        ah_say = {
            'type': 'asay',
            'nick': msg.author.name,
            'msg':  msg.content
        }
#        h.logger("{0}".format(ah_say), "Disc")
        loop = asyncio.get_running_loop()
        try:
#            h.logger("on_message asay: sending", "Disc")
            reslut = await loop.run_in_executor(None, byond.topic.send,
                                                bot.status_server_address_dev, bot.status_server_port_dev,
                                                urllib.parse.urlencode(ah_say))
            if reslut == 0:
                await msg.add_reaction('\N{THUMBS DOWN SIGN}')
            else:
                # react to original message with 'speech balloon'
                await msg.add_reaction('\N{SPEECH BALLOON}')
        except:
            await bot.jetsam_chan.send("DEV Exceptional: {0}".format(sys.exc_info()[1]))

        try:
            reslut = await loop.run_in_executor(None, byond.topic.send,
                                                bot.status_server_address_pud, bot.status_server_port_pud,
                                                urllib.parse.urlencode(ah_say))
            if reslut == 0:
                await msg.add_reaction('\u274E')
            else:
                await msg.add_reaction('\u2705')
        except:
            await bot.jetsam_chan.send("PUD Exceptional: {0}".format(sys.exc_info()[1]))

        return
    # -~- end auto asay stuff -~-

    # moved this here to improve prompt responses
    h.markov_add(m, msg.content, config["markov_excluded_words"])

    if 'flexx' in msg.content.lower():
        if '@everyone' in msg.content.lower() or '@ everyone' in msg.content.lower():
            await msg.reply("your gimmick is bad and you should feel bad.")
            return

#        h.logger("User provided a cool and normal prompt which was: " + msg.content, "Debug")
        markov_string = m.generate_sentence(msg.content)
        await msg.channel.send(markov_string)
        return

    #h.markov_add(m, msg.content, config["markov_excluded_words"])
    if str(msg.channel) not in config["talk_in"]:
        return

    # h.logger(str(msg.author) + " : " + msg.content, "Debug")  # Just so I can see what's coming in
    rng_calculator = random.randrange(1, 50)
#    h.logger("Calculated a random number : " + str(rng_calculator), "Debug")

    if str(msg.channel) == "dog-water":
        if rng_calculator >= 30:
            h.logger("RNG >= 30, dog water", "Info")
            await msg.channel.send("dog water")
        return

    if str(msg.channel) == "a-channel-where-you-can-only-say-im-gay":
        if 'straight' in msg.content.lower():
            await msg.channel.send("no.")
        if rng_calculator >= 40:
            h.logger("RNG >= 40, im gay", "Info")
            await msg.channel.send("im gay")
        return

    # print(str(rng_calculator))
    if rng_calculator == 10:
 #       h.logger("RNG = 10, Butt Replace function activated", "Debug")
        # do the butt replace
        butt = h.butt_replace(msg.content)
        print(butt)
        if butt is not None:
#            h.logger("adding a JUICER phrase to the BRANE OKAY", "Debug")
            h.markov_add(m, butt, config["markov_excluded_words"])
            await msg.channel.send(butt)
        return

    if rng_calculator == 42:
        h.logger("RNG = 42, sending a spooky one", "Debug")
        misdirection = h.spooky(msg.content)
        if misdirection is not None:
            spookymsg = m.generate_sentence(misdirection)
            await msg.channel.send(spookymsg)
        return

    if rng_calculator >= 48:
#        h.logger("RNG >= 48, Markov Gibberish function activated", "Debug")
        markov_string = m.generate_sentence()
        await msg.channel.send(markov_string)
        return

if __name__ == "__main__":
    # Horrible transmodule global vars stuff because I suck at
    # architecturing stuff
    intertwingle.setComms(bot)
    intertwingle.setConfig(config)

    # Fire up the Topic()/Export() receiving server on a separate thread.
    bridge = ThreadingHTTPServer(("0.0.0.0", config["ircbot_port"]), BridgeServer)
    bridgeThread = threading.Thread(target=bridge.serve_forever)
    bridgeThread.start()

    # Discrud. :3
    bot.run(config["discord_token"])
