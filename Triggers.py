import Competitors
import datetime


class Trigger(object):
    def check_match(self, command):
        return False

    def print_trigger(self):
        return "No message"


class GuthTrigger(Trigger):
    def check_match(self, command):
        return ("second" in command or "2nd" in command) and "best" in command and "house" in command

    def print_trigger(self):
        return "I'm not sure, but it's definitely not Kevin Guth."


class HillTrigger(Trigger):
    def check_match(self, command):
        return "why" in command and "controllers" in command and ("broke" in command or "break" in command)

    def print_trigger(self):
        return "Probably because Matt Hill keeps throwing them across the room."


class WorstTrigger(Trigger):
    def check_match(self, command):
        return ("worst" in command or "last" in command) and "house" in command

    def print_trigger(self):
        worst = Competitors.all_competitors()[0]
        for comp in Competitors.all_competitors():
            if comp.rank > worst.rank:
                worst = comp

        return worst.name + " is currently the worst player in the house, with an ELO of " + str(worst.elo) + "."


class BestTrigger(Trigger):
    def check_match(self, command):
        return ("best" in command or "first" in command) and "house" in command

    def print_trigger(self):
        best = Competitors.all_competitors()[0]
        for comp in Competitors.all_competitors():
            if comp.rank < best.rank:
                best = comp

        return best.name + " is currently the best player in the house, with an ELO of " + str(best.elo) + "."


class WallyTrigger(Trigger):
    def check_match(self, command):
        return "wally" in command and "2-0" in command and ("beanbag" in command or "jeremy" in command)

    def print_trigger(self):
        return "It was a fluke!"


class WaveTrigger(Trigger):
    def check_match(self, command):
        return "wave:" in command

    def print_trigger(self):
        return "Hey! :daddy:"


class AliveTrigger(Trigger):
    def check_match(self, command):
        return ("are you" in command or "ru" in command) and ("alive" in command or "awake" in command)

    def print_trigger(self):
        return "Yes :daddy:"
		
		
class MorningTrigger(Trigger):
    def check_match(self, command):
        return "how" in command and "feeling" in command and "morning" in command

    def print_trigger(self):
        return "It's great to be alive in the morning! :sunny:"


class DedicatedTrigger(Trigger):
    def check_match(self, command):
        return "are" in command and "dedicated" in command and "you" in command

    def print_trigger(self):
        return "Dedicated, dedicated, hell yeah dedicated!"


class MotivatedTrigger(Trigger):
    def check_match(self, command):
        return "are" in command and "motivated" in command and "you" in command

    def print_trigger(self):
        return "Motivated, motivated, hell yeah motivated!"


class ConstipatedTrigger(Trigger):
    def check_match(self, command):
        return "are" in command and "constipated" in command and "you" in command

    def print_trigger(self):
        return "Hell no!"


class WeekTrigger(Trigger):
    def check_match(self, command):
        return "what" in command and "week" in command and "is" in command

    def print_trigger(self):
        today = datetime.date.today()
        if today.year != 2017 or today.month != 2 or today.day < 20 or today.day > 25:
            return "Not pride week, that's for sure."
        else:
            down = today.day-20;
            days = " day " if down==1 else " days "
            return "Pride Week! Pride Week! We love Pride Week!\n" + str(down) + days + "down and 6 to go!\nYo ho, yo ho, yo ho!"
