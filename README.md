# ttServerManager
A server management bot fore TeamTalk5.
See the [example configuration file](https://raw.githubusercontent.com/blindelectron/ttServerManager/main/config_example.ini) for the documentation on how to configure it.
# features
## commands
* ban and unban, ban a user by nickname.
it bans the users ipAddress.
* bans, lists all band users on the server and there attributes.
* kick, kick a user by nickname.
* kickall, kick all users off the server.
The only user that is not kicked by this command is the bot itself.
* jail and unjail, locks the user and ip address to a certain channel.
Any users logging in from that ipAddress will also be locked, and any users logging in from a different ipAddress but the same userName will get there ipAddresse locked.
* broadcast, broadcasts a message using TeamTalks broadcast feature
* cbroadcast, broadcasts a message threw out all channels on a server.
this can be done because admins of a TeamTalk server are able to send messages to channels that they are not in.
* pbroadcast, broadcasts a message by private messaging every user logged in to the server.
* announcer, makes it so that any message sent by the specified user is rebroadcast via cbroadcast.
Run the command against the same user again to turn off announcements
* newaccount, creates a new user account on the server.
the syntax is as follows:
```
newaccount username=<accountUserName> password=<accountPassword type=<accountType>
```
Replace accountUsername with the username you want to use for the account, and accountPassword with the password you want for the account. Types are 1: default user, 2: administrator, 0: disabled
* delaccount, deletes the account with the specified username.
* accounts, lists all accounts on the server and there attributes.
Note that this command will list passwords, so don't use it in a channel where others are, in fact I would recommend just private messaging the bot if your touching the account commands.
* move, moves the specified user to the specified channel.
It does not matter if you propend and append the channel path with slashes, this is handled automatically.
* motd, sends back the server message of the day.
* talkto, allows the sender to have  a private conversation with another specified user.
This command moves the sender and user in to anew channel with a genorated password, it is useful when an admin needs to have a private conversation with a user.
* setconfig, this command allows the user to set configuration options and have them written to the config file.
the syntax is as follows:
```
setconfig nickname=testing bot
```
This syntax works for any option in the config file, you can even use it to write new options to the config file. You are also able to send it more than one option, like this:
```
setconfig nickname=testing bot autoaway=true
```
### notes on commands.
if sending in a channel message, you must propend the command with a slash(/)
Most commands are based on user nickname, unless otherwise specified.
The commands kick, move, ban, and talkto are able to take lists of users, separated by to colons(::).
## other functions.
* If the user is an admin and the feature  is enabled, the bot will intercept there channel messages so that it won't matter what channel they are in.
* If the feature is enabled, the bot can move a user to an idle channel when there status changes to away.
# important notes.
The bot must be logged in as an admin for it to work properly.
If you have a problem with the bot, please contact me directly or open an issue on Github.