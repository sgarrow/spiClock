'''
When a client enters a command those commands are received by function
handleClient in file server.py.  The command (string) is forwarded to
function "vector" (in this file) and the appropriate "worker" function
is then vectored to in file cmdWorkers.py.
'''

import multiprocessing as mp
import clockRoutines   as cr
import testRoutines    as tr
import spiRoutines     as sr
import makeScreen      as ms
import cfgDict         as cd
import cmds            as cm
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
    VER = ' v0.3.3 - 9-Apr-2025'
    return [VER]
#############################################################################

def vector(inputStr): # called from handleClient. inputStr from client.

    # This dictionary embodies the worker function vector (and menu) info.
    vectorDict = {
    # Worker Function in clockRoutines.py.
    'sc'  : { 'func'    : cr.startClk,   'parm' : [[],qs],
              'mainMnu' : 'Start Clock'                    },
    'pc'  : { 'func'    : cr.stopClk,    'parm' : qs,     
              'mainMnu' : 'stoP  Clock'                    },
    'tm'  : { 'func'    : None,          'parm' : None,   
              'mainMnu' : 'Test  Menu'                     },

    # Worker Function in testRoutines.py.
    'rt1' : { 'func'    : tr.runTest1,   'parm' : None,   
              'testMnu' : 'Run Test 1'                     },
    'rt2' : { 'func'    : tr.runTest2,   'parm' : None,   
              'testMnu' : 'Run Test 2'                     },

    # Worker Function in spiRoutines.py.
    'rh'  : { 'func'    : sr.hwReset,    'parm' : None,   
              'mainMnu' : 'Reset LCD HW'                   },
    'rs'  : { 'func'    : sr.swReset,    'parm' : 'scLSD',
              'mainMnu' : 'Reset LCD SW'                   },
    'sb'  : { 'func'    : sr.setBkLight, 'parm' : [0],    
              'mainMnu' : 'Set   Backlight'                },

    # Worker Function in makeScreens.py.
    'mds' : { 'func'    : ms.mkDigScr,   'parm' : ['redOnGreen', '255','0','0', '0','0','255'],   
              'mainMnu' : 'Make  Digit  Screen'            },

    # Worker Function in cfgDict.py.
    'rcd' : { 'func'    : cd.readCfgDict,'parm' : None,   
              'mainMnu' : 'Read  Config Dict'              },

    # Worker Function in cmds.py.
    'lc'  : { 'func'    : cm.cmds,       'parm' : None,   
              'mainMnu' : 'List  Commands'                 },

    # Worker Function in this module.
    'ks'  : { 'func'    : killSrvr,      'parm' : None,   
              'mainMnu' : 'Kill  Server'                   },
    }

    # Process the string (command) passed to this function via the call
    # from function handleClient in file server.py.
    inputWords = inputStr.split()

    if inputWords == []:       # In case user entered just spaces.
        rspStr = 'Invalid command'
        return rspStr          # Return to srvr for forwarding to clnt.

    choice     = inputWords[0]
    optArgsStr = inputWords[1:]

    if choice in vectorDict and vectorDict[choice]['func'] is not None:
        func   = vectorDict[choice]['func']
        params = vectorDict[choice]['parm']

        if choice in ['sc'] and len(optArgsStr) == 3:
            params[0] = optArgsStr

        if choice in ['sb'] and len(optArgsStr) == 1:
            params = optArgsStr

        if choice in ['mds'] and len(optArgsStr) > 0:
            params = optArgsStr

        #try:                   # Catch exceptions in command procesing.
        if params is None:
            rsp = func()   # rsp[0] = rspStr. Vector to worker.
            return rsp[0]  # return to srvr for forwarding to clnt.

        rsp = func(params) # rsp[0] = rspStr. Vector to worker.
        return rsp[0]      # Return to srvr for forwarding to clnt.
        #except Exception as e: # pylint: disable = W0718
        #    return str(e)

    if choice in ['m','tm']:
        rspStr = ''
        for k,v in vectorDict.items():
            if   choice == 'm'  and 'mainMnu' in v:
                rspStr += ' {:3} - {}\n'.format(k, v['mainMnu'] )
            elif choice == 'tm' and 'testMnu' in v:
                rspStr += ' {:3} - {}\n'.format(k, v['testMnu'] )
        return rspStr          # Return to srvr for forwarding to clnt.

    rspStr = 'Invalid command'
    return rspStr              # Return to srvr for forwarding to clnt.
