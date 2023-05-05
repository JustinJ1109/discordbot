import json

help_msg = """
        \'!js-<server name>-up\' - Request the server to come online
        \'!js-<server name>-down\' - Request the server to shutdown
        \'!js-<server name>-status\' - Request the status of a specific server
        \'!js-<server name>-info\' - Prints out host name and port # to connect to the specified server

        VALID SERVER NAMES
        \'all\' - All hosted servers (can only be used with \'!js-all-status\')
    """

with open('server_conf.json', 'r') as fp:
    obj = json.load(fp)

help_msg = """
    Basic usage: `!js-\{server\}-\{command\}`
    

    **VALID SERVER NAMES**
        `all` - All hosted servers (can only be used with `!js-all-status`)
    """

for k in obj.keys():
    help_msg += "\t\'" + k + '\'\t - ' + obj[k]['description'] + '\n'

help_msg += """
**COMMANDS**
    `up` - Request the server to come online
    `down` - Request the server to shutdown
    `status` - Request the status of a specific server
    `info` - Prints out connection info"""
help_msg += '\nEx. To request the minecraft server come online:\n> !js-minecraft-up'
print(help_msg) 