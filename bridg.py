# Bridge server for the ircbot Export requests
# Mostly: Tamber's fault, based on TetraServ.

from http.server import BaseHTTPRequestHandler
import asyncio
import urllib.parse
import json
import random
import sys
import discord
import byond.topic
import intertwingle

class BridgeServer(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.bot = intertwingle.getComms()
        self.loop = intertwingle.getLoop()
        self.h = intertwingle.getLogger()
        self.status_announce_playtest = False
        super().__init__(*args, **kwargs)

    def log_message(self, format, *args):
        # Shut the fuck. (Otherwise it dumps the full request & query
        # string for *every http request it gets*, to the console.)
        pass

    def api_error(self, code, message):
        self.send_response(code)
        self.send_header("Content-type", "text/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps({"status": "error", "errormsg": message}), "utf-8"))

    def api_success(self):
        self.send_response(200)
        self.send_header("Content-type", "text/json")
        self.wfile.write(bytes(json.dumps({"status": "ok"}), "utf-8"))

    def do_GET(self):
        req = urllib.parse.urlparse(self.path)

        # This is what the ircbot code calls our 'iface'.
        endpoint = req.path.lstrip('/')

        # And our ircbot 'args'. What they are depends on which endpoint is in use.
        # But there are 3 we can expect to see every time:
        # - api_key: This is configured on the game server by the config option IRCBOT_API
        #            and must match what we were given in the config.
        #
        # - server_name: "Coolstation Development" or whatever
        #
        # - server: It's the 'serverKey'. Presumably this lets you
        #   figure out which of your servers is chatting crap to you
        #   when you have more than 1.
        #   I'll have to account for that if we ever get to that point.

        rawrgs = urllib.parse.parse_qs(req.query) # uwu

        if 'api_key' in rawrgs:
            if(rawrgs['api_key'][0] != intertwingle.getConfig()['ircbot_token']):
                self.api_error(403, "Incorrect API Key")
                self.h.logger('Bridge: Incorrect API key "{0}" sent by {1}'.format(rawrgs['api_key'][0], self.client_address), "Warn")
            else:
#                if endpoint == "event":
#                    self.GameEvent(rawrgs)
#                    self.api_success()
#                    self.h.logger('Game event: {0}'.format(rawrgs['type'][0]), "Debug")
                if endpoint == "admin":
                    # Assorted "Shit has gone wrong" warnings.
                    self.AdminNotice(rawrgs)
                    self.api_success()
#                    self.h.logger('Admin Notice from {0}'.format(rawrgs['key'][0]), "Debug")
                elif endpoint == "help":
                    # Requesting admin help
                    self.AdminHelp(rawrgs)
                    self.api_success()
#                    self.h.logger('AdminHelp from {0}'.format(rawrgs['key'][0]), "Info")
                elif endpoint == "mentorhelp":
                    self.MentorHelp(rawrgs)
                    self.api_success()
#                    self.h.logger('MentorHelp from {0}'.format(rawrgs['key'][0]), "Info")
                elif endpoint == "mentorpm":
                    # Response to a mentor
                    self.MentorReply(rawrgs)
                    self.api_success()
#                    self.h.logger('MentorReply from {0}'.format(rawrgs['key'][0]), "Info")
                elif endpoint == "asay":
                    self.ASay(rawrgs)
                    self.api_success()
#                    self.h.logger('ASay from {0}'.format(rawrgs['key'][0]), "Info")
                elif endpoint == "pm":
                    self.Apm(rawrgs)
                    self.api_success()
#                    self.h.logger('PM from {0}'.format(rawrgs['key'][0]), "Info")
                elif endpoint == "ban":
                    self.Bans(rawrgs)
                    self.api_success()
#                    self.h.logger('Ban for {0} {1} by {2}'.format(rawrgs['key2'][0],
#                                                                  rawrgs['type'][0],
#                                                                  rawrgs['key'][0]))
                else:
                    self.api_error(404, "Unknown iface")
                    self.h.logger("Unknown interface request: '{0}'".format(endpoint), "Warn")
        else:
            self.api_error(403, "Incorrect API Key")
            self.h.logger('Bridge: No API key sent by {0}'.format(self.client_address), "Warn")


    def AdminHelp(self, ahelp):
        bot = intertwingle.getComms()
        if(ahelp['key'][0] == 'Loggo'):
            # First AHELP of the shift sends a link to the current logs on the web thing.
            # Thanks Zamujasa!
            asyncio.run_coroutine_threadsafe(bot.ahelpZone.send(ahelp['msg'][0]),
                                                 intertwingle.getLoop())
        else:
            if 'name' not in ahelp:
                ahelp['name'] = ["Unknown"]

            helpcard = discord.Embed(title="AHELP Request from {0}".format(ahelp['key'][0]),
                                     description='**{0} (as {1})**: {2}'.format(ahelp['key'][0],
                                                                                ahelp['name'][0],
                                                                                ahelp['msg'][0]),
                                     color = discord.Color.gold())
            helpcard.set_footer(text="To reply: `$pm1 {0} <message>`".format(ahelp['key'][0]))
            asyncio.run_coroutine_threadsafe(bot.ahelpZone.send(embed=helpcard),
                                             intertwingle.getLoop())
    def MentorHelp(self, mhelp):
        bot = intertwingle.getComms()
        if 'name' not in mhelp:
            mhelp['name'] = ["Unknown"]

        helpcard = discord.Embed(title="Mentor Help Request from {0}".format(mhelp['key'][0]),
                                 description='**{0} (as {1})**: {2}'.format(mhelp['key'][0],
                                                                            mhelp['name'][0],
                                                                            mhelp['msg'][0]),
                                 color = discord.Color.gold())
        helpcard.set_footer(text="To reply: `$mpm1 {0} <message>`".format(mhelp['key'][0]))
        asyncio.run_coroutine_threadsafe(bot.mhelpZone.send(embed=helpcard),
                                         intertwingle.getLoop())

    def MentorReply(self, mreply):
        bot = intertwingle.getComms()
        if 'name' not in mreply:
            mreply['name'] = ["Unknown"]
        asyncio.run_coroutine_threadsafe(bot.mhelpZone.send(embed=discord.Embed(
                title="Mentor PM to {0}".format(mreply['key2'][0]),
                description='**{0} (as {1})**: {2}'.format(mreply['key'][0],
                                                           mreply['name'][0],
                                                           mreply['msg'][0]),
                color = discord.Color.gold())),
                                             intertwingle.getLoop())

    # Warning log type deals. i.e. VPN bans, computer-ID tests, station name changes, ban updates, etc.
    def AdminNotice(self, notice):
        bot = intertwingle.getComms()
        if 'key' in notice:
            if 'name' not in notice:
                notice['name'] = ["Unknown"]
            asyncio.run_coroutine_threadsafe(bot.ahelpZone.send(
                embed=discord.Embed(title="Notice",
                                    description='**{0} ({1})**: {2}'.format(notice['key'][0],
                                                                        notice['name'][0],
                                                                        notice['msg'][0]),
                                    color = discord.Color.red())),
                                             intertwingle.getLoop())
        else:
            asyncio.run_coroutine_threadsafe(bot.ahelpZone.send(
                embed=discord.Embed(title="Notice",
                                    description=notice['msg'][0],
                                    color = discord.Color.red())),
                                             intertwingle.getLoop())
    # Ah say, ah say, ah say...
    def ASay(self, say):
        bot = intertwingle.getComms()
        if 'name' not in say:
            say['name'] = ["Unknown"]
        asyncio.run_coroutine_threadsafe(bot.ahelpZone.send(
            embed=discord.Embed(title="Ah say...",
                                description='**{0} (as {1})**: {2}'.format(say['key'][0],
                                                                    say['name'][0],
                                                                    say['msg'][0]),
                                color = discord.Color.blue())),
                                         intertwingle.getLoop())
    # Responses to admin-PMs
    def Apm(self, say):
        bot = intertwingle.getComms()
        if 'name' not in say:
            say['name'] = ["Unknown"]
        if 'name2' not in say:
            say['name2'] = ["Unknown"]

        asyncio.run_coroutine_threadsafe(bot.ahelpZone.send(
            embed=discord.Embed(title="PM",
                                description='**{0} (as {1}) to {2} (as {3})**: {4}'.format(
                                    say['key'][0],
                                    say['name'][0],
                                    say['key2'][0],
                                    say['name2'][0],
                                    say['msg'][0]),
                                color = discord.Color.blue())),
                                         intertwingle.getLoop())

    # Game Bans
    def Bans(self, say):
        bot = intertwingle.getComms()
        if 'expiry' not in say:
            say['expiry'] = ["N/A"]

        asyncio.run_coroutine_threadsafe(bot.ahelpZone.send(
            embed=discord.Embed(title="Ban",
                                description='**{0} {1} ban: {2} "*{3}*" - Expires: {4}'.format(
                                    say['key'][0],
                                    say['type'][0],
                                    say['key2'][0],
                                    say['msg'][0],
                                    say['expiry'][0]),
                                color = discord.Color.red())),
                                         intertwingle.getLoop())

    # Assorted logging shit.
    def GameEvent(self, event):
        bot = intertwingle.getComms()
        eventType = event['type'][0]
        if eventType == 'serverstart':
            statusCard = discord.Embed(title="Server starting",
                                       description='**{0}** round on **{1}**'.format(event["gamemode"][0],
                                                                                     event["map"][0]),
                                       color = discord.Color.green(),
                                       url="https://connect.coolstation.space/"
                                       )
            statusCard.set_footer(text=random.choice(intertwingle.getConfig()["taglines"]))
            asyncio.run_coroutine_threadsafe(bot.eventsLog.send(embed=statusCard),
                                             intertwingle.getLoop())
        elif eventType == 'shuttledock':
            asyncio.run_coroutine_threadsafe(bot.eventsLog.send('Shuttle has docked with the station'),
                                             intertwingle.getLoop())
        elif eventType == 'roundend':
            self.h.logger("Roundend event received.", "Debug")
            self.h.logger("Event data: {0}".format(event), "Debug")

            asyncio.run_coroutine_threadsafe(bot.eventsLog.send(
                "# Shift Ended on {0} \n\
                Final grade: **{1}**\n\
                Crew survival rate: **{2:.1f}**%\n\
                Security Dept Score: **{3:.1f}**\n\
                Engineering Dept Score: **{4:.1f}**\n\
                Research Dept Score: **{5:.1f}**\n\
                Civilian Dept Score: **{6:.1f}**\n\
                **{7}** farts blasted\n\
                **{8}** weade grown (**{9}** doinks sparked)\n\
                Clowns abused: **{10}**".format(
                    event["map"][0],
                    event["grade"][0],
                    float(event["survival"][0]),
                    float(event["sec_scr"][0]),
                    float(event["eng_scr"][0]),
                    float(event["res_scr"][0]),
                    float(event["civ_scr"][0]),
                    event["farts"][0],
                    event["wead"][0],
                    event["doinks"][0],
                    (event["clowns"][0] if(int(event["clowns"][0]) > 0) else random.choice(["None that you could prove!", "Not enough.", "They couldn't get the charges to stick"])))),
                                             intertwingle.getLoop())

            self.status_announce_playtest = True
        elif eventType == 'login':
            # Client connection to server. Arg: ckey.
            self.popCheckAnnounce()
        else:
            pass


    def popCheckAnnounce(self):
        bot = intertwingle.getComms()
        if(self.status_announce_playtest):
            # This only wants to be once a round, first thing we do is
            # switch off the flag to try prevent multiple simultaneous
            # announcements (e.g. as the server starts and people join)
            self.status_announce_playtest = False
            numPlayers = 0
            try:
                worldStatus = byond.topic.queryStatus(bot.status_server_address_pud, bot.status_server_port_pud)
                if(worldStatus):
                    numPlayers = int(worldStatus['players'][0])

                if(numPlayers > 10):
                    # Status card into playtesting channel.
                    gamedesc = "# Hey, come check it out\n There's **{0}** juicer{1} *{2}* on **{3}**!".format(
                        numPlayers, ("" if (numPlayers == 1) else "s"),
                        random.choice(["having fun",
                                       "wrecking the joint",
                                       "causing trouble",
                                       "chilling"]),
                        worldStatus['station_name'][0])

                    asyncio.run_coroutine_threadsafe(bot.playtest_chan.send(gamedesc),
                                                     intertwingle.getLoop())
                else:
                    # Fewer than 10 players, take the safety off the announce flag again.
                    self.status_announce_playtest = True
            except:
                asyncio.run_coroutine_threadsafe(bot.jetsam_chan.send(
                    "Popcheck shit broke.\n{0}".format(sys.exc_info()[1])),
                                                intertwingle.getLoop())
