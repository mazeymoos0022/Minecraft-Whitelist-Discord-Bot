# Minecraft Whitelist Discord Bot

This is a simple python scrpit that allows your users to whitelist themselves on a Minecraft Server via a Discord Bot

# Installation Proccess

## Linux

VIDEO COMING SOON!

1) Download the `main.py` file to your machine, a directory near your server directory

2) In the terminal run `pip install discord.py`, `pip install mcrcon` and `pip install aiohttp`

3) Go to the [Discord Developer Portal](https://www.discord.com/developers) and create a Discord Application, it will automatically assign it as a bot.

4) Under "Bot" click "Reset Token" and copy it into your clipboard or store safe. This is your `Bot Token` (If you are already using a MC-Discord plugin, you can use the same bot, just copy the token from the plugin config file).

5) Enable RCON on our server, head to the `server.properties` file and edit `enable-rcon=true` and `rcon.password=WHATEVER_PASSWORD_YOU_WANT`. (Optionally if `rcon.port` is not your preffer port, you can edit that too!)

6) Enter `main.py` and edit the config at the top, changing the below:

```
# Bot and Folder Config
DISCORD_TOKEN = 'DISCORD_TOKEN_HERE' # Put your Bot Token here
WHITELIST_PATH = 'PATH_TO_FOLDER/whitelist.json' # Change this to the location of the server files, if you put it in the same 
ADMIN_ROLE_NAME = 'ADMIN_ROLE' # Change this to the name of the role that your users have in able to whitelist (ie Member or everyone)

# Minecraft RCON configuration
RCON_HOST = 'localhost' # Don't Change Me 
RCON_PORT = 25575 # Must equal rcon.port
RCON_PASSWORD = 'RCON_PASSWORD' # Must be the same as rcon.password
```

7) Save the file and then restart your server

8) Run the file with `python3 main.py`