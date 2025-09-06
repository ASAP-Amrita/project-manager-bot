import discord
import asyncio

from discord import Embed
from discord.ext import commands
from discord.ext.commands import has_permissions, MissingPermissions

from config import TOKEN

intents = discord.Intents.default()
intents.message_content = True  # Enable the message content intent
intents.members = True  # Enable the members intent

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

bot.remove_command("help")


#=======================================================================================================================
# Google Sheets Integration
#=======================================================================================================================
import gspread
from google.oauth2.service_account import Credentials


scope = ['https://www.googleapis.com/auth/spreadsheets']

creds = Credentials.from_service_account_file('creds.json', scopes=scope)
client = gspread.authorize(creds)

sheet_id = "1vQNrdfFPWkCQHPBgSb-imKLcl0o0HW0_PqJgJMOYKS8"
sheet = client.open_by_key(sheet_id)

#=======================================================================================================================
# Commands
#=======================================================================================================================
@bot.command(name='Commit', aliases=["commit","cum","COMMIT"], help="Commit a message to the Google Sheet.")
async def commit(ctx,*,Message: str):
    user = ctx.author
    message = ctx.message
    guild_id = message.guild.id
    channel_id = message.channel.id
    message_id = message.id
    message_link = f"https://discord.com/channels/{guild_id}/{channel_id}/{message_id}"
    nickname = user.display_name  # This gets the server nickname
    table_row_number = int(sheet.sheet1.acell('G2').value)
    user_cell = sheet.sheet1.find(nickname.upper())
    index_data = int(sheet.sheet1.cell(2,user_cell.col).value)
    nickname = nickname.lower()
    commit_id = nickname[:5]+'#'+str(index_data)
    #sheet.sheet1.update_cell(row_number,1, commit_id)  #commit id
    sheet.sheet1.update_cell(table_row_number,1, commit_id)
    sheet.sheet1.update_cell(table_row_number,2, nickname)  #server nickname
    sheet.sheet1.update_cell(table_row_number,3, message_link)
    sheet.sheet1.update_cell(table_row_number,4, ctx.message.created_at.strftime("%Y-%m-%d %H:%M:%S"))
    sheet.sheet1.update_cell(table_row_number,5, Message)
    await ctx.send(f"Message committed to Google Sheet by {nickname} with Commit id {commit_id} .")

@bot.command(name='Update', aliases=["update","UPDATE"])
async def update(ctx,commit_id: str,*,Message: str):
    user = ctx.author
    nickname = user.display_name
    message = ctx.message
    guild_id = message.guild.id
    channel_id = message.channel.id
    message_id = message.id
    message_link = f"https://discord.com/channels/{guild_id}/{channel_id}/{message_id}"
    if(commit_id.lower() == 'last'):
        table_row_number = int(sheet.sheet1.acell('G2').value) -1
        commit_id = sheet.sheet1.cell(table_row_number,1).value
    else:
        table_row_number = sheet.sheet1.find(commit_id).row 
    sheet.sheet1.update_cell(table_row_number,3, message_link)
    sheet.sheet1.update_cell(table_row_number,4, ctx.message.created_at.strftime("%Y-%m-%d %H:%M:%S"))
    sheet.sheet1.update_cell(table_row_number,5, Message)
    await ctx.send(f"Message Updated in Google Sheet by {nickname} to Commit id {commit_id} .")

@bot.command(name='List', aliases=["list","LIST"])
async def list(ctx,n:str = "1"):
    if '#' in n.lower():
        commit_id = n
        table_row_number = sheet.sheet1.find(commit_id).row 
        await ctx.send(f"Commit id:{sheet.sheet1.cell(table_row_number,1).value}, Message:{sheet.sheet1.cell(table_row_number,5).value}")
        return
    n = int(n)
    table_row_number = int(sheet.sheet1.acell('G2').value)
    if n > table_row_number -2:
        await ctx.send(f"Only {table_row_number -2} commits are available.")
        return
    if n <= 0:
        await ctx.send("Please provide a positive integer for the number of commits to list.")
        return
    await ctx.send(f"Last {n} commits are:")
    for i in range(n):
        table_row_number -= 1
        await ctx.send(f"Commit id:{sheet.sheet1.cell(table_row_number,1).value}, Message:{sheet.sheet1.cell(table_row_number,5).value}")

    

bot.run(TOKEN)
