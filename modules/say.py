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

        allow = False
        for role in msg.author.roles:
            if role.permissions.administrator:
                allow = True
        if not allow:
            log("Forbidden: .say for {0}".format(msg.author))
            return

        if len(args) == 0:
            embed = create_embed("Error - No arguments",
                                 "Syntax: .say COLOR §§ TITLE §§ CONTENT",
                                 0xAA0000)
            await self._bot.send_message(msg.channel, embed=embed)
            return

        argstr = " ".join(args)
        realargs = argstr.split("§§")
        if len(realargs) != 3:
            embed = create_embed("Error - To few real arguments",
                                 "Syntax: .say COLOR §§ TITLE §§ CONTENT",
                                 0xAA0000)
            await self._bot.send_message(msg.channel, embed=embed)
            return

        try:
            color = int(realargs[0], 16)
            title = realargs[1]
            content = realargs[2]
        except:
            embed = create_embed("Error - Parsing failed",
                                 "Example: .say 0xFF0000 §§ Hey there! §§ OK?",
                                 0xAA0000)
            await self._bot.send_message(msg.channel, embed=embed)
            return

        embed = create_embed(title, content, color)
        await self._bot.send_message(msg.channel, embed=embed)
