import os
import discord
from dotenv import load_dotenv
from proxmoxer import ProxmoxAPI
import time
import socket
import re
import json

# SETUP
load_dotenv()

with open('server_conf.json', 'r') as fp:
    SERVER_CONF = json.load(fp)

token=os.getenv('TOKEN')
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

def help():
    help_msg = """
    Basic usage: `!js-{server}-{command}`
    **VALID SERVER NAMES**
        `all` - All hosted servers (can only be used with `!js-all-status`)
    """

    for k in SERVER_CONF.keys():
        help_msg += "\t`" + k + '` - ' + SERVER_CONF[k]['messages']['display_name'] + '\n\t'

    help_msg += """
    **COMMANDS**
        `up` - Request the server to come online
        `down` - Request the server to shutdown
        `status` - Request the status of a specific server
        `info` - Prints out connection info"""
    help_msg += '\nEx. To request the minecraft server come online: `!js-minecraft-up`'
    return help_msg

def print_status(api):
    status_str = "**SERVER STATUS**\n------------------\n"
    for serv in SERVER_CONF.keys():
        container = api.nodes('pve').lxc(SERVER_CONF[serv]['CTID'])
        status_str += f'**{SERVER_CONF[serv]["messages"]["display_name"]}** -'
        # get status of each CT
        if container.status.current().get()['status'] == 'running':
            status_str += ' Running'
        else:
            status_str += ' Offline'
        status_str += '\n'

def print_info(server_name):
    info_str = ''
    return info_str

def check_status(host, port, timeout=5):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
    except:
        return False
    else:
        sock.close()
        return True
    

def handle_servercmd(server_name, command, api):

    message_flairs = SERVER_CONF[server_name]['messages']

    container_id = SERVER_CONF[server_name]['CTID']
    container = api.nodes('pve').lxc(container_id)
    if command == "up":
        if container.status.current().get()['status'] == 'running':
            yield "Server is already running!"
            return
            # TODO: show online players
        container.status.start.post()
        yield message_flairs['starting']
        
        # let server start before checking
        startup_time = 15
        if 'startup_time' in SERVER_CONF[server_name]:
            startup_time = SERVER_CONF[server_name]['startup_time']
        time.sleep(startup_time)
        
        CT_host = SERVER_CONF[server_name]['host']
        CT_port = SERVER_CONF[server_name]['port']
        if check_status(CT_host, CT_port):
            yield message_flairs['on']
        else:
            yield 'Unable to open server'

    elif command == "down":
        if container.status.current().get()['status'] == 'stopped':
            yield 'Server already down'
            return

        container.status.stop.post()
        yield message_flairs['stopping']

    elif command == 'status':
        if check_status(CT_host, CT_port):
            yield 'Server is up!'
        else:
            yield 'Server is offline'

    elif command == 'info':
        yield print_info(server_name)
    else:
        yield False

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    

@client.event
async def on_message(message):
    
    if message.author == client.user:
        return
    
    print(message.author)
    return
    
    prox_host = os.getenv('PROXMOX_HOST')
    prox_user = os.getenv('PROXMOX_USER')
    prox_password = os.getenv('PROXMOX_PASSWORD')

    api = ProxmoxAPI(
        prox_host,
        user=prox_user,
        password=prox_password,
        verify_ssl=False
    )
            
    if message.content[:4] == '!js-':
        tokens = message.content[4:].split('-')
        command = tokens[-1]
        serverName = '-'.join(tokens[:-1])
        print('-' * 50)
        print('servername ' + serverName)
        print('command ' + command)
        print('-' * 50)

        if message.content[4:] == 'help':
            await message.channel.send(help())
            return
        if message.content[4:] == 'info':
            for serv in SERVER_CONF.keys():
                print_info(serv)
            return
        if (message.content[4:] == 'status' or (serverName == 'all' and command=='status')):
            print_status(api)
        await message.channel.send('Not a valid command. Type \'!js-help\' for a list of commands')
        
        if serverName in SERVER_CONF.keys():
            for res in handle_servercmd(serverName, command, api):        
                if not res:
                    await message.channel.send(help())
                    return
                await message.channel.send(res)

client.run(token)