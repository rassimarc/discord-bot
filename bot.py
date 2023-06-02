import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

# Dictionary to store the options and queues
voting_options = {
    'option1': [],
    'option2': [],
    'option3': [],
    'option4': [],
    'option5': []
}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    # Check if the command is used in a server
    if ctx.guild is None:
        return

    # Check if the bot has permissions to manage channels
    if not ctx.guild.me.guild_permissions.manage_channels:
        await ctx.send("I don't have the permissions to manage channels.")
        return

    # Create the voting message
    voting_message = await ctx.send("Vote for an option:\n"
                                    "1. Option 1\n"
                                    "2. Option 2\n"
                                    "3. Option 3\n"
                                    "4. Option 4\n"
                                    "5. Option 5")

    # Add reactions to the voting message
    await voting_message.add_reaction("1️⃣")
    await voting_message.add_reaction("2️⃣")
    await voting_message.add_reaction("3️⃣")
    await voting_message.add_reaction("4️⃣")
    await voting_message.add_reaction("5️⃣")

@bot.event
async def on_raw_reaction_add(payload):
    # Check if the reaction is added to the voting message
    if payload.message_id == YOUR_VOTING_MESSAGE_ID:
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        channel = guild.get_channel(YOUR_TEXT_CHANNEL_ID)

        # Check if the user is in the guild and the channel exists
        if member and channel:
            # Check if the reaction corresponds to an option
            if str(payload.emoji) == "1️⃣":
                voting_options['option1'].append(member)
            elif str(payload.emoji) == "2️⃣":
                voting_options['option2'].append(member)
            elif str(payload.emoji) == "3️⃣":
                voting_options['option3'].append(member)
            elif str(payload.emoji) == "4️⃣":
                voting_options['option4'].append(member)
            elif str(payload.emoji) == "5️⃣":
                voting_options['option5'].append(member)

            # Check if each option has been chosen at least twice
            if all(len(queue) >= 2 for queue in voting_options.values()):
                # Dequeue each option twice and create new text channels
                for option, queue in voting_options.items():
                    for _ in range(2):
                        member = queue.pop(0)
                        new_channel = await guild.create_text_channel(f"{option}-{member.name}")
                        await new_channel.send(f"Welcome {member.mention} to the {option} channel!")

bot.run('YOUR_BOT_TOKEN')