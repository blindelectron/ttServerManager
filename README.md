# ttServerManager
A server management bot fore TeamTalk5
see the example configuration file for the documentation on how to configure it.
# features
# commands
ban and unban, ban a user by nickname.
it bans the users ipAddress.
bans, lists all band users on the server and there atributes.
kick, kick a user by nickname.
kickall, kick all users off the server.
The only user that is not kicked by this command is the bot itself.
jail and unjail, lockes the user and ip address to a certin channel
any users logging in from that ipAddress will also be locked, and any users logging in from a different ipAddress but the same userName will get there ipAddresse locked.
broadcast, broadcasts a message using TeamTalks broadcast feature
cbroadcast, broadcasts a message thrue out all channels on a server.
this can be done because admins of a TeamTalk server are able to send messages to channels that they are not in.
pbroadcast, broadcasts a message by private messaging every user logged in to the server.
announcer, makes it so that any message sent by the specified user is rebrodcasted via cbroadcast.
Run the command against the same user again to turn off announcements
newaccount, creates a new user account on the server.
the syntax is as follows:
newaccount username=<accountUserName> password=<accountPassword type=<accountType>
Replace accountUsername with the username you want to use for the account, and accountPassword with the password you want for the account. Types are 1: default user, 2: administrator, 0: disabled
delaccount, deletes the account with the specified username.
accounts, lists all accounts on the server and there attributes.
Note that this command wil list passwords, so don't use it in a channel where others are, infact I would recomend just private messaging the bot if your touching the account commands.
move, moves the specified user to the specified channel.
It does not matter if you prepend and append the channel path with slashes, this is handled automatically.
motd, sends back the server message of the day.
# notes on commands.
if sending in a channel message, you must prepend the command with a slash(/)
Most commands are baced on user nickname, unless otherwise specified.
# other functions.
If the user is an admin and the feature  is enabled, the bot will intercept there channel messages so that it won't matter what channel they are in.
# important notes.
The bot must be logged in as an admin for it to work properly.