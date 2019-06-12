from misc.adapter import create_bot, connect_bot
from embedbot import EmbedBot

if __name__ == "__main__":
    rf = EmbedBot()
    bot = create_bot(rf)
    rf.bot = bot
    connect_bot(bot)
