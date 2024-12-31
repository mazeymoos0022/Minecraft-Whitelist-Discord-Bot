import discord
from discord.ext import commands
import json
import os
from datetime import datetime
import asyncio
from mcrcon import MCRcon
import aiohttp  # For async HTTP requests to Mojang API

# Bot and Folder Config
DISCORD_TOKEN = 'DISCORD_TOKEN_HERE'
WHITELIST_PATH = 'PATH_TO_FOLDER/whitelist.json'
ADMIN_ROLE_NAME = 'ADMIN_ROLE'

# Minecraft RCON configuration
RCON_HOST = 'localhost' # Don't Change Me
RCON_PORT = 25575
RCON_PASSWORD = 'RCON_PASSWORD'

# Initialize bot with command prefix !
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

async def get_minecraft_uuid(username):
    """Fetch UUID from Mojang API"""
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://api.mojang.com/users/profiles/minecraft/{username}') as response:
            if response.status == 200:
                data = await response.json()
                # Convert UUID to hyphenated format
                uuid = data['id']
                hyphenated_uuid = f"{uuid[:8]}-{uuid[8:12]}-{uuid[12:16]}-{uuid[16:20]}-{uuid[20:]}"
                return hyphenated_uuid, data['name']  # Returns correct case of username too
            return None, None

async def reload_whitelist():
    """Reload the whitelist on the Minecraft server using RCON"""
    try:
        with MCRcon(RCON_HOST, RCON_PASSWORD, RCON_PORT) as mcr:
            resp = mcr.command("whitelist reload")
            return resp
    except:
        return "Failed to reload whitelist on server. Check RCON settings."

async def load_whitelist():
    """Load the current whitelist from file"""
    try:
        with open(WHITELIST_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

async def save_whitelist(whitelist_data):
    """Save the whitelist to file and reload it on the server"""
    with open(WHITELIST_PATH, 'w') as f:
        json.dump(whitelist_data, f, indent=4)
    return await reload_whitelist()

def has_admin_role():
    """Check if user has admin role or is server admin"""
    async def predicate(ctx):
        if ctx.author == ctx.guild.owner:
            return True
        
        if ctx.author.guild_permissions.administrator:
            return True
            
        admin_role = discord.utils.get(ctx.guild.roles, name=ADMIN_ROLE_NAME)
        if admin_role is None:
            try:
                admin_role = await ctx.guild.create_role(name=ADMIN_ROLE_NAME)
                await ctx.send(f"Created {ADMIN_ROLE_NAME} role. Please assign it to trusted users.")
            except discord.Forbidden:
                await ctx.send("Error: Bot doesn't have permission to create roles.")
                return False
        
        return admin_role in ctx.author.roles
    return commands.check(predicate)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Invite link: https://discord.com/api/oauth2/authorize?client_id={bot.user.id}&permissions=2147483648&scope=bot')

@bot.command(name='whitelist')
@has_admin_role()
async def whitelist_add(ctx, minecraft_username: str):
    """Add a player to the whitelist"""
    # First, verify the username and get UUID
    uuid, correct_username = await get_minecraft_uuid(minecraft_username)
    
    if not uuid:
        await ctx.send(f'Error: Could not find Minecraft player "{minecraft_username}". Please check the username.')
        return
    
    whitelist = await load_whitelist()
    
    # Check if player is already whitelisted (using UUID to be completely accurate)
    if any(player['uuid'] == uuid for player in whitelist):
        await ctx.send(f'Player {correct_username} is already whitelisted!')
        return
    
    whitelist.append({
        "uuid": uuid,
        "name": correct_username
    })
    
    reload_response = await save_whitelist(whitelist)
    await ctx.send(f'Added {correct_username} (UUID: {uuid}) to the whitelist!\nServer response: {reload_response}')

@bot.command(name='unwhitelist')
@has_admin_role()
async def whitelist_remove(ctx, minecraft_username: str):
    """Remove a player from the whitelist"""
    whitelist = await load_whitelist()
    
    # Try to get UUID first for accurate removal
    uuid, correct_username = await get_minecraft_uuid(minecraft_username)
    
    initial_length = len(whitelist)
    if uuid:
        # Remove by UUID if we found one
        whitelist = [player for player in whitelist if player['uuid'] != uuid]
    else:
        # Fall back to name-based removal if UUID lookup failed
        whitelist = [player for player in whitelist if player['name'].lower() != minecraft_username.lower()]
    
    if len(whitelist) == initial_length:
        await ctx.send(f'Player {minecraft_username} was not found in the whitelist!')
        return
    
    reload_response = await save_whitelist(whitelist)
    await ctx.send(f'Removed {correct_username or minecraft_username} from the whitelist!\nServer response: {reload_response}')

@bot.command(name='listwhitelist')
@has_admin_role()
async def whitelist_list(ctx):
    """List all whitelisted players"""
    whitelist = await load_whitelist()
    
    if not whitelist:
        await ctx.send('The whitelist is empty!')
        return
    
    player_list = '\n'.join([f"- {player['name']} (UUID: {player['uuid']})" for player in whitelist])
    await ctx.send(f'**Whitelisted Players:**\n{player_list}')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send(f"You don't have permission to use this command! You need the '{ADMIN_ROLE_NAME}' role or administrator permissions.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing required argument! Please check the command usage.")
    else:
        await ctx.send(f"An error occurred: {str(error)}")

# Run the bot
bot.run(DISCORD_TOKEN)
