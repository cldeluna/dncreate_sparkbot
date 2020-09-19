#!/usr/bin/python -tt
# Project: Dropbox (Indigo Wire Networks)
# Filename: flaskapp
# claudia
# PyCharm

__author__ = "Claudia de Luna (claudia@indigowire.net)"
__version__ = ": 1.0 $"
__date__ = "2019-06-16"
__copyright__ = "Copyright (c) 2018 Claudia"
__license__ = "Python"

import os
import sys
import logging

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

import dotenv
import json
import re
import requests
import subprocess
import bot_functions

from webexteamsbot import TeamsBot
from webexteamsbot.models import Response



# Create a custom bot greeting function returned when no command is given.
# The default behavior of the bot is to return the '/help' command response
def greeting(incoming_msg):
    # Loopkup details about sender
    sender = app.teams.people.get(incoming_msg.personId)
    room = app.teams.rooms.get(incoming_msg.roomId)
    # site_id, match = get_siteid(room)

    # Create a Response object and craft a reply in Markdown.
    response = Response()
    response.markdown = f"\nHello {sender.displayName} in room {room.title}! \nI'm your SparkBot and I'm here to help!\n "

    response.markdown += f"\nSee what I can do by asking for **/help**.\n"
    #response.markdown += f"\n===Start Data Structure Output\nincoming_msg:\n{incoming_msg} \nsender object:\n {sender}\nroom object:\n {room}\n===END Data Structure Output"
    return response


def debug_data(incoming_msg):
    # Loopkup details about sender
    sender = app.teams.people.get(incoming_msg.personId)
    room = app.teams.rooms.get(incoming_msg.roomId)

    regexp = r"test"
    room_title = room.title
    match = re.search(regexp, room_title, re.IGNORECASE)
    if match:
        is_test = "This is a TEST Space!"
    else:
        is_test = match.group()

    # Create a Response object and craft a reply in Markdown.
    response = Response()
    response.markdown = f"Hello {sender.displayName} in room {room.title}.\n "
    if match:
        response.markdown += f"\nThe Teams Space {is_test} is a Test space!\n"
    else:
        response.markdown += f"\nThis is Teams Space {is_test}\n"
    response.markdown += f"\nLets look at some DEBUG Info...\n"
    response.markdown += f"\n===Start Data Structure Output\nincoming_msg:\n{incoming_msg} \nsender object:\n {sender}\nroom object:\n {room}\n===END Data Structure Output"
    return response


def aci_health(incoming_msg):
    """
    Sample function to check overall health of DevNet Always On Sandbox APIC via REST call.
    :param incoming_msg: The incoming message object from Teams
    :return: A text or markdown based reply
    """

    # Split incoming message into a list of its component so we can strip off Bot Name, command, and get to the
    # parameters.  In this case any additional parameter will be interpreted as debug.

    message = incoming_msg.text.split()


    url = "https://sandboxapicdc.cisco.com/api/aaaLogin.json"
    # payload = "{\"aaaUser\": {\"attributes\": {\"name\": \"admin\", \"pwd\": \"ciscopsdt\"}}}"

    # payload = {
    #    "aaaUser":{
    #       "attributes":{
    #          "name": os.getenv('APIC_USER'),
    #          "pwd": os.getenv('APIC_PWD')
    #       }
    #    }
    # }

    p1 = r'{"aaaUser": {"attributes": {"name": "'
    p2 = os.getenv('APIC_USER')
    p3 = r'", "pwd": "'
    p4 = os.getenv('APIC_PWD')
    p5 = r'"}}}'

    payload = p1 + p2 + p3 + p4 + p5

    c = bot_functions.rest_api_call(url, payload=payload, type="POST")
    cjson = c.json()

    status_code = c.status_code
    token = cjson['imdata'][0]['aaaLogin']['attributes']['token']

    url = "https://sandboxapicdc.cisco.com/api/node/mo/topology/HDfabricOverallHealth5min-0.json"
    payload = {}
    cookie = f"APIC-cookie={token}"
    health_obj = bot_functions.rest_api_call(url, payload=payload, cookie=cookie)

    # Create a Response object and craft a reply in Markdown.
    response = Response()
    health_obj_json = health_obj.json()
    response.markdown = f"DevNet ACI Sandbox Fabric Health is: " \
                        f"\n\tDN:\t{health_obj_json['imdata'][0]['fabricOverallHealthHist5min']['attributes']['dn']}" \
                        f"\n\tMax:\t{health_obj_json['imdata'][0]['fabricOverallHealthHist5min']['attributes']['healthMax']}" \
                        f"\n\tMin:\t{health_obj_json['imdata'][0]['fabricOverallHealthHist5min']['attributes']['healthMin']}" \
                        f"\n\tAvg:\t{health_obj_json['imdata'][0]['fabricOverallHealthHist5min']['attributes']['healthAvg']}"

    if len(message) > 2:
        response.markdown += f"\nDebug: \n```{json.dumps(health_obj.json(), indent=4, sort_keys=True)}```\n"

    return response


# An example using a Response object.  Response objects allow more complex
# replies including sending files, html, markdown, or text. Rsponse objects
# can also set a roomId to send response to a different room from where
# incoming message was recieved.
def ret_message(incoming_msg):
    """
    Sample function that uses a Response object for more options.
    :param incoming_msg: The incoming message object from Teams
    :return: A Response object based reply
    """
    # Create a object to create a reply.
    response = Response()

    # Set the text of the reply.
    response.text = "Here's a fun little meme."

    # Craft a URL for a file to attach to message
    u = "https://sayingimages.com/wp-content/uploads/"
    u = u + "aaaaaalll-righty-then-alrighty-meme.jpg"
    response.files = u
    return response


# An example command the illustrates using details from incoming message within
# the command processing.
def current_time(incoming_msg):
    """
    Sample function that returns the current time for a provided timezone
    :param incoming_msg: The incoming message object from Teams
    :return: A Response object based reply
    """

    reply = bot_functions.get_time(incoming_msg)

    response = Response()
    response.markdown = f"\n{reply}\n"

    return response


def need_comic(incoming_msg):
    """
    Sample function that uses a Response object for more options.
    :param incoming_msg: The incoming message object from Teams
    :return: A Response object based reply
    """
    # Create a object to create a reply.
    response = Response()

    # Set the text of the reply.
    response.text = "Clearly its time for some comic relief"

    get_url = 'http://xkcd.com/info.0.json'

    get_response = requests.get(get_url)

    if get_response.status_code != 200:
        response.text = response.text + "\nEven the Comic Relief is tired!"
        raise Exception("Status code: " + str(get_response.status_code) + " for url: " + get_url)

    else:

        #response.files ="https://imgs.xkcd.com/comics/stack.png" 
        data = get_response.json()
        u = str(data["img"])
        response.files = u

    return response


def l3_sum(incoming_msg):
    """
    Main function called by the Bot Menu to generate L3 Subnet Summary report.
    This function calls the bot_functions.conn_matrix function for the actual processing

    :param incoming_msg:
    :return:
    """

    # Get sent message
    msg = ''
    message = incoming_msg.text.split()

    # Lookup details about sender
    sender = app.teams.people.get(incoming_msg.personId)
    room = app.teams.rooms.get(incoming_msg.roomId)

    # if length of split message is greater than 2 elements then the function is being passed a site id parameter
    if len(message) > 2:
        siteid = message[2]
        room_title = siteid
    # Otherwise extract site id from room information
    else:
        site_id, id_match = get_siteid(room)
        room_title = room.title

    regexp = r"\d{4}"
    match = re.search(regexp, room_title)

    if match:
        site_id = match.group()
        response_data = bot_functions.conn_matrix(site_id)
    else:
        site_id = f"ERROR"
        response_data = f"ERROR:  Bot function was passed something that was not understood: {incoming_msg.text}.  " \
            f"\n\rIf you are not in an NT3 space please provide the 4 digit site code."

    # response_data += f"match is {match}\nsite_id is {site_id}\n room_title is {room_title}"

    # Create a Response object and craft a reply in Markdown.
    response = Response()
    response.markdown = f"\n{response_data}\n"

    if match:
        response.files = f"./{site_id}_sdwan_report.txt"

    return response


def sdwan_report(incoming_msg):
    """
    Main function called by the Bot Menu to generate SD WAN report.
    This function calls the bot_functions.conn_matrix function for the actual processing

    :param incoming_msg:
    :return:
    """

    # Get sent message
    msg = ''
    message = incoming_msg.text.split()

    # Lookup details about sender
    sender = app.teams.people.get(incoming_msg.personId)
    room = app.teams.rooms.get(incoming_msg.roomId)

    # if length of split message is greater than 2 elements then the function is being passed a site id parameter
    if len(message) > 2:
        siteid = message[2]
        room_title = siteid
    # Otherwise extract site id from room information
    else:
        site_id, id_match = get_siteid(room)
        room_title = room.title

    regexp = r"\d{4}"
    match = re.search(regexp, room_title)

    if match:
        site_id = match.group()
        response_data = bot_functions.conn_matrix(site_id)
    else:
        site_id = f"ERROR"
        response_data = f"ERROR:  Bot function was passed something that was not understood: {incoming_msg.text}.  " \
            f"\n\rIf you are not in an NT3 space please provide the 4 digit site code."

    # response_data += f"match is {match}\nsite_id is {site_id}\n room_title is {room_title}"

    # Create a Response object and craft a reply in Markdown.
    response = Response()
    response.markdown = f"\n{response_data}\n"

    if match:
        response.files = f"./{site_id}_sdwan_report.txt"

    return response


def cfgdiff_report(incoming_msg):
    """
    Main function called by the Bot Menu to generate a Config Diff Report.
    This function calls the bot_functions.xxxxx function for the actual processing

    :param incoming_msg:
    :return:
    """

    app.logger.info('Processing config diff request')

    # Get sent message
    msg = ''
    message = incoming_msg.text.split()

    # Loopkup details about sender
    sender = app.teams.people.get(incoming_msg.personId)
    room = app.teams.rooms.get(incoming_msg.roomId)

    # if length of split message is greater than 2 elements then the function is being passed a site id parameter
    if len(message) > 3:
        siteid = message[2]
        room_title = siteid
        dev_action = message[3]

    # Otherwise extract site id from room information
    else:
        site_id, id_match = get_siteid(room)
        room_title = room.title
        dev_action = message[2]

    regexp = r"\d{4}"
    match = re.search(regexp, room_title)


    f1 = "srv01.txt"
    f2 = "srv02.txt"

    if match:
        site_id = match.group()
        response_data = bot_functions.diff_config_processing(dev_action, site_id)
    else:
        site_id = f"ERROR"
        response_data = f"ERROR:  Bot function was passed something that was not understood: {incoming_msg.text}.  " \
            f"\n\rIf you are not in an NT3 space please provide the 4 digit site code."

    # response_data += f"match is {match}\nsite_id is {site_id}\n room_title is {room_title}"

    # Create a Response object and craft a reply in Markdown.
    response = Response()
    response.markdown = f"```\n{response_data}\n```"

    if not re.search(r'ERROR',response_data):
        response.markdown += f"\n The provided HTML file at the top of this response will provide a side by side " \
            f"color coded comparison."

        if match:
            response.files.append("./diff_report.html")

    return response


# ## MAIN BODY

# Retrieve required details from environment variables
dotenv.load_dotenv()

bot_email = os.getenv('BOT_EMAIL')
teams_token = os.getenv('TEAMS_TOKEN')
bot_url = os.getenv('BOT_URL')
bot_app_name = os.getenv('BOT_APP_NAME')

# Create a Bot Object
app = TeamsBot(
    bot_app_name,
    teams_bot_token=teams_token,
    teams_bot_url=bot_url,
    teams_bot_email=bot_email,
)

# Add new commands to SparkBot.

# Set the bot greeting.
app.set_greeting(greeting)

# Create help message for current_time command
current_time_help = "Look up the current time for a given timezone. "
current_time_help += "_Example: **/time EST**_"
app.add_command("/time", current_time_help, current_time)

app.add_command("/greeting", "Bot Greeting", greeting)

app.add_command("/debug_data", "Debug Data", debug_data)

app.add_command("/need_comic", "Need some random comic relief", need_comic)

app.add_command("/aci_health", "Check Overall Health of the DevNet Always On APIC", aci_health)

app.add_command("/l3_sum", "Generate Layer 3 Subnet Summary report", l3_sum)

if __name__ == "__main__":

    logFormatStr = '[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s'
    logging.basicConfig(format = logFormatStr, filename = "./global.log", level=logging.DEBUG)
    formatter = logging.Formatter(logFormatStr,'%m-%d %H:%M:%S')
    fileHandler = logging.FileHandler("./global.log")
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setLevel(logging.DEBUG)
    streamHandler.setFormatter(formatter)
    app.logger.addHandler(fileHandler)
    app.logger.addHandler(streamHandler)
    app.logger.info("Logging is set up.")

    app.run(host='0.0.0.0')

