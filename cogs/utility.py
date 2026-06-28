import discord
from discord.ext import commands
import time


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """Check bot latency."""
        latency = round(self.bot.latency * 1000)
        color = discord.Color.green() if latency < 100 else discord.Color.orange() if latency < 200 else discord.Color.red()
        embed = discord.Embed(title="🏓 Pong!", description=f"Latency: **{latency}ms**", color=color)
        await ctx.send(embed=embed)

    @commands.command()
    async def serverinfo(self, ctx):
        """Show server information."""
        guild = ctx.guild
        embed = discord.Embed(title=f"📊 {guild.name}", color=discord.Color.blurple())
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
        embed.add_field(name="Members", value=guild.member_count, inline=True)
        embed.add_field(name="Channels", value=len(guild.channels), inline=True)
        embed.add_field(name="Roles", value=len(guild.roles), inline=True)
        embed.add_field(name="Boosts", value=guild.premium_subscription_count, inline=True)
        embed.add_field(name="Created", value=guild.created_at.strftime("%b %d, %Y"), inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    async def userinfo(self, ctx, member: discord.Member = None):
        """Show information about a user."""
        member = member or ctx.author
        roles = [r.mention for r in member.roles if r.name != "@everyone"]
        embed = discord.Embed(title=f"👤 {member}", color=member.color)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Nickname", value=member.nick or "None", inline=True)
        embed.add_field(name="Bot", value="Yes" if member.bot else "No", inline=True)
        embed.add_field(name="Joined Server", value=member.joined_at.strftime("%b %d, %Y"), inline=True)
        embed.add_field(name="Account Created", value=member.created_at.strftime("%b %d, %Y"), inline=True)
        embed.add_field(name=f"Roles ({len(roles)})", value=" ".join(roles) if roles else "None", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def avatar(self, ctx, member: discord.Member = None):
        """Show a user's avatar."""
        member = member or ctx.author
        embed = discord.Embed(title=f"🖼️ {member.display_name}'s Avatar", color=discord.Color.blurple())
        embed.set_image(url=member.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def poll(self, ctx, *, args: str):
        """Create a poll. Usage: !poll Question | Option1 | Option2"""
        parts = [p.strip() for p in args.split("|")]
        if len(parts) < 3:
            return await ctx.send("❌ Usage: `!poll Question | Option 1 | Option 2`")

        question, *options = parts
        if len(options) > 10:
            return await ctx.send("❌ Maximum 10 options.")

        EMOJI = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
        description = "\n".join(f"{EMOJI[i]} {opt}" for i, opt in enumerate(options))

        embed = discord.Embed(title=f"📊 {question}", description=description, color=discord.Color.gold())
        embed.set_footer(text=f"Poll by {ctx.author.display_name}")

        await ctx.message.delete()
        msg = await ctx.send(embed=embed)
        for i in range(len(options)):
            await msg.add_reaction(EMOJI[i])

    @commands.command()
    async def say(self, ctx, *, message: str):
        """Make the bot say something."""
        await ctx.message.delete()
        await ctx.send(message)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int = 5):
        """Delete the last n messages (default: 5). Requires Manage Messages."""
        if amount < 1 or amount > 100:
            return await ctx.send("❌ Amount must be between 1 and 100.")
        deleted = await ctx.channel.purge(limit=amount + 1)
        msg = await ctx.send(f"🗑️ Deleted **{len(deleted) - 1}** message(s).")
        await msg.delete(delay=3)

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You need **Manage Messages** permission for that.")

    @commands.command()
    async def invite(self, ctx):
        """Get the bot's invite link."""
        perms = discord.Permissions(
            send_messages=True,
            read_messages=True,
            manage_messages=True,
            embed_links=True,
            add_reactions=True,
            connect=True,
            speak=True
        )
        url = discord.utils.oauth_url(self.bot.user.id, permissions=perms)
        embed = discord.Embed(title="📨 Invite Me!", description=f"[Click here to invite the bot]({url})", color=discord.Color.green())
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Utility(bot))
