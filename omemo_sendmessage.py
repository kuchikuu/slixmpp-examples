#!/bin/python3
# Run with:
# PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
# Example:
# $ PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python python3 omemo_sendmessage.py
import os

import slixmpp

import slixmpp_omemo
from slixmpp import JID
from slixmpp_omemo import PluginCouldNotLoad, MissingOwnKey, EncryptionPrepareException
from slixmpp_omemo import UndecidedException, UntrustedException, NoAvailableSession
from omemo.exceptions import MissingBundleException


class SendMessage(slixmpp.ClientXMPP):
    eme_ns = 'eu.siacs.conversations.axolotl'

    def __init__(self, jid, password, recipient, message):
        slixmpp.ClientXMPP.__init__(self, jid, password)

        self.recipient = recipient
        self.msg = message

        self.add_event_handler("session_start",self.start)

    async def start(self, event):
        self.send_presence()
        await self.get_roster()

        await self.encrypted_reply(mto=self.recipient, body=self.msg)
        self.disconnect()
    async def encrypted_reply(self, mto: JID, body):
        print("in encrypted reply")
        msg = self.make_message(mto=mto, mtype='chat')

        msg['eme']['namespace'] = "eu.some.namespace.oki"
        msg['eme']['name'] = self['xep_0380'].mechanisms[self.eme_ns]

        recipients = [JID(mto)]
        expect_problems = {}
        while True:
            try:
                print("making encrypt")
                encrypt = await self['xep_0384'].encrypt_message(body, recipients, expect_problems)
                print("appending encrypt")
                msg.append(encrypt)
                print("returning msg.send()")
                return msg.send()
            except UndecidedException as exn:
                await self['xep_0384'].trust(exn.bare_jid, exn.device, exn.ik)
            except Exception as exn:
                print(f"Everything failed: {exn}")
                raise

        return None

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),'omemo')
os.makedirs(DATA_DIR, exist_ok=True)

_jid = "YourBotAddress@domain.example"
_pas = "YourBotsPassword"
_rec = "AddressOfThePersonYouWantToSendTheMessageTo@domain.example"
_mes = "This is the text the person will receive"

xmpp = SendMessage(_jid, _pas, _rec, _mes)
xmpp.register_plugin('xep_0030') # Service Discovery
xmpp.register_plugin('xep_0199') # XMPP Ping
xmpp.register_plugin('xep_0380') # Explicit Message Encryption

try:
    xmpp.register_plugin('xep_0384',{'data_dir':DATA_DIR},module=slixmpp_omemo)
except (PluginCouldNotLoad):
    print("Can't load omemo")
    exit(1)

xmpp.connect()
xmpp.process(forever=False)
