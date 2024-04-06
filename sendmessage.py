#!/bin/python3

import slixmpp

class SendMessage(slixmpp.ClientXMPP):
    def __init__(self, jid, password, recipient, message):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        self.recipient = recipient
        self.msg = message

        self.add_event_handler("session_start",self.start)

    async def start(self, event):
        self.send_presence()
        await self.get_roster()

        self.send_message(mto=self.recipient,
                mbody=self.msg,
                mtype='chat')
        self.disconnect()

_jid = "YourBotAddress@domain.example"
_pas = "YourBotsPassword"
_rec = "AddressOfThePersonYouWantToSendTheMessageTo@domain.example"
_mes = "This is the text the person will receive"

xmpp = SendMessage(_jid, _pas, _rec, _mes)
xmpp.register_plugin('xep_0030') # Service Discovery
xmpp.register_plugin('xep_0199') # XMPP Ping

xmpp.connect()
xmpp.process(forever=False)
