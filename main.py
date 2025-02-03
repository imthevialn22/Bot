import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix=",", intents=intents)

# Dictionary to store slot information, including ping limits
slots = {}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# Find or create the "Slots" category
async def get_or_create_category(guild):
    category = discord.utils.get(guild.categories, name="Slots")
    if category is None:
        category = await guild.create_category("Slots")
    return category

# Create a new slot (channel) with ping limits
@bot.command()
async def slot(ctx, user: discord.Member, slot_tier: str, duration: str, everyone_pings: int = 3, here_pings: int = 3):
    guild = ctx.guild
    category = await get_or_create_category(guild)
    
    # Create a private channel for the user
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        bot.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
    }
    
    channel_name = f"{user.name}-slot"
    channel = await guild.create_text_channel(name=channel_name, category=category, overwrites=overwrites)
    
    # Store slot details
    slots[user.id] = {
        "tier": slot_tier,
        "duration": duration,
        "status": "active",
        "channel": channel.id,
        "everyone_pings": everyone_pings,
        "here_pings": here_pings
    }

    await ctx.send(f"Created slot for {user.mention} in {channel.mention} (Tier: {slot_tier}, Duration: {duration}).")

# Command to ping @everyone in the slot (limited)
@bot.command()
async def everyone(ctx):
    user = ctx.author
    if user.id in slots:
        slot_info = slots[user.id]
        if slot_info["everyone_pings"] > 0:
            slot_info["everyone_pings"] -= 1
            await ctx.send(f"@everyone - Ping by {user.mention}")
            await show_pings(ctx)
        else:
            await ctx.send(f"{user.mention}, you have **0** @everyone pings left.")
    else:
        await ctx.send(f"{user.mention}, you don't have a slot.")

# Command to ping @here in the slot (limited)
@bot.command()
async def here(ctx):
    user = ctx.author
    if user.id in slots:
        slot_info = slots[user.id]
        if slot_info["here_pings"] > 0:
            slot_info["here_pings"] -= 1
            await ctx.send(f"@here - Ping by {user.mention}")
            await show_pings(ctx)
        else:
            await ctx.send(f"{user.mention}, you have **0** @here pings left.")
    else:
        await ctx.send(f"{user.mention}, you don't have a slot.")

# Show remaining pings in an embed (like in the image)
async def show_pings(ctx):
    user = ctx.author
    if user.id in slots:
        slot_info = slots[user.id]
        embed = discord.Embed(color=discord.Color.blue(), description="**Pings left:**")
        embed.add_field(name="@here", value=f"**{slot_info['here_pings']}x**", inline=True)
        embed.add_field(name="@everyone", value=f"**{slot_info['everyone_pings']}x**", inline=True)
        embed.set_footer(text="Use our #🔗 | middleman to secure your transactions.")
        await ctx.send(embed=embed)

# Command to set/reset ping limits (only admins can use)
@bot.command()
@commands.has_permissions(administrator=True)
async def set_pings(ctx, user: discord.Member, everyone_pings: int, here_pings: int):
    if user.id in slots:
        slots[user.id]["everyone_pings"] = everyone_pings
        slots[user.id]["here_pings"] = here_pings
        await ctx.send(f"Updated pings for {user.mention}: @everyone = {everyone_pings}, @here = {here_pings}.")
        await show_pings(ctx)
    else:
        await ctx.send(f"{user.mention} does not have a slot.")

# Run the bot (Replace 'YOUR_BOT_TOKEN' with your actual bot token)
bot.run("cPRQgb0KnnfqcSeUw")
