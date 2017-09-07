from Commands import LadderCommand
from Commands import MatchCommand
from Commands import MatchCancelCommand
from Commands import MatchConfirmCommand
from Commands import AddCompetitorCommand
from Commands import AdminCommand
from Commands import ProjectCommand
from Triggers import WorstTrigger
from Triggers import BestTrigger
from Triggers import GuthTrigger
from Triggers import HillTrigger
from Triggers import WallyTrigger
from Triggers import AliveTrigger
from Triggers import WaveTrigger
from Triggers import MorningTrigger
from Triggers import DedicatedTrigger
from Triggers import MotivatedTrigger
from Triggers import ConstipatedTrigger
from Triggers import WeekTrigger
from Users import User
import Commands
import smashbot

COMMANDS = []
TRIGGERS = []
USERS = []
APPROVED_CHANNELS = []

print_uids = True
UNKNOWN_USER = User("None", "x", 0)

pending = False
player1 = ""
player2 = ""
score1 = 0
score2 = 0


def init():
    COMMANDS.append(AddCompetitorCommand())
    COMMANDS.append(AdminCommand())
    COMMANDS.append(LadderCommand())
    COMMANDS.append(MatchCommand())
    COMMANDS.append(MatchCancelCommand())
    COMMANDS.append(MatchConfirmCommand())
    COMMANDS.append(ProjectCommand())

    ufile = open("users.txt", 'r+')
    utext = ufile.read().split("\n")
    for user in utext:
        u = user.split()
        USERS.append(User(u[0], u[1], int(u[2])))
    ufile.close()

    APPROVED_CHANNELS.append('G3GKCT0DV') # test_bot
    APPROVED_CHANNELS.append('G3GQU2WB0') # smash_test
    APPROVED_CHANNELS.append('C3G7ENL4V') # smash

    TRIGGERS.append(GuthTrigger())
    TRIGGERS.append(HillTrigger())
    TRIGGERS.append(WorstTrigger())
    TRIGGERS.append(BestTrigger())
    TRIGGERS.append(WallyTrigger())
    TRIGGERS.append(WaveTrigger())
    TRIGGERS.append(AliveTrigger())
    TRIGGERS.append(MorningTrigger())
    TRIGGERS.append(DedicatedTrigger())
    TRIGGERS.append(MotivatedTrigger())
    TRIGGERS.append(ConstipatedTrigger())
    TRIGGERS.append(WeekTrigger())

    print("Commands loaded:")
    for c in COMMANDS:
        print(c.name)


def execute_command(command, channel, user):
    # triggers
    for trig in TRIGGERS:
        if trig.check_match(command):
            return trig.print_trigger(), channel

    # find user
    uobj = None
    for u in USERS:
        if u.uid.lower() == user.lower():
            uobj = u
    if uobj is None:
        uobj = UNKNOWN_USER

    # find channel
    approved = True if uobj.perm==Commands.PERM_ADMIN else False
    for chan in APPROVED_CHANNELS:
        if channel == chan:
            approved = True

    # run commands
    for c in COMMANDS:
        if command.split()[0] == c.name:
            if c.permissions == 0:
                return c.execute(command.split(), channel, user)
            elif not approved:
                return "Error: This channel (" + channel + ") is not approved to use Smashbot.", channel
            elif c.permissions <= uobj.perm:
                return c.execute(command.split(), channel, user)
            elif print_uids:
                return "Error: You (UID " + user +", Permission "+ str(uobj.perm) + ") are not authorized to use the " + \
                       c.name + " command.", channel
            else:
                return "Error: You are not authorized to use the " + c.name + " command.", channel

    return invalid_command(), channel


def invalid_command():
    res = "Invalid command. Valid commands are:\n"
    for c in COMMANDS:
        res += ("@smashbot " + c.usage() + "\n")
    return res

