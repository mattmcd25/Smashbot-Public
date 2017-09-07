import os
import time
import CommandHandler
import Competitors
import sys
from slackclient import SlackClient

# starterbot's ID as an environment variable
BOT_ID = "U3GJQL5KQ"

# constants
AT_BOT = "<@" + BOT_ID + ">"

# instantiate Slack & Twilio clients
apikey = open("api-key.txt", 'r+').read()
slack_client = SlackClient(apikey)


def handle_command(command, channel, user):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    new_command = command
    if command[0] == ":":
        new_command = command[1:]

    response, ochannel = CommandHandler.execute_command(new_command, channel, user)
    slack_client.api_call("chat.postMessage", channel=ochannel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    # print(slack_rtm_output)
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                    return output['text'].split(AT_BOT)[1].strip().lower(), \
                           output['channel'], \
                           output['user']
    return None, None, None


def main():
    global slack_client
    

    READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose
    Competitors.load_competitors()
    if slack_client.rtm_connect():
        print("Smashbot connected and running!")
        CommandHandler.init()

        if sys.argv[-1] == "tfile":
            tfile = open("entry.txt", 'r+')
            stuff = tfile.read().split("\n")
            channel = stuff[4]
            user = "U2636HDUG"  # jackson lol
            print(stuff)
            CommandHandler.player1 = stuff[0]
            CommandHandler.player2 = stuff[1]
            CommandHandler.score1 = int(stuff[2])
            CommandHandler.score2 = int(stuff[3])
            CommandHandler.pending = True
            command = "match-confirm no-print"
            tfile.truncate()
            tfile.close()
            print("about to run")
            handle_command(command, channel, user)
        elif sys.argv[-1] == "addfile":
            tfile = open("entry.txt", 'r+')
            stuff = tfile.read().split("\n")
            channel = stuff[2]
            user = "U2636HDUG"  # also jackson.
            print(stuff)
            command = "add-competitor " + stuff[0] + " " + stuff[1] + " no-print"
            tfile.truncate()
            tfile.close()
            handle_command(command, channel, user)
        elif sys.argv[-1] == "cancelfile":
            tfile = open("entry.txt", 'r+')
            stuff = tfile.read().split("\n")
            channel = stuff[0]
            user = "U2636HDUG"
            command = "match-cancel no-print"
            print(stuff)
            tfile.truncate()
            tfile.close()
            handle_command(command, channel, user)

        while True:
            command, channel, user = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel, user)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")


if __name__ == "__main__":
    main()
