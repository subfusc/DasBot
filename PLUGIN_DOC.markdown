DOCUMENTATION
========== 

This document describes most of the aspects people need to know in order to write a plugin for this IRC bot.

The bot will search for plugins.<name> and try to instanciate a class of type `Plugin`. The `Plugin` class provides three different functions that can be used. These are:

- `cmd` (for IRC commands like `!kick`)
- `listen` (to get everything said in a channel)
- `help` (so you can inform people of your commands) Syntax of help is: `?<cmd>`. The command `?all` lists all of the available commands provided by a plugin.

Information available in kwargs
---------

- from_nick: The nick of the sender of this message/command
- from_ident: The ident from the hostmask of the sender of this message/command
- from_host_mask: The adress the sender has.
- auth_nick: If a user is logged in, this will be his account name. None if the Auth System is turned
             off or the person is not logged in.
- auth_level: an integer between 0 and 100, where 100 is the owner and 0 is just a user. Who is what
              and at what level distinqushes what, is up for debate.
- channel_users: The list of users in the channel that the current message/command is comming from.
- nick_to_user: A dictionary that contains the Username in the Authentication system as value and
                current nick on IRC as key. This will contain the nick if the user is online.
- user_to_nick: same as above, only reversed key and value. This has a lazy evaluation, so it will
                not delete a user even if he goes online. But will reset if the user changes nick
- new_job: This is the function to add jobs to the CronBot. It takes a touple with the unix time you 
           want the function to execute, the function and a list of argument. 
           e.g: kwargs['new_job']((time.time() + 20, self._send_reminder, [channel, msg]))
                will execute (Class)._send_reminder(channel, msg)
           Return values should be the same as below.


Return values
-------------

To send messages or notifies to a channel, you have to return it. It should be in the form of 
a list with touples, where each touple must contain the following:

    (0, channel, message) // Same as send message to channel.
    (0, channel, nick, message) // Same as above but will be prefixed witht the nick e.g Bob: <message>
    (1, channel, message) // Notify in a channel (if channel == user, the user will be notified)

So return values would be e.g:

    [(0, "#iskbot", "Nothing more to do here")]

will give channel message:

    Bot: Nothing more to do here

and

    [(0, "#iskbot", "Bob is being mean"), (1, "Bob", "This is a warning for bad behaviour")]

will give channel message:

    Bot: Bob is being mean
and notification to Bob:

    -Notice- This is a warning for bad behaviour
