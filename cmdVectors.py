'''
When a client enters a command those commands are received by function
handleClient in file server.py.  The command (string) is forwarded to
function "vector" (in this file) and the appropriate "worker" function
is then vectored to in file cmdWorkers.py.
'''

import clockRoutines as cr
import spiRoutines   as sr
import testRoutines  as tr
import cmds
#############################################################################

def killSrvr(): # The ks handled directly in the handleClient func so it
    return      # doesn't need a wrk funct, but because of the way vectoring
                # is done a func needs to exist. This func never called/runs.
#############################################################################

def getVer():
    VER = ' v0.0.14 - 5-Mar-2025'
    return [VER]
#############################################################################

def vector(inputStr): # called from handleClient. inputStr from client.

    # This dictionary embodies the worker function vector (and menu) info.
    vectorDict = {
    'cmds' : { 'func': cmds.cmds,       'parm': None,     
               'menu': 'List Commands'                     },

    'hr'   : { 'func': sr.hwReset,      'parm': None,     
               'menu': 'HW Reset'                          },

    'sr'   : { 'func': sr.swReset,      'parm': None,     
               'menu': 'SW Reset'                          },

    'sbl'  : { 'func': sr.setBackLight, 'parm': [0], 
               'menu': 'Set Backlight'                     },

    'rt'   : { 'func': tr.runTest,      'parm': None,     
               'menu': 'Run Test'                          },

    'cc'   : { 'func': cr.calClk,       'parm': [11],    
               'menu': 'Cal   Clock'                       },

    'sc'   : { 'func': cr.startClk,     'parm': [3,45,0], 
               'menu': 'Start Clock'                       },

    'ks'   : { 'func': killSrvr,        'parm': None,     
               'menu': 'Kill Server'                       }
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

        if choice in ['sc', 'sw']:
            if len(optArgsStr) == 3:
                params = optArgsStr

        if choice in ['cc', 'sbl']:
            if len(optArgsStr) == 1:
                params = optArgsStr

        #try:
        if params is None:
            rsp = func()       # rsp[0] = rspStr. Vector to worker.
            return rsp[0]      # return to srvr for forwarding to clnt.

        rsp = func(params)     # rsp[0] = rspStr. Vector to worker.
        return rsp[0]          # Return to srvr for forwarding to clnt.
        #except Exception as e:
        #    return str(e)

    if choice == 'm':
        rspStr = ''
        for k,v in vectorDict.items():
            rspStr += ' {:2} - {}\n'.format(k, v['menu'] )
        return rspStr          # Return to srvr for forwarding to clnt.

    rspStr = 'Invalid command'
    return rspStr              # Return to srvr for forwarding to clnt.
