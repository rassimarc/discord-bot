import disnake
from disnake.ext import commands
from disnake.ui import View, Button
from disnake import ui
from dotenv import load_dotenv
import os
import sqlite3


load_dotenv()


# Intents are required to get the member object when a button is clicked
intents = disnake.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix='#', intents=intents)

# Dictionary to store the options and queues
voting_options = {
    'TOP': [],
    'MID': [],
    'SUP': [],
    'ADC': [],
    'JUNGLE': []
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

    # Create the voting message with buttons
    view = View()
    view.add_item(Button( label="TOP", custom_id="TOP"))
    view.add_item(Button( label="MID", custom_id="MID"))
    view.add_item(Button( label="SUP", custom_id="SUP"))
    view.add_item(Button( label="ADC", custom_id="ADC"))
    view.add_item(Button( label="JUNGLE", custom_id="JUNGLE"))
    view.add_item(Button(style = disnake.ButtonStyle.red , label = "Leave" , custom_id = "leave"))

    voting_message = await ctx.send("Vote for an option:", view=view)

    # Store the message ID for later reference
    global voting_message_id
    voting_message_id = voting_message.id

@bot.event
async def on_button_click(inter):
    
    if inter.message.id == voting_message_id:
        guild = inter.guild
        member = guild.get_member(inter.user.id)
        channel = guild.get_channel(1114156750598328413)

        # Check if the user is in the guild and the channel exists
        if member and channel:
            # Check if the button label corresponds to an option
            option = inter.component.custom_id
            if option == 'leave':
                for options, queue in voting_options.items():
                    if member in queue:
                        queue.remove(member)

            if option in voting_options and member not in voting_options[option]:
                for options, queue in voting_options.items():
                    if member in queue:
                        queue.remove(member)
                voting_options[option].append(member)

                # Check if each option has been chosen at least twice
                if len(voting_options['TOP']) >= 2:
                    new_channel = await guild.create_text_channel(
                        name="Game1",
                        overwrites={
                            guild.default_role: disnake.PermissionOverwrite(read_messages=False),
                        }
                    )
                    # Dequeue each option twice and create new text channels
                    for option, queue in voting_options.items():
                        for _ in range(2):
                            if queue:
                                member = queue.pop(0)
                                await new_channel.set_permissions(member, read_messages=True)
                                await new_channel.send(f"Welcome {member.mention} to the Game1 channel!")

bot.run(os.getenv('TOKEN'))