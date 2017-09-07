import subprocess
import time

def main():
    return_status = subprocess.call("smashbot.py")
    while True:
        print("RE-RUNNING SCRIPT!")
        print(time.strftime("%d/%m/%Y") + "@" + time.strftime("%H:%M:%S"))
        if return_status == 69:
            return_status = subprocess.call("smashbot.py tfile")
        elif return_status == 70:
            return_status = subprocess.call("smashbot.py addfile")
        elif return_status == 71:
            return_status = subprocess.call("smashbot.py cancelfile")
        else:
            return_status = subprocess.call("smashbot.py")
        print("Return code: " + str(return_status))
    print("DONE")




if __name__ == '__main__':
    main()

