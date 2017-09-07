import gspread
import json
import operator
import time
import smashbot
import CommandHandler
import sys
from xml.etree.ElementTree import ParseError
from oauth2client.client import SignedJwtAssertionCredentials

json_key = json.load(open('creds.json'))  # json credentials you downloaded earlier
scope = ['https://spreadsheets.google.com/feeds']

# get email and key from creds
credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'].encode(), scope)

file = gspread.authorize(credentials)  # authenticate with Google
sheet = file.open("Smash Ladder").sheet1  # open sheet
history = file.open("Smash Ladder").worksheet("Match History")

ELO_CONSTANT = 100

CHALLENGE_RANGE = 8

complist = []


def all_competitors():
    global complist
    if len(complist) == 0:
        load_competitors()

    return complist


def refresh_rankings():
    global complist
    complist.sort(key=operator.attrgetter('elo'), reverse=True)
    i = 1
    for comp in complist:
        comp.rank = i
        i += 1
        print(str(comp.rank) + " " + comp.name + " " + str(comp.elo))


def load_competitors():
    global complist
    retlist = []
    i = 2
    name = sheet.cell(i, 3).value
    elo = sheet.cell(i, 4).value
    while name != "":
        retlist.append(Competitor(name, i-1, int(elo)))
        i += 1
        name = sheet.cell(i, 3).value
        elo = sheet.cell(i, 4).value

    complist = retlist
    print("Competitors loaded from Google Sheets.")
    return retlist


def save_competitors(channel, mode="normal", comp=None):
    global complist
    try:
        global sheet
        gfile = gspread.authorize(credentials)
        sheet = gfile.open("Smash Ladder").sheet1  # open sheet

        for comp in complist:
            sheet.update_cell(comp.rank+1, 2, comp.rank)
            sheet.update_cell(comp.rank+1, 3, comp.name)
            sheet.update_cell(comp.rank+1, 4, comp.elo)
        print("Competitors saved to Google Sheets.")
    except:
        smashbot.slack_client.api_call("chat.postMessage",
                                       channel='G3GKCT0DV', text="Failed to save. Retrying...", as_user=True)
        tfile = open("entry.txt", 'r+')
        tfile.truncate()
        if mode == "normal":
            tfile.write(CommandHandler.player1 + "\n" + CommandHandler.player2 + "\n" +
                        str(CommandHandler.score1) + "\n" + str(CommandHandler.score2) + "\n" +
                        channel)
            tfile.close()
            sys.exit(69)
        elif mode == "add":
            tfile.write(comp.name + "\n" + str(comp.elo) + "\n" + channel)
            tfile.close()
            sys.exit(70)
        elif mode == "cancel":
            tfile.write(channel)
            tfile.close()
            sys.exit(71)


def record_match(player1, player2, p1score, p2score, old_p1elo, old_p2elo, attempt=1):
    try:
        global history
        gfile = gspread.authorize(credentials)
        history = gfile.open("Smash Ladder").worksheet("Match History")

        hist = [x for x in history.col_values(1) if x != ""]
        history.update_cell(len(hist)+1, 1, time.strftime("%d/%m/%Y") + "@" + time.strftime("%H:%M:%S"))
        history.update_cell(len(hist)+1, 2, player1.name)
        history.update_cell(len(hist)+1, 3, old_p1elo)
        history.update_cell(len(hist)+1, 4, player2.name)
        history.update_cell(len(hist)+1, 5, old_p2elo)
        history.update_cell(len(hist)+1, 6, p1score)
        history.update_cell(len(hist)+1, 7, p2score)
        history.update_cell(len(hist)+1, 8, player1.elo)
        history.update_cell(len(hist)+1, 9, player2.elo)
    except:
        if attempt==1:
            record_match(player1, player2, p1score, p2score, old_p1elo, old_p2elo, attempt=2)
            print("Retrying match history...")
        else:
            smashbot.slack_client.api_call("chat.postMessage",
            channel='G3GKCT0DV', text="Match was saved, but not recorded in history. @mattmcd25", as_user=True)


class Competitor(object):
    def __init__(self, name, rank, elo):
        self.name = name
        self.rank = rank
        self.elo = elo
