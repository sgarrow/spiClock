'''
When a client enters a command those commands are received by function
handleClient in file server.py.  The command (string) is forwarded to
function "vector" (in this file) and the appropriate "worker" function
is then vectored to in file cmdWorkers.py.
'''

import multiprocessing as mp
import clockRoutines as cr
import spiRoutines   as sr
import testRoutines  as tr
import cmds
#############################################################################

lcdCq = mp.Queue() # LCD Cmd Q. mp queue must be used here.
lcdRq = mp.Queue() # LCD Rsp Q. mp queue must be used here.
clkCq = mp.Queue() # CLK Cmd Q. mp queue must be used here.
clkRq = mp.Queue() # CLK Rsp Q. mp queue must be used here.
qs    = [ lcdCq, lcdRq, clkCq, clkRq ]
#############################################################################

def killSrvr():    # The ks handled directly in the handleClient func so it
    return         # doesn't need a wrk funct, but because of way vectoring
                   # is done a func needs to exist. Func never called/runs.
#############################################################################

def getVer():
    VER = ' v0.2.3 - 15-Mar-2025'
    return [VER]
#############################################################################

def vector(inputStr): # called from handleClient. inputStr from client.

    # This dictionary embodies the worker function vector (and menu) info.
    vectorDict = {
    'lc'  :{'func':cmds.cmds,      'parm':None,   'menu': 'List Commands'},
    'hr'  :{'func':sr.hwReset,     'parm':None,   'menu': 'HW Reset'     },
    'sr'  :{'func':sr.swReset,     'parm':None,   'menu': 'SW Reset'     },
    'sb'  :{'func':sr.setBackLight,'parm':[0],    'menu': 'Set Backlight'},
    'rt'  :{'func':tr.runTest,     'parm':None,   'menu': 'Run Test'     },
    'sc'  :{'func':cr.startClk,    'parm':[[],qs],'menu': 'Start Clock'  },
    'pc'  :{'func':cr.stopClk,     'parm':qs,     'menu': 'stoP Clock'  },
    'ks'  :{'func':killSrvr,       'parm':None,   'menu': 'Kill Server'  }
    }

    # Process the string (command) passed to this function via the call
    # from function handleClient in file server.py.
    inputWords = inputStr.split()

    if inputWords == []:       # In case user entered just spaces.
        rspStr = 'Invalid command'
        return rspStr          # Return to srvr for forwarding to clnt.

    choice     = inputWords[0]
    optArgsStr = inputWords[1:]

    if choice in vectorDict:
        func   = vectorDict[choice]['func']
        params = vectorDict[choice]['parm']

        if choice in ['sc']:
            if len(optArgsStr) == 3:
                params[0] = optArgsStr

        if choice in ['cc', 'sbl']:
            if len(optArgsStr) == 1:
                params = optArgsStr

        #try:
        if params is None:
            rsp = func()       # rsp[0] = rspStr. Vector to worker.
            return rsp[0]      # return to srvr for forwarding to clnt.

        rsp = func(params)     # rsp[0] = rspStr. Vector to worker.
        return rsp[0]          # Return to srvr for forwarding to clnt.
        #except Exception #as e:
        #    return str(e)

    if choice == 'm':
        rspStr = ''
        for k,v in vectorDict.items():
            rspStr += ' {:2} - {}\n'.format(k, v['menu'] )
        return rspStr          # Return to srvr for forwarding to clnt.

    rspStr = 'Invalid command'
    return rspStr              # Return to srvr for forwarding to clnt.
