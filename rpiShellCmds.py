import subprocess
import threading
import time
#############################################################################

def killSrvr():
    # Run in a seperate RPi terminal.  Kills the server process and
    # all of the threads it may have started.  Slightly hackish.
    # Not needed/called now that the "ks" command is working.

    # Get all processes.
    result = subprocess.run(['ps','aux'],
             stdout=subprocess.PIPE,text=True, check = False)
    rspStr = result.stdout.strip()
    lines = rspStr.splitlines()

    # Get all processes that are running the python server.
    pythonServerLines = []
    for line in lines:
        if 'server' in line:
            pythonServerLines.append(line)

    # Get all pids of processes that are running the python server.
    pythonServerPids = []
    for line in pythonServerLines:
        splitLine  = line.split()
        processNum = splitLine[1]
        pythonServerPids.append(processNum)

    # Kill all pids of python servers.
    for pid in pythonServerPids:
        result = subprocess.run( [ 'kill','-9', pid ],
                                  stdout = subprocess.PIPE,
                                  text   = True,
                                  check  = False
                               )
############################################################################

def reboot_worker(delay_seconds=3):
    time.sleep(delay_seconds)
    subprocess.Popen(["sudo", "reboot"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.Popen(["nohup", "sudo", "reboot"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def rebootRpi():
    # Launch reboot logic in background and return immediately
    #threading.Thread(target=reboot_worker, daemon=True).start()
    return ['Rebooting in 3 seconds... (RE: rbt)']
############################################################################

if __name__ == '__main__':
    killSrvr()
