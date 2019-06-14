from misc.adapter import log
from misc.config import Config
from modules.say import SayModule
import discord


class EmbedBot:

    def __init__(self):
        self.bot = None
        self.server = None
        self.modules = []
        self.config = Config()

    async def on_ready(self):
        """Event handler for when the bot is ready."""
        log("Initializing bot presence...")
        await self.bot.change_presence(activity=discord.Game(name="Skynet"))

        log("Retrieving server...")
        for server in self.bot.guilds:
            self.server = server
            log("Assigned main server: {0.name}".format(self.server))
            break

        if self.server.large:
            log("Requesting offline users on server...")
            await self.bot.request_offline_members(self.server)

        log("Loading modules...")
        self.modules = [
            SayModule(self, self.bot)
        ]

        log("Initialization complete.")

    async def on_message_delete(self, msg):
        """Event handler for when a message is deleted.

        Args:
            msg: The message that was deleted.
        """
        for module in self.modules:
            await module.on_message_delete(msg)

    async def on_message_edit(self, before, after):
        """Event handler for when a message is edited.

        Args:
            before: The message before the edit.
            after: The message after the edit.
        """
        for module in self.modules:
            await module.on_message_edit(before, after)

    async def on_member_join(self, member):
        """Event handler for when a member joins the server.

        Args:
            member: The member that joined the server.
        """
        for module in self.modules:
            await module.on_member_join(member)

    async def on_member_remove(self, member):
        """Event handler for when a member leaves the server.

        Args:
            member: The member that left the server.
        """
        for module in self.modules:
            await module.on_member_remove(member)

    async def on_message(self, msg):
        """Event handler for messages.

        Args:
            msg: The message.
        """
        for module in self.modules:
            await module.on_message(msg)

    async def handle_command(self, msg, cmd, args):
        """Event handler for commands.

        Args:
            msg: The message that contains the command.
            cmd: The command.
            args: The arguments provided.
        """
        for module in self.modules:
            await module.on_command(msg, cmd, args)
