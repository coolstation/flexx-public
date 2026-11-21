# Helpers for admin messaging nonsense.
# Makes the pretty cards for ahelps, mentorhelps, notices, and asay

import discord

async def AdminHelp(self, ahelp):
    if(ahelp['key'][0] == 'Loggo'):
        if(self.ahelpZone):
            await self.ahelpZone.send('*changes the "[ ] hours since last AHELP" sign back to 0*')
    else:
        if(self.ahelpZone):
            await self.ahelpZone.send(embed=discord.Embed(title="AHELP Request from {0}".format(ahelp['key'][0]),
                                                          author='{0} (as {1})'.format(ahelp['key'][0],
                                                                                       ahelp['name'][0]),
                                                          description='{0}'.format(ahelp['msg'][0]),
                                                          color = discord.Color.gold()))
async def MentorHelp(self, mhelp):
    if(self.mhelpZone):
        await self.mhelpZone.send(embed=discord.Embed(title="Mentor Help Request from {0}".format(mhelp['key'][0]),
                                                      author='{0} (as {1})'.format(mhelp['key'][0],
                                                                                   mhelp['name'][0]),
                                                      description='{0}'.format(mhelp['msg'][0]),
                                                      color = discord.Color.gold()))
async def AdminNotice(self, notice):
    if(self.ahelpZone):
        if 'key' in notice:
            await self.ahelpZone.send(embed=discord.Embed(title="Notice",
                                                          author='{0} ({1})'.format(notice['key'][0],
                                                                                    notice['name'][0]),
                                                          description='{0}'.format(notice['msg'][0]),
                                                          color = discord.Color.red()))
        else:
            await self.ahelpZone.send(embed=discord.Embed(title="Notice",
                                                          description=notice['msg'][0],
                                                          color = discord.Color.red()))
async def ASay(self, say):
    if(self.ahelpZone):
        await self.ahelpZone.send(embed=discord.Embed(title="Blah",
                                                      author='{0} (as {1})'.format(say['key'][0],
                                                                                   say['name'][0]),
                                                      description='{0}'.format(say['msg'][0]),
                                                      color = discord.Color.blue()))
