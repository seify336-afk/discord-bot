import discord
from discord.ext import commands
import yt_dlp
import asyncio
from collections import deque

YTDL_OPTIONS = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "default_search": "ytsearch",
    "socket_timeout": 10,
    "retries": 3,
    "nocheckcertificate": True,
    "extract_flat": False,
    "js_runtimes": {"nodejs": {"path": "/usr/bin/node"}},
    "postprocessors": [{
        "key": "FFmpegExtractAudio",
        "preferredcodec": "opus",
    }],
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn -ar 48000",
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get("title")
        self.url = data.get("webpage_url")
        self.duration = data.get("duration", 0)
        self.thumbnail = data.get("thumbnail")

    @classmethod
    async def from_query(cls, query, *, loop=None, volume=0.5):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(query, download=False)
        )
        if "entries" in data:
            data = data["entries"][0]
        filename = data["url"]
        return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data, volume=volume)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues: dict[int, deque] = {}
        self.volumes: dict[int, float] = {}

    def get_queue(self, guild_id):
        return self.queues.setdefault(guild_id, deque())

    def format_duration(self, seconds):
        if not seconds:
            return "?"
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        return f"{h}:{m:02}:{s:02}" if h else f"{m}:{s:02}"

    async def play_next(self, ctx):
        queue = self.get_queue(ctx.guild.id)
        if not queue:
            return
        query = queue.popleft()
        try:
            vol = self.volumes.get(ctx.guild.id, 0.5)
            player = await YTDLSource.from_query(query, loop=self.bot.loop, volume=vol)
            ctx.voice_client.play(
                player,
                after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop)
            )
            embed = discord.Embed(
                title="🎵 Now Playing",
                description=f"[{player.title}]({player.url})",
                color=discord.Color.green()
            )
            embed.add_field(name="Duration", value=self.format_duration(player.duration))
            if player.thumbnail:
                embed.set_thumbnail(url=player.thumbnail)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Error playing track: `{e}`")
            await self.play_next(ctx)

    @commands.command()
    async def join(self, ctx):
        """Join your voice channel."""
        if not ctx.author.voice:
            return await ctx.send("❌ You're not in a voice channel.")
        channel = ctx.author.voice.channel
        if ctx.voice_client:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()
        await ctx.send(f"✅ Joined **{channel.name}**")

    @commands.command()
    async def play(self, ctx, *, query: str):
        """Play a song from YouTube."""
        if not ctx.author.voice:
            return await ctx.send("❌ Join a voice channel first.")

        if not ctx.voice_client:
            await ctx.author.voice.channel.connect()

        queue = self.get_queue(ctx.guild.id)

        async with ctx.typing():
            if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                queue.append(query)
                await ctx.send(f"➕ Added to queue: **{query}** (position {len(queue)})")
            else:
                queue.append(query)
                await self.play_next(ctx)

    @commands.command()
    async def pause(self, ctx):
        """Pause playback."""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("⏸️ Paused.")
        else:
            await ctx.send("❌ Nothing is playing.")

    @commands.command()
    async def resume(self, ctx):
        """Resume playback."""
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("▶️ Resumed.")
        else:
            await ctx.send("❌ Nothing is paused.")

    @commands.command()
    async def skip(self, ctx):
        """Skip the current song."""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("⏭️ Skipped.")
        else:
            await ctx.send("❌ Nothing is playing.")

    @commands.command()
    async def stop(self, ctx):
        """Stop playback and disconnect."""
        if ctx.voice_client:
            self.get_queue(ctx.guild.id).clear()
            await ctx.voice_client.disconnect()
            await ctx.send("⏹️ Stopped and disconnected.")
        else:
            await ctx.send("❌ Not connected to a voice channel.")

    @commands.command()
    async def queue(self, ctx):
        """Show the song queue."""
        q = self.get_queue(ctx.guild.id)
        if not q:
            return await ctx.send("📭 Queue is empty.")
        items = "\n".join(f"`{i+1}.` {title}" for i, title in enumerate(q))
        embed = discord.Embed(title="🎵 Queue", description=items, color=discord.Color.blurple())
        embed.set_footer(text=f"{len(q)} song(s) in queue")
        await ctx.send(embed=embed)

    @commands.command()
    async def volume(self, ctx, vol: int):
        """Set volume (1–100)."""
        if not 1 <= vol <= 100:
            return await ctx.send("❌ Volume must be between 1 and 100.")
        self.volumes[ctx.guild.id] = vol / 100
        if ctx.voice_client and ctx.voice_client.source:
            ctx.voice_client.source.volume = vol / 100
        await ctx.send(f"🔊 Volume set to **{vol}%**")


async def setup(bot):
    await bot.add_cog(Music(bot))
