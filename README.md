# SliXMPP examples

In this repo, I added examples how to use slixmpp library to send messages in certain scenarios

1. sendmessage.py - Send a direct message to a person
2. one\_message\_mucbot.py - Send a message to a MUC
3. omemo\_sendmessage.py - Send an encrypted message to a person using OMEMO
4. omemo\_one\_message\_mucbot.py - Send an encrypted message to a MUC using OMEMO

If you want to use OMEMO, you have to install slixmpp-omemo library.

Overall, the basic to have a bot is to install slixmpp library.

The credentials of the bot account are hardcoded into the script (You must add your own)


The bots do the following thing:
+ Personal message
1. Connect to a server with a provided credentials
2. Send a message to an address
3. Disconnect and close the script

+ Sending a message to a MUC
1. Connnect to a server with a provided credentials
2. Join a MUC
3. Send the message
4. Disconnect and close the script


+ Encrypted personal message
1. Connect to a server with a provided credentials
2. Blind-trust OMEMO keys of the recipient
3. Encrypt the message
4. Send the message
5. Disconnect and close the script

+ Sending an encrypted message to a MUC
1. Connnect to a server with a provided credentials
2. Join a MUC
3. Get JIDs of the MUC
4. Get and blind-trust OMEMO keys of everyone in the MUC
5. Encrypt the message for every OMEMO key
6. Send the message
7. Disconnect and close the script
