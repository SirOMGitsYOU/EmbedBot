from misc.util import create_embed, log
from modules.module import Module


class SayModule(Module):

    def __init__(self, frontend, bot):
        """Constructor."""
        super().__init__(frontend, bot)
        self._syntax = ("Syntax: .say COLOUR §§ TITLE §§ CONTENT\n\n"
                        + "Optionally add fields at the end of the command:\n"
                        + ".say 0xFF0000 §§ Test §§ Text §§ Field 1 §§ Desc 1"
                        + " §§ Field 2 §§ Desc 2\n\n"
                        + "Replace .say by .announce to ping `@everyone`.\n\n"
                        + "In order to target another channel, append the"
                        + " channel ID to the command:\n"
                        + ".say743841223333 ...\n"
                        + ".announce856823533737772 ...\n")

    async def on_command(self, msg, cmd, args):
        """Event handler for commands.

        Args:
            msg: The message.
            cmd: The command label.
            args: The command arguments.
        """
        if not cmd.startswith("say") and not cmd.startswith("announce"):
            return
        announce = True if cmd.startswith("announce") else False

        channel = None
        if announce:
            if cmd != "announce":
                channel = int(cmd[8:])
        else:
            if cmd != "say":
                channel = int(cmd[3:])

        allow = False
        for role in msg.author.roles:
            if role.permissions.administrator:
                allow = True
        if not allow:
            log("Forbidden: .say for {0}".format(msg.author))
            return

        argstr = " ".join(args)
        realargs = argstr.split("§§")
        if len(realargs) < 3:
            embed = create_embed("Error - To few arguments", self._syntax,
                                 0xAA0000)
            await msg.channel.send(embed=embed)
            return
        if len(realargs) % 2 != 1:
            embed = create_embed("Error - Unbalanced fields", self._syntax,
                                 0xAA0000)
            await msg.channel.send(embed=embed)
            return

        try:
            color = int(realargs[0], 16)
            title = realargs[1]
            content = realargs[2]
            data = {}
            fieldlen = (len(realargs) -3) // 2
            for i in range(fieldlen):
                header = realargs[3 + i * 2]
                desc = realargs[4 + i * 2]
                data[header] = desc
        except:
            embed = create_embed("Error - Parsing failed", self._syntax,
                                 0xAA0000)
            await msg.channel.send(embed=embed)
            return

        tagline = ""
        if announce:
            tagline = "@everyone"
        embed = create_embed(title, content, color, data)
        if channel is None:
            channel = msg.channel
        else:
            channel = msg.channel.guild.get_channel(channel)
        await channel.send(tagline, embed=embed)
