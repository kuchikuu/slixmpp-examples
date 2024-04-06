#!/bin/python3

import slixmpp

class MUCBot(slixmpp.ClientXMPP):
    def __init__(self, jid, password, room, nick, mes):
        slixmpp.ClientXMPP.__init__(self, jid, password)
        
        self.room = room
        self.nick = nick
        self.mes = mes

        self.add_event_handler("session_start", self.start)

    async def start(self, event):
        self.send_presence()
        await self.get_roster()
        try:
            await self.plugin['xep_0045'].join_muc(self.room, self.nick)
        except:
            print("Error while joining the MUC")
        try:
            self.send_message(mto=self.room,
                    mbody=self.mes,
                    mtype='groupchat')
            self.disconnect()
        except:
            print("Error while sending the message")


_jid = "YourBotAddress@domain.example"
_pas = "YourBotsPassword"
_room = "AddressOfTheMUC@chat.domain.example"
_nick = "YourBotNick(GiveItSome)"
_mes = "This is the text that will be sent to the MUC"


xmpp = MUCBot(_jid, _pas, _room, _nick, _mes)

xmpp.register_plugin('xep_0030') # Service Discovery
xmpp.register_plugin('xep_0045')
xmpp.register_plugin('xep_0199') # XMPP Ping


xmpp.connect()
xmpp.process(forever=False)
