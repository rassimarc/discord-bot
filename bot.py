import disnake
from disnake.ext import commands
from disnake.ui import View, Button
from disnake import ui
from dotenv import load_dotenv
import os

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
    global category
    category = await ctx.guild.create_category("League of Legends Games")
    # Check if the command is used in a server
    if ctx.guild is None:
        return

    # Check if the bot has permissions to manage channels
    if not ctx.guild.me.guild_permissions.manage_channels:
        await ctx.send("I don't have the permissions to manage channels.")
        return


    embed = disnake.Embed(
        title="⚔ League of Legends Queue ⚔",
        description="Click the buttons below to vote for an option.",
        color=disnake.Color.red()
    )
    with open("LOL.jpg", "rb") as file:
        embed.set_image(url="attachment://lol_image.jpg")
        file = disnake.File(file, filename="lol_image.jpg")
        await ctx.send(embed=embed, file=file)    #embed.set_thumbnail(url="https://media-cldnry.s-nbcnews.com/image/upload/newscms/2016_27/1141049/hot-grandpa-001-tease-today-160705.JPG")  # Replace with your bot thumbnail URL

    # Create the voting message with buttons
    view = View()
    view.add_item(Button(style=disnake.ButtonStyle.green, label="Top", custom_id="TOP"))
    view.add_item(Button(style=disnake.ButtonStyle.green, label="Mid", custom_id="MID"))
    view.add_item(Button(style=disnake.ButtonStyle.green, label="Support", custom_id="SUP"))
    view.add_item(Button(style=disnake.ButtonStyle.green, label="ADC", custom_id="ADC"))
    view.add_item(Button(style=disnake.ButtonStyle.green, label="Jungle", custom_id="JUNGLE"))
    view.add_item(Button(style = disnake.ButtonStyle.red , label = "Leave" , custom_id = "leave"))

    voting_message = await ctx.send(view=view)

    # Store the message ID for later reference
    global voting_message_id
    voting_message_id = voting_message.id

@bot.event
async def on_button_click(inter):
    #await inter.response.defer()  # Acknowledge the interaction

    if inter.message.id == voting_message_id:
        guild = inter.guild
        member = guild.get_member(inter.user.id)
        channel = guild.get_channel(inter.channel_id)

        # Check if the user is in the guild and the channel exists
        if member and channel:
            # Check if the button label corresponds to an option
            option = inter.component.custom_id
            if option != 'leave':
                embed = disnake.Embed(
                    title="Queue Joined",
                    description=f"✅ You have joined the queue as a {option}.",
                    color=disnake.Color.green()
                )
                await inter.response.send_message(embed=embed, ephemeral=True, delete_after=10)
            else:
                embed = disnake.Embed(
                    title="Queue Left",
                    description="❌ You have left the queue.",
                    color=disnake.Color.red()
                )
                await inter.response.send_message(embed=embed, ephemeral=True, delete_after=10)
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
                #if len(voting_options['TOP']) >= 1:
                if all(len(queue) >= 2 for queue in voting_options.values()):
                    new_channel = await guild.create_text_channel(
                        name="Game",
                        category=category,
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
                                await new_channel.send(f"Welcome {member.mention} to the channel!")

bot.run(os.getenv('TOKEN'))