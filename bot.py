import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)


@bot.event
async def on_ready():
    import os, shutil
    cookie = os.getenv("COOKIE_DATA")
    print(f"COOKIE_DATA set: {bool(cookie)}, length: {len(cookie) if cookie else 0}")
    deno = shutil.which("deno")
    print(f"deno path: {deno or 'NOT FOUND'}")
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening,
        name="!help"
    ))


async def load_cogs():
    for cog in ["cogs.music", "cogs.utility"]:
        try:
            await bot.load_extension(cog)
            print(f"  ✅ Loaded {cog}")
        except Exception as e:
            print(f"  ❌ Failed to load {cog}: {e}")


@bot.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(
        title="📖 Bot Commands",
        color=discord.Color.blurple()
    )
    embed.add_field(
        name="🎵 Music",
        value=(
            "`!join` — Join your voice channel\n"
            "`!play <query>` — Play a YouTube song\n"
            "`!pause` — Pause playback\n"
            "`!resume` — Resume playback\n"
            "`!skip` — Skip current song\n"
            "`!stop` — Stop & disconnect\n"
            "`!queue` — Show song queue\n"
            "`!volume <1–100>` — Set volume"
        ),
        inline=False
    )
    embed.add_field(
        name="🛠️ Utility",
        value=(
            "`!ping` — Check bot latency\n"
            "`!serverinfo` — Server details\n"
            "`!userinfo [@user]` — User details\n"
            "`!avatar [@user]` — Show avatar\n"
            "`!poll <question> | <opt1> | <opt2>` — Create a poll\n"
            "`!say <message>` — Bot repeats your message\n"
            "`!clear <n>` — Delete last n messages"
        ),
        inline=False
    )
    embed.set_footer(text=f"Requested by {ctx.author.display_name}")
    await ctx.send(embed=embed)


async def main():
    async with bot:
        await load_cogs()
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            print("❌ DISCORD_TOKEN not set in .env")
            return
        await bot.start(token)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
