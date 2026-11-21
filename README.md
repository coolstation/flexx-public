# Flexx Discord Bot - Learned 2 Wipe Edition

Flexx is one of the discord bots of all time, a conglomeration of shit-talking
markov bot (the core of which is from **Vaporwave George Costanza**, IYKYK.),
and slightly crude game management tools for CoolStation spacestation13
servers. (May work on GoonStation servers too, but we've not tried it. YMMV.)

This is the public edition, because some folks wanted to see how the sausage was
made. Some CoolStation Exclusive™ commands have been removed, and some
CoolStation specific things have been tweaked, but you may still stumble across
things that are hard-coded or make some assumptions that Do Not Work for you.

(Also because it's so hard to dry-run this thing because it's very dependent on
*being connected to discord and having messages pushed at it*, it's entirely
possible something is broken without having been noticed.)

No AI was used in the production of this codebase. 🖤
🐾 Made with our own grubby paws! 🐾

 == ⚠️ == ⚠️ == ⚠️ == ⚠️ == ⚠️ == ⚠️ == ⚠️ == ⚠️ == ⚠️ == ⚠️ == ⚠️ == ⚠️ ==
**                                                                            **
** This bot will ingest messages in all channels it is in, even if it is not  **
**    allowed to speak in there, and will digest them into the markov chain   **
**                                                                            **
**                    Ensure your users are aware of this.                    **
**                                                                            **
**  If you do not wish the bot to ingest, digest, and potentially regurgitate **
**   messages from certain channels (labour-relations, sensitive admin chat,  **
**     current affairs, news, etc), **do not allow it into those channels**.  **
**                                                                            **
================================================================================

There is some configurable badwords filtering, but by and large the protection against
spamming is *your own community administration*. If someone is trying to
force-feed the bot to respond in ways you don't want, *tell them to knock it
off*.  If they persist, maybe consider whether that's the sort of
boundary-disrespecting behaviour you want to allow in your spaces okay?

# License

**Flexx** is released under the terms of the Creative Commons
Attribution-NonCommercial-ShareAlike license, version 4.0 International
edition. A copy of which is provided as <LICENSE>.

# Configuration
Configuration is JSON, in `config/config_secret.json`, wherein your discord keys
and whatnot will be set. You probably want that to only be readable by the bot
user.

* `discord_token`: This is the access token for your bot's discord account, that
  you need to go bother Discord for.  Please see:
  https://discordpy.readthedocs.io/en/stable/discord.html
* `talk_in`: A list of channels where markov chatter is permitted. Channels
  outside of this will only get 'business' responses (for commands and the like)
* `markov_excluded_words`: Words the markov chaining will not learn, nor allow
  to be emitted. (Badwords list, basically.)
* `ircbot_token`:
* `ircbot_port`: (Numeric) Port that the byond bridge server will run on, for
  game Topic calls to connect to.
* `status_server_address_pud`: (Domain/IP address) Address or IP that your live
  server is running on.
* `status_server_port_pud`: (Numeric) Port that your live server's BYOND
  instance is running on.
* `status_server_address_dev`: (Domain/IP address) Address or IP that your dev
  server is running on.
* `status_server_port_dev`: (Numeric) Port that your dev server's BYOND instance
  is running on.
* `the_team`: (Guild ID) Your admins role.
* `codre_id`: (Guild ID) Role allowed to fire off the build script and other
  development stuff without getting full access to all the admin comments.
* `mentaurs`: (Guild ID) Your designated player-mentors.
* `butt_events`: (Channel ID) Where you want in-game events to be announced.
* `ahelp_zone`: (Channel ID) Where you want admin-help requests to be sent. (You
  probably want this to be a channel that only your game-admins can see.)
* `mhelp_zone`: (Channel ID) Where do mentor-help requests go? (Less
  sensitive. You likely want this to be a channel that your designated
  player-mentors are.
* `jetsam_chan`: (Channel ID) Debugging/error/status announcements from the bot,
  including any caught exceptions.
* `codre_chan`: (Channel ID) Where byond build-script failure logs get yote. In
  case you use a cool/goon setup with a split repo for secret content, where
  build errors have potential to leak info about secret content.
* `playtest_chan`: (Channel ID)
* `flexxup`: path to the script to update your bot code repository
* `gamebuild`: path to the script used to update your game code and build the
  latest revision
* `webupdate`: path to the script you want to launch to update your website
  stuff.
* `scriptup`: path to the script used to update your infra scripts (gamebuild,
  webupdate, etc)
* `taglines`: A list of taglines for use at the bottom of status cards and
  whatnot.

## config/butt_exclusions
A newline-delimited list of words to **not** replace with 'butt', when hunting
for a word in a sentence to replace with 'butt'. Except in this case, they'd be
replaced with 'juice', but same difference.

## markov-brain/markov_brain.txt

You gotta load this up with some newline-delimited sentences, but it will grow
with activity. Some nonsense has been specially selected to start you off with
(<3) but the more real actual conversation builds up in here the better the
result will be.

Perhaps let the bot chill in a channel for a bit without being able to talk in
there, and let natural conversation built its brane.

# Running
## 'installation'

* Do the usual dance with creating & activating a python venv
  (`python -m venv env`, `source ./env/bin/activate`)
* Install the dependencies (`pip install -r requirements.txt`)
* Get your discord API/bot key thing
* Mess with all the configuration files
* Start it (Run `discord_bot.sh`)
* Fix everything wrong
* Enjoy?

## Log files

* `georgie.log` - The internal logging system format.
* `crudlog` - A dump of stderr & stdout, which you can paw through for any
  mysterious uncaught exceptions and the like.

# Commands

Commands are given with a `$` prefix. This was chosen so it didn't interfere
with other bots that use `!`.

Commands will often give feedback via reacts. Usually a thumbs-up if a command
succeeded, or a thumbs-down if it didn't.

The `help` command will also respond with a listing of available commands and
their arguments.

## Bot Management
### test
Check if the bot is alive and listening to you. Just reacts with a thumbs-up if
the command was received.

### naptime
**Requires `the_team` role.**
Shuts down the bot.

### order
**Requires `the_team` role**

Checks, or changes, the markov chain order value; that is, the distance between
words to be processed.

### flush
**Requires `the_team` role**
Purges logger entries older than 14 days.

### flexxup
**Requires `codre_id` role.**

Runs the bot update script, then if that returns success (... well, a return of
0, at least), will then shut the bot down so the cron script can restart it.

**Has no recovery/fallback if the new code crashes on startup. So watch out! <3**

## Game Management

### status

Checks the status of the game world on the live server, using BYOND Topic
queries. Returns a nice pretty card with some game round status, including the
game-mode, what map is currently in use, number of players, and the in-game
station name. Also some silly configurable tag-lines.

### status1
Same as above, but for the dev server.

### pm
**Requires `the_team` role**
`pm <ckey> <message>`

Sends an admin-pm to a user on the live server. `ckey` only needs to be complete
enough to match a distinct user. (i.e. if user `muggins` is the only person on
the server with name starting with 'm', `pm m knock it off` will go directly to
them. If you also have user `mellow` connected, then you'd need to use `pm mu
knock it off` to have the same effect.)

### pm1
**Requires `the_team` role**

Same as `pm`, but for the dev server.

### mhelp
**Requires `mentaurs` role**
`mpm <ckey> <message>`

Sends a mentor-help reply to a user on the live server.

### mhelp1
**Requires `mentaurs` role**
Same as above, but for the dev server.

### ooc
**Requires `the_team` role**
`ooc <message>`

Sends a message to OOC chat on the live server

### ooc1
**Requires `the_team` role**
Same as `ooc`, but for the dev server.

### kill
**Requires `the_team` role**
Shuts down the DreamDaemon process. Has a cooldown of 1 use every 2.5 minutes.

### build
**Requires `codre_id` role**
Fires off the game server build script.

Will give a thumbs up or down react on completion, depending on whether the
build worked or failed. Will also reply to the build requester with a silly
message.

On build failure, some crude feedback will be given depending on the return
value from the build script, letting you know where in the build the process
shat itself. **This is fairly Cool specific, your build script needs to return a
different positive integer for each stage, and you'd need to change the feedback
output to match what those stages are.** See `discord_bot.py`#L291

It will also dump a file containing the build process output, into
`codre_chan`.

## Other Management

### buildweb
**Requires `the_team` role.**
Fires off the script to update the website

### scriptup
**Requires `codre_id` role.**
Fires off the script to update the updater scripts.

## Silly
### crack
For chiropractic use. 'cracks' someone's nick. Requires the bot to have enough
permissions to be able to change people's nicks.
