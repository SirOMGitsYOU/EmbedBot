import asyncio
from misc.util import create_embed, log
from modules.module import Module


class SayModule(Module):

    async def on_command(self, msg, cmd, args):
        """Event handler for commands.

        Args:
            msg: The message.
            cmd: The command label.
            args: The command arguments.
        """
        if cmd != "say":
            return

        perms = msg.channel.permissions_for(msg.author)
        if not perms.manage_messages:
            await self._perm_error(msg.channel, "manage_messages",
                                   "this channel")
            return

        data = {
            "msg": msg,
            "channel": None,
            "ping": False,
            "color": 1,
            "title": "",
            "text": "",
            "fields": {}
        }
        await self._prompt_channel(data)

    async def _prompt_channel(self, data):
        """Part of the .say command. Prompts a target channel.

        Args:
            data: The session data for this command.
        """
        msg = data["msg"]
        await msg.channel.send("Please mention the channel where you want to"
                               + " post an embed into. Mention no channel to"
                               + " abort.")
        response = await self._input(msg.author, msg.channel)
        if response is None:
            return

        if len(response.channel_mentions) == 0:
            await msg.channel.send("Aborted.")
            return

        channel = response.channel_mentions[0]
        perms = channel.permissions_for(msg.author)
        if not perms.manage_messages:
            await self._perm_error(msg.channel, "manage_messages",
                                   "the target channel")
            return
        if not perms.send_messages:
            await self._perm_error(msg.channel, "send_messages",
                                   "the target channel")
            return
        if not perms.embed_links:
            await self._perm_error(msg.channel, "embed_links",
                                   "the target channel")
            return

        data["channel"] = channel
        await self._prompt_ping(data)

    async def _prompt_ping(self, data):
        """Part of the .say command. Prompts whether everyone should be pinged.

        Args:
            data: The session data for this command.
        """
        msg = data["msg"]
        perms = data["channel"].permissions_for(msg.author)
        if not perms.mention_everyone:
            await self._prompt_color(data)
            return

        await msg.channel.send("Do you want to ping everyone in the target"
                               + " channel? [Yes/No]")
        response = await self._input(msg.author, msg.channel)
        if response is None:
            return

        ping = False
        confirm = "Will not ping everyone in the target channel."
        if response.content.lower() == "yes":
            ping = True
            confirm = "Will ping everyone in the target channel."
        await msg.channel.send(confirm)

        data["ping"] = ping
        await self._prompt_color(data)

    async def _prompt_color(self, data):
        """Part of the .say command. Prompts the embed color.

        Args:
            data: The session data for this command.
        """
        msg = data["msg"]
        await msg.channel.send("Please enter a hexcode for the embed color"
                               + " (e.g. 0xFF0000 for red).")
        response = await self._input(msg.author, msg.channel)
        if response is None:
            return

        preset = {
            "green": 0x01dc40,
            "purple": 0xac00ff,
            "blue": 0x3f92ff,
            "gold": 0xffc901
        }
        try:
            if response.content.lower() in preset:
                color = preset[response.content.lower()]
            else:
                color = int(response.content, 16)
        except:
            await msg.channel.send("Invalid color code, aborting.")
            return

        data["color"] = color
        await self._prompt_title(data)

    async def _prompt_title(self, data):
        """Part of the .say command. Prompts the embed title.

        Args:
            data: The session data for this command.
        """
        msg = data["msg"]
        await msg.channel.send("Please enter a title for the embed.")
        response = await self._input(msg.author, msg.channel)
        if response is None:
            return

        data["title"] = response.content
        await self._prompt_text(data)

    async def _prompt_text(self, data):
        """Part of the .say command. Prompts the embed text.

        Args:
            data: The session data for this command.
        """
        msg = data["msg"]
        await msg.channel.send("Please enter a description for the embed. Type"
                               + " NONE to not have any description.")
        response = await self._input(msg.author, msg.channel)
        if response is None:
            return

        if response.content != "NONE":
            data["text"] = response.content
        await self._prompt_ask_add_field(data)

    async def _prompt_ask_add_field(self, data):
        """Part of the .say command. Asks whether embed fields should be added.

        Args:
            data: The session data for this command.
        """
        msg = data["msg"]
        await msg.channel.send("Do you want to add a field to the embed?"
                               + " [Yes/No]")
        response = await self._input(msg.author, msg.channel)
        if response is None:
            return

        if response.content.lower() == "yes":
            await self._prompt_add_field(data)
        else:
            await self._prompt_check(data)

    async def _prompt_add_field(self, data):
        """Part of the .say command. Adds a field to the embed.

        Args:
            data: The session data for this command.
        """
        msg = data["msg"]

        await msg.channel.send("Please enter a title for the field.")
        response = await self._input(msg.author, msg.channel)
        if response is None:
            return
        title = response.content

        await msg.channel.send("Please enter the field's contents.")
        response = await self._input(msg.author, msg.channel)
        if response is None:
            return
        content = response.content

        data["fields"][title] = content
        await self._prompt_ask_add_field(data)

    async def _prompt_check(self, data):
        """Part of the .say command. Constructs the embed and demonstrates it.

        Args:
            data: The session data for this command.
        """
        msg = data["msg"]

        embed = create_embed(data["title"], data["text"], data["color"],
                             data["fields"])
        headline = "**THIS IS HOW YOUR EMBED WILL LOOK LIKE**"
        if data["ping"]:
            headline += "\n(Will also ping everyone in the target channel)"
        await msg.channel.send(headline, embed=embed)

        await msg.channel.send("Confirm sending this embed? [Yes/Abort]")
        response = await self._input(msg.author, msg.channel)
        if response is None:
            return

        if response.content.lower() == "yes":
            tagline = ""
            if data["ping"]:
                tagline = "@everyone"
            await data["channel"].send(tagline, embed=embed)
        else:
            await msg.channel.send("Action aborted.")

    async def _input(self, author, channel):
        """Attempts to wait for a message by the given author.

        Args:
            author: The author to wait for.
            channel: The channel which is monitored.

        Returns:
            The message that was received, or None.
        """
        try:
            pred = lambda m: m.author == author and m.channel == channel
            response = await self._bot.wait_for("message", check=pred,
                                                timeout=60.0)
            return response
        except asyncio.TimeoutError:
            await channel.send("Request timed out.")
            return None

    async def _perm_error(self, channel, what, where):
        """Sends a permission error to the given channel.

        Args:
            channel: The channel.
            what: The permission that is needed.
            where: Where the permission is needed.
        """
        await self._error(channel, "Insufficient Permissions",
                          "You need `" + what + "` in " + where
                          + " to do this.")

    async def _error(self, channel, title, content):
        """Sends an error to the given channel.

        Args:
            channel: The channel.
            title: The title of the error.
            content: The error message.
        """
        embed = create_embed("Error - " + title, content, 0xAA0000)
        await channel.send(embed=embed)
