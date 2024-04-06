#!/bin/python3
# Run with:
# PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
# Example:
# $ PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python python3 omemo_sendmessage.py

import slixmpp
import time
import os
import asyncio

import slixmpp_omemo
from slixmpp import JID
from slixmpp_omemo import PluginCouldNotLoad, MissingOwnKey, EncryptionPrepareException
from slixmpp_omemo import UndecidedException, UntrustedException, NoAvailableSession, IqError
from omemo.exceptions import MissingBundleException

class MUCBot(slixmpp.ClientXMPP):
    eme_ns = 'eu.siacs.conversations.axolotl'
    def __init__(self, jid, password, room, nick, message):
        slixmpp.ClientXMPP.__init__(self, jid, password)
        
        self.room = room
        self.nick = nick
        self.message = message

        self.add_event_handler("session_start", self.start)

    async def start(self, event):
        print("in the start event")
        self.send_presence()
        await self.get_roster()
        try:
            await self.plugin['xep_0045'].join_muc(self.room, self.nick)
        except:
            print("Error while joining the MUC")
        # Uncomment for some additional info:
        #muc_roster = self.plugin['xep_0045'].get_joined_rooms()
        #print(f"{muc_roster}")
        #muc_roster = await self.plugin['xep_0045'].get_affiliation_list(self.room, 'none')
        #print(f"affiliation: none: {muc_roster}")



        await self.encrypted_send(mto=self.room,
                    body=self.message,
                    mtype='groupchat')
        self.disconnect()
        print("end of start event")

    async def encrypted_send(self, mto: JID, body, mtype):
        print("in encrypted reply")
        msg = self.make_message(mto=mto, mtype=mtype)

        msg['eme']['namespace'] = "eu.some.namespace.oki"
        msg['eme']['name'] = self['xep_0380'].mechanisms[self.eme_ns]
        
        recipients = []

        muc_nicks = self.plugin['xep_0045'].get_roster(JID(self.room))
        print(f"Nicks in muc: {muc_nicks}")
        for nick in muc_nicks:
            recipients.append(JID(self.plugin['xep_0045'].get_jid_property(self.room, nick, 'jid')))
    
        for _affi in ['owner','member','admin','outcast']:
            muc_roster = await self.plugin['xep_0045'].get_affiliation_list(self.room, _affi)
            print(f"affiliation: {_affi}: {muc_roster}")
            for _affi_jid in muc_roster:
                if(_affi_jid in recipients):
                    print(f"{_affi_jid} already in recipients")
                else:
                    recipients.append(JID(_affi_jid))

        print(f"Recipients: {recipients}")
        expect_problems = {}
        while True:
            try:
                print("making encrypt")
                encrypt = await self['xep_0384'].encrypt_message(body, recipients, expect_problems)
                print("appending encrypt")
                msg.append(encrypt)
                print("returning msg.send()")
                # Uncomment if you want to see the XML of the message (Quite interesting)
                #print(f"MSG: {msg}")
                return msg.send()
            except UndecidedException as exn:
                await self['xep_0384'].trust(exn.bare_jid, exn.device, exn.ik)
            except IqError as lool:
                print(f"IqError: {lool}")
                raise
            except Exception as exn:
                print(f"Everything failed: {exn}")
                raise

        return None


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),'omemo')
os.makedirs(DATA_DIR, exist_ok=True)



_jid = "YourBotAddress@domain.example"
_pas = "YourBotsPassword"
_room = "AddressOfTheMUC@chat.domain.example"
_nick = "YourBotNick(GiveItSome)"
_message = "This is the text that will be sent to the MUC"


xmpp = MUCBot(_jid, _pas, _room, _nick, _message)

xmpp.register_plugin('xep_0030') # Service Discovery
xmpp.register_plugin('xep_0045')
xmpp.register_plugin('xep_0199') # XMPP Ping
xmpp.register_plugin('xep_0380') # Explicit Message Encryption
try:
        xmpp.register_plugin('xep_0384',{'data_dir':DATA_DIR},module=slixmpp_omemo)
except (PluginCouldNotLoad):
        print("Can't load omemo")
        exit(1)

xmpp.connect()
xmpp.process(forever=False)
