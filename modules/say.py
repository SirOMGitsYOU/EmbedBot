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

        chk = lambda p: p.manage_messages
        permchk = await self._check_perms(msg.author, msg.channel, chk)
        if not permchk:
            await self._perm_error(msg.channel, ["manage_messages"],
                                   "this channel")
            return

        data = {
            "msg": msg,
            "channel": None,
            "ping": False,
            "color": 1,
            "title": "",
            "text": "",
            "image": "",
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

        chk = lambda p: p.manage_messages and p.send_messages and p.embed_links
        permchk = await self._check_perms(msg.author, channel, chk)
        if not permchk:
            await self._perm_error(msg.channel, [
                "manage_messages",
                "send_messages",
                "embed_links"
            ], "the target channel")
            return

        data["channel"] = channel
        await self._prompt_ping(data)

    async def _prompt_ping(self, data):
        """Part of the .say command. Prompts whether everyone should be pinged.

        Args:
            data: The session data for this command.
        """
        msg = data["msg"]

        chk = lambda p: p.mention_everyone
        permchk = await self._check_perms(msg.author, data["channel"], chk)
        if not permchk:
            await self._prompt_color(data)
            return

        await msg.channel.send("Who should be pinged (Ie `everyone`, `here`, @role, @user)")
        response = await self._input(msg.author, msg.channel)

        if response is None:
            return
           
        if response.content.lower() == "none":
            ping = None
            confirm = "Will not ping anyone in the target channel."
  
        else:
            ping = response.content.lower()
            if response.content.lower() == "everyone":
                ping = "@everyone"
            if response.content.lower() == "here":
                ping = "@here"
            confirm = "Will ping `" + ping + "` in the target channel."
            




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

        presets = self._frontend.config.get("colors", {
            "green": 0x01dc40,
            "purple": 0xac00ff,
            "blue": 0x3f92ff,
            "gold": 0xffc901,
            "red": 0xFF0000
        })
        try:
            if response.content.lower() in presets:
                color = presets[response.content.lower()]
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
                               + " None to not have any description.")
        response = await self._input(msg.author, msg.channel)
        if response is None:
            return

        if response.content.lower() != "none":
            data["text"] = response.content
        await self._prompt_image(data)

    async def _prompt_image(self, data):
        """Part of the .say command. Prompts the embed image.

        Args:
            data: The session data for this command.
        """
        msg = data["msg"]
        await msg.channel.send("Please enter the URL of the image/GIF you'd like to use."
                               + " Type none to no Image/GIF attached.")
        response = await self._input(msg.author, msg.channel)
        if response is None:
            return

        if response.content.lower() != "none":
            data["image"] = response.content
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

        embed = create_embed(data["title"], data["text"], data["color"], data["image"], data["fields"])
        headline = "**THIS IS WHAT YOUR EMBED WILL LOOK LIKE**"
        if data["ping"] is not None:
            headline += "\n(Will also ping `" + data["ping"] \
                        + "` in the target channel)"
        await msg.channel.send(headline, embed=embed)

        await msg.channel.send("Confirm sending this embed? [Yes/Abort]")
        response = await self._input(msg.author, msg.channel)
        if response is None:
            return

        if response.content.lower() == "yes":
            tagline = ""
            if data["ping"] is not None:
                tagline = data["ping"]
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

    async def _check_perms(self, member, channel, chk):
        """Checks the permissions for the given user.

        Args:
            member: The member.
            channel: The channel.
            chk: A function taking a permissions object that checks permissions.

        Returns:
            True if and only if the permission check succeeded.
        """
        whitelist_roles = self._frontend.config.get("whitelist-roles", [
            "Admin"
        ])
        use_real_perms = self._frontend.config.get("use-real-perms", True)

        # First check: Whitelisted roles
        for role in member.roles:
            if role.name in whitelist_roles:
                return True

        # Second check: Use real perms, if wanted.
        if use_real_perms:
            perms = channel.permissions_for(member)
            return chk(perms)
        else:
            return False

    async def _perm_error(self, channel, what, where):
        """Sends a permission error to the given channel.

        Args:
            channel: The channel.
            what: The permissions that are needed.
            where: Where the permission is needed.
        """
        use_real_perms = self._frontend.config.get("use-real-perms", True)
        if not use_real_perms:
            await self._error(channel, "Insufficient Permissions", "You need to"
                              + " be whitelisted in order to do this.")
            return

        whats = ", ".join(map(lambda s: "`%s`" % s, what))
        await self._error(channel, "Insufficient Permissions",
                          "You need " + whats + " in " + where
                          + " in order to do this.")

    async def _error(self, channel, title, content):
        """Sends an error to the given channel.

        Args:
            channel: The channel.
            title: The title of the error.
            content: The error message.
        """
        embed = create_embed("Error - " + title, content, "", 0xAA0000)
        await channel.send(embed=embed)
