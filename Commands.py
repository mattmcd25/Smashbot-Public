import CommandHandler
import Competitors
import math
import sys
import smashbot
from Competitors import Competitor
from Users import User

MATCHES_TO_WIN = 3
PERM_ANYONE = 0
PERM_APPROVED = 1
PERM_ADMIN = 5
POSSIBLE_SCORE = [1, 0.75, 0.6, 0.4, 0.25, 0]
ENGLISH_SCORE = ["3-0", "3-1", "3-2", "2-3", "1-3", "0-3"]

class Command(object):
    def __init__(self, name, permissions):
        self.name = name
        self.permissions = permissions

    def execute(self, args, channel, user):
        return "Undefined command body for " + self.name, channel

    def usage(self):
        return "Undefined usage body for " + self.name


class LadderCommand(Command):
    def __init__(self):
        Command.__init__(self, "ladder", PERM_ANYONE)

    def execute(self, args, channel, user):
        result = "Ladder Standings\n"
        for comp in Competitors.all_competitors():
            result += (str(comp.rank) + ") " + comp.name + " - ELO " + str(comp.elo) + "\n")
        return result, channel

    def usage(self):
        return "ladder"


class MatchCommand(Command):
    def __init__(self):
        Command.__init__(self, "match", PERM_APPROVED)

    def execute(self, args, channel, user):
        if len(args) != 5:
            return "Invalid use of match. Proper use is " + self.usage(), channel

        CommandHandler.player1 = args[1]
        CommandHandler.score1 = int(args[2])
        CommandHandler.player2 = args[3]
        CommandHandler.score2 = int(args[4])

        result = CommandHandler.player1
        if CommandHandler.score1 == CommandHandler.score2:
            return "Invalid use of match. There are no ties.", channel
        elif CommandHandler.score1 != MATCHES_TO_WIN and CommandHandler.score2 != MATCHES_TO_WIN:
            return "Invalid use of match. At least one player must have " + str(MATCHES_TO_WIN) + " wins.", channel
        elif CommandHandler.score1 + CommandHandler.score2 >= MATCHES_TO_WIN * 2:
            return "Invalid use of match. There can be at most " + str(MATCHES_TO_WIN * 2 - 1) + " matches played.", channel
        elif CommandHandler.player1 == CommandHandler.player2:
            return "Invalid use of match. The players can't be the same.", channel
        elif CommandHandler.score1 > CommandHandler.score2:
            result += " beat "
        else:
            result += " lost to "

        p1 = None
        p2 = None
        for comp in Competitors.all_competitors():
            if comp.name.lower() == CommandHandler.player1:
                p1 = comp
            elif comp.name.lower() == CommandHandler.player2:
                p2 = comp

        if p1 is None:
            return "Unknown player " + CommandHandler.player1 + ". Please use add-competitor to add a new player.", channel
        if p2 is None:
            return "Unknown player " + CommandHandler.player2 + ". Please use add-competitor to add a new player.", channel

        if p1.rank < p2.rank-Competitors.CHALLENGE_RANGE or p1.rank > p2.rank+Competitors.CHALLENGE_RANGE:
            return p1.name + " and " + p2.name + " are too far apart in the standings to compete. (ranks " + \
                   str(p1.rank) + " and " + str(p2.rank) + ")", channel


        result += (CommandHandler.player2 + " " + str(CommandHandler.score1) + "-" + str(CommandHandler.score2) + ".\n")
        result += "Is this correct?\nRespond with @smashbot match-confirm or @smashbot match-cancel"
        CommandHandler.pending = True

        smashbot.handle_command("match-confirm", channel, user)

        return "", ''

    def usage(self):
        return "match [player1] [score1] [player2] [score2]"


class MatchConfirmCommand(Command):
    def __init__(self):
        Command.__init__(self, "match-confirm", PERM_APPROVED)

    def execute(self, args, channel, user):
        if not CommandHandler.pending:
            return "There is no pending match.", channel

        player1 = None
        player2 = None
        sprint = True

        if len(args) > 1:
            if args[1] == "no-print":
                print("rerunning from file")
                sprint = False

        for comp in Competitors.all_competitors():
            if comp.name.lower() == CommandHandler.player1:
                player1 = comp
            elif comp.name.lower() == CommandHandler.player2:
                player2 = comp

        if player1 is None:
            return "Unknown player " + CommandHandler.player1 + ". Please use add-competitor to add a new player.", channel
        if player2 is None:
            return "Unknown player " + CommandHandler.player2 + ". Please use add-competitor to add a new player.", channel

        print("player1: " + player1.name + ", " + str(player1.elo) + ", " + str(player1.rank))
        print("player2: " + player2.name + ", " + str(player2.elo) + ", " + str(player2.rank))

        expected_p1score = 1 / (1 + math.pow(10, (player2.elo - player1.elo) / 400))
        expected_p2score = 1 / (1 + math.pow(10, (player1.elo - player2.elo) / 400))

        print("expected p1 " + str(expected_p1score) + " expected p2 " + str(expected_p2score))

        p1score = CommandHandler.score1 / (CommandHandler.score1 + CommandHandler.score2)
        p2score = CommandHandler.score2 / (CommandHandler.score1 + CommandHandler.score2)

        print("p1score " + str(p1score) + " p2score " + str(p2score))

        new_p1elo = round(player1.elo + Competitors.ELO_CONSTANT * (p1score - expected_p1score))
        new_p2elo = round(player2.elo + Competitors.ELO_CONSTANT * (p2score - expected_p2score))

        print("new p1 " + str(new_p1elo) + " new p2 " + str(new_p2elo))

        p1delta = new_p1elo - player1.elo
        p2delta = new_p2elo - player2.elo

        old_p1elo = player1.elo
        old_p2elo = player2.elo

        player1.elo = new_p1elo
        player2.elo = new_p2elo

        Competitors.refresh_rankings()

        result = "New rankings as a result of " + player1.name + " " + str(CommandHandler.score1) + "-" + \
                 player2.name + " " + str(CommandHandler.score2) + ":\n"
        result += player1.name + " is now rank " + str(player1.rank) + " with an ELO of " + str(player1.elo)
        if p1delta > 0:
            result += " (+" + str(p1delta) + ")\n"
        else:
            result += " (" + str(p1delta) + ")\n"
        result += player2.name + " is now rank " + str(player2.rank) + " with an ELO of " + str(player2.elo)
        if p2delta > 0:
            result += " (+" + str(p2delta) + ")\n"
        else:
            result += " (" + str(p2delta) + ")\n"

        smashbot.slack_client.api_call("chat.postMessage", channel='G3GKCT0DV',
                                            text="Saving to Google Sheets...", as_user=True)

        if sprint:
            smashbot.slack_client.api_call("chat.postMessage", channel=channel, text=result, as_user=True)
        Competitors.save_competitors(channel)

        Competitors.record_match(player1, player2, p1score, p2score, old_p1elo, old_p2elo)

        CommandHandler.player1 = ""
        CommandHandler.player2 = ""
        CommandHandler.score1 = 0
        CommandHandler.score2 = 0
        CommandHandler.pending = False
        return "Saved match between " + player1.name + " and " + player2.name + ".", 'G3GKCT0DV'

    def usage(self):
        return "match-confirm"


class ProjectCommand(Command):
    def __init__(self):
        Command.__init__(self, "project", PERM_ANYONE)

    def execute(self, args, channel, user):
        if len(args) < 3:
            return "Invalid use of project. Proper use is " + self.usage(), channel

        player1 = None
        player2 = None

        for comp in Competitors.all_competitors():
            if comp.name.lower() == args[1]:
                player1 = comp
            elif comp.name.lower() == args[2]:
                player2 = comp

        if player1 is None:
            return "Unknown player " + CommandHandler.player1 + ". Please use add-competitor to add a new player.", channel
        if player2 is None:
            return "Unknown player " + CommandHandler.player2 + ". Please use add-competitor to add a new player.", channel

        expected_p1score = 1 / (1 + math.pow(10, (player2.elo - player1.elo) / 400))
        expected_p2score = 1 / (1 + math.pow(10, (player1.elo - player2.elo) / 400))

        result = "Projected results of " + player1.name + " challenging " + player2.name + ":\n"

        result += "Current Ratings: " + player1.name + " is rank " + str(player1.rank) + " with ELO " + str(player1.elo) + ", " + player2.name + " is rank " + str(player2.rank) + " with ELO " + str(player2.elo) + "\n"

        if expected_p1score > 0.5:
            result += player1.name + " is favored to win with a " + str(round(expected_p1score*100,2)) + " winrate.\n"
        elif 0.5 > expected_p1score:
            result += player1.name + " is favored to lose with a " + str(round(expected_p1score*100,2)) + " winrate.\n"
        else:
            result += player1.name + " and " + player2.name + " are exactly even.\n"

        # 3-0, 3-1, 3-2, 2-3, 1-3, 0-3

        for i in range(6):
            p1score = POSSIBLE_SCORE[i]
            p2score = 1-p1score
            new_p1elo = round(player1.elo + Competitors.ELO_CONSTANT * (p1score - expected_p1score))
            new_p2elo = round(player2.elo + Competitors.ELO_CONSTANT * (p2score - expected_p2score))
            p1delta = new_p1elo - player1.elo
            result += "If the score is " + ENGLISH_SCORE[i] + ": " + str(new_p1elo) + " (" + \
                      ("+" if p1delta > 0 else "") + str(p1delta) + ") VS " + str(new_p2elo) + "\n"

        return result, channel

    def usage(self):
        return "project [player1] [player2]"


class MatchCancelCommand(Command):
    def __init__(self):
        Command.__init__(self, "match-cancel", PERM_APPROVED)

    def execute(self, args, channel, user):
        sprint = True

        if len(args) > 1:
            if args[1] == "no-print":
                sprint = False

        hist = [x for x in Competitors.history.col_values(1) if x != ""]
        last_match = Competitors.history.row_values(len(hist))
        print(last_match)
        name1 = last_match[1]
        elo1 = last_match[2]
        name2 = last_match[3]
        elo2 = last_match[4]

        player1 = None
        player2 = None

        for comp in Competitors.all_competitors():
            if comp.name.lower() == name1.lower():
                player1 = comp
            elif comp.name.lower() == name2.lower():
                player2 = comp

        player1.elo = int(elo1)
        player2.elo = int(elo2)

        Competitors.refresh_rankings()

        result = "Successfully reverted match between " + name1 + " and " + name2 + ".\n"
        result += name1 + " is now back to ELO " + elo1 + ", and " + name2 + " is back to ELO " + elo2 + "."

        smashbot.slack_client.api_call("chat.postMessage", channel='G3GKCT0DV',
                                       text="Saving to Google Sheets...", as_user=True)

        if sprint:
            smashbot.slack_client.api_call("chat.postMessage", channel=channel, text=result, as_user=True)

        Competitors.save_competitors(channel, mode="cancel")

        # print("hey")

        # delete history
        for x in list(range(9)):
            # print(str(x+1))
            Competitors.history.update_cell(len(hist), x+1, "")

        return "Saved cancel between " + name1 + " and " + name2 + ".", 'G3GKCT0DV'

    def usage(self):
        return "match-cancel"


class AddCompetitorCommand(Command):
    def __init__(self):
        Command.__init__(self, "add-competitor", PERM_APPROVED)

    def execute(self, args, channel, user):
        if len(args) != 3:
            return "Invalid use of add-competitor. Proper use is " + self.usage(), channel

        sprint = True
        if len(args) > 3:
            if args[3] == "no-print":
                sprint = False

        elo = int(args[2])

        if elo < 1000:
            elo = 1000

        for comp in Competitors.all_competitors():
            if comp.name.lower() == args[1]:
                return "A competitor named " + args[1] + " already exists.", channel

        name = args[1]
        if len(name) <= 2 or not ("a" in name or "e" in name or "i" in name or "o" in name or "u" in name):
            name = name.upper()
        else:
            name = name[0].upper()+name[1:]

        new_comp = Competitor(name, 0, elo)

        Competitors.complist.append(new_comp)
        Competitors.refresh_rankings()

        result = "Competitor " + args[1] + " added with an ELO of " + str(elo) + ". Starting rank: " + \
                 str(new_comp.rank) + ".\n"
        smashbot.slack_client.api_call("chat.postMessage", channel='G3GKCT0DV', text="Saving to Google Sheets...",
                                       as_user=True)
        if sprint:
            smashbot.slack_client.api_call("chat.postMessage", channel=channel,
                                       text=result, as_user=True)
        Competitors.save_competitors(channel, mode="add", comp=new_comp)
        return "Saved new competitor " + args[1] + ".", 'G3GKCT0DV'

    def usage(self):
        return "add-competitor [name] [initial-elo]"


class AdminCommand(Command):
    def __init__(self):
        Command.__init__(self, "admin", PERM_ADMIN)

    def execute(self, args, channel, user):
        if len(args) < 2:
            return "Please enter an admin command.", channel

        if args[1] == "help":
            return "uid_on, uid_off, change_constant, authorize, users, add_channel, save_sheet, load_sheet, reboot", channel

        if args[1] == "uid_on":
            CommandHandler.print_uids = True
            return "UID Printing enabled.", channel

        if args[1] == "uid_off":
            CommandHandler.print_uids = False
            return "UID Printing disabled.", channel

        if args[1] == "change_constant":
            Competitors.ELO_CONSTANT = int(args[2])
            return "ELO Constant changed to " + args[2] + ".", channel

        if args[1] == "authorize":
            CommandHandler.USERS.append(User(args[2], args[3], int(args[4])))
            ufile = open("users.txt", 'r+')
            ufile.read()
            ufile.write("\n" + args[2] + " " + args[3].upper() + " " + args[4])
            ufile.close()
            return "User " + args[2] + " approved.", channel

        if args[1] == "users":
            result = "Users: \n"
            for u in CommandHandler.USERS:
                result += u.name + ", UID " + u.uid + ", Permission " + str(u.perm) + "\n"
            return result, channel

        if args[1] == "add_channel":
            CommandHandler.APPROVED_CHANNELS.append(channel)
            print("***ADD CHANNEL " + channel + " TO smashbot.py TO PRESERVE ABILITY***")
            return "Channel " + channel + " approved temporarily.", channel

        if args[1] == "save_sheet":
            smashbot.slack_client.api_call("chat.postMessage", channel=channel,
                                           text="Saving to Google Sheets...", as_user=True)
            Competitors.save_competitors(channel)
            return "Saved.", channel

        if args[1] == "load_sheet":
            smashbot.slack_client.api_call("chat.postMessage", channel=channel,
                                           text="Loading from Google Sheets...", as_user=True)
            Competitors.load_competitors()
            return "Loaded.", channel

        if args[1] == "reboot":
            sys.exit(0)

        return "Unknown admin command " + args[1] + ".", channel

    def usage(self):
        return "admin [command] [args...]"
