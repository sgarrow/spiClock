'''
When a client enters a command those commands are received by function
handleClient in file server.py.  The command (string) is forwarded to
function "vector" (in this file) and the appropriate "worker" function
is then vectored to in file cmdWorkers.py.
'''

import multiprocessing   as mp
import threading         as th
import styleMgmtRoutines as sm
import startStopClock    as cr
import testRoutines      as tr
import spiRoutines       as sr
import makeScreen        as ms
import cmds              as cm
#############################################################################

lcdCq = mp.Queue() # LCD Cmd Q. mp queue must be used here.
lcdRq = mp.Queue() # LCD Rsp Q. mp queue must be used here.
clkCq = mp.Queue() # CLK Cmd Q. mp queue must be used here.
clkRq = mp.Queue() # CLK Rsp Q. mp queue must be used here.
qs    = [ lcdCq, lcdRq, clkCq, clkRq ]

openSocketsLst = []     # Needed for processing close and ks commands.

ESC = '\x1b'
RED = '[31m'
TERMINATE = '[0m'
############################################################################
#############################################################################

def killSrvr():    # The ks handled directly in the handleClient func so it
    return         # doesn't need a wrk funct, but because of way vectoring
                   # is done a func needs to exist. Func never called/runs.
#############################################################################

def getVer():
    VER = ' v1.2.0 - 05-May-2025'
    return [VER]
#############################################################################

def getActiveThreads():

    rspStr = ' Running Threads:\n'
    for t in th.enumerate():
        rspStr += '   {}\n'.format(t.name)

    rspStr += '\n Open Sockets:\n'
    for openS in openSocketsLst:
        rspStr += '   {}\n'.format(openS['ca'])

    rspStr += '\n Running Processes:\n'
    for k,v in cr.procPidDict.items():
        if v is not None:
            rspStr += '   {}\n'.format(k)
    return [rspStr]
#############################################################################
def vector(inputStr,styleDic,styleLk): # called from handleClient.

#    print('vector',styleDic, styleLk)
    mTxt = {
    'sc'  : 'Start Clock',
    'pc'  : 'stoP  Clock',
    'cb'  : 'Ctrl  Brightness',
    'tm'  : 'Test  Menu',

    'rt1' : 'Run   Test 1',
    'rt2' : 'Run   Test 2',
    'rt3' : 'Run   Test 3',

    'rh'  : 'Reset LCD HW',
    'rs'  : 'Reset LCD SW',
    'sb'  : 'Set   Backlight',

    'gas' : 'Get   Active Style',
    'sas' : 'Set   Active Style',
    'gAs' : 'Get   ALL    Styles',
    'gds' : 'Get   Day    Style',
    'sds' : 'Set   Day    Style',
    'gns' : 'Get   Night  Style',
    'sns' : 'Set   Night  Style',

    'mus' : 'Make  User   Style',

    'lc'  : 'List  Commands',
    'ks'  : 'Kill  Server',
    'gat' : 'Get   Active Threads',
    'gvn' : 'Get   Version Number',
    }
    dfltMDSPrm = ['redOnGreen', '255','0','0', '0','0','255']

    # This dictionary embodies the worker function vector (and menu) info.
    vectorDict = {
    # Worker Function in clockRoutines.py.
    'sc' :{ 'fun': cr.startClk,       'prm': [[],qs,styleDic,styleLk],       'mnMnu' : mTxt['sc' ]},
    'pc' :{ 'fun': cr.stopClk,        'prm': qs,                             'mnMnu' : mTxt['pc' ]},
   #'cb' :{ 'fun': cr.ctrlBright,     'prm': ['None'],                       'mnMnu' : mTxt['cb' ]},

    # Worker Function in testRoutines.py.
    'rt1':{ 'fun': tr.runTest1,       'prm': None,                           'tstMnu': mTxt['rt1']},
    'rt2':{ 'fun': tr.runTest2,       'prm': [lcdCq,styleDic,styleLk],       'tstMnu': mTxt['rt2']},
    'rt3':{ 'fun': tr.runTest3,       'prm': None,                           'tstMnu': mTxt['rt3']},

    # Worker Function in spiRoutines.py.
    'rh' :{ 'fun': sr.hwReset,        'prm': None,                           'tstMnu': mTxt['rh' ]},
    'rs' :{ 'fun': sr.swReset,        'prm': 'scLSD',                        'tstMnu': mTxt['rs' ]},
    'sb' :{ 'fun': sr.setBkLight,     'prm': [0],                            'tstMnu': mTxt['sb' ]},

    # Worker Function in styleMgmtRoutines.py.
    'gas':{ 'fun': sm.getActiveStyle, 'prm': [styleDic,styleLk],             'mnMnu' : mTxt['gas']},
    'gds':{ 'fun': sm.getDayStyle,    'prm': [styleDic,styleLk],             'mnMnu' : mTxt['gds']},
    'gns':{ 'fun': sm.getNightStyle,  'prm': [styleDic,styleLk],             'mnMnu' : mTxt['gns']},

    'gAs':{ 'fun': sm.getAllStyles,   'prm': None,                           'mnMnu' : mTxt['gAs']},

    'sas':{ 'fun': sm.setActiveStyle, 'prm': ['None',styleDic,styleLk,lcdCq],'mnMnu' : mTxt['sas']},
    'sds':{ 'fun': sm.setDayStyle,    'prm': ['None',styleDic,styleLk],      'mnMnu' : mTxt['sds']},
    'sns':{ 'fun': sm.setNightStyle,  'prm': ['None',styleDic,styleLk],      'mnMnu' : mTxt['sns']},

    # Worker Function in makeScreens.py.
    'mus':{ 'fun': ms.mkUsrDigPikF,   'prm': dfltMDSPrm,                     'mnMnu' : mTxt['mus']},

    # Worker Function in cmds.py.
    'lc' :{ 'fun': cm.cmds,           'prm': None,                           'tstMnu': mTxt['lc' ]},

    # Worker Function in this module.
    'ks' :{ 'fun': killSrvr,          'prm': None,                           'tstMnu': mTxt['ks' ]},
    'gat':{ 'fun': getActiveThreads,  'prm': None,                           'tstMnu': mTxt['gat']},
    'gvn':{ 'fun': getVer,            'prm': None,                           'mnMnu' : mTxt['gvn']},

    # Worker Function in clockRoutines.py.
    'tm' :{ 'fun': None,              'prm': None,                           'mnMnu' : mTxt['tm' ]},
    }

    # Process the string (command) passed to this function via the call
    # from function handleClient in file server.py.
    inputWords = inputStr.split()

    if inputWords == []:       # In case user entered just spaces.
        rspStr = 'Invalid command'
        return rspStr          # Return to srvr for forwarding to clnt.

    choice     = inputWords[0]
    optArgsStr = inputWords[1:]

    if choice in vectorDict and vectorDict[choice]['fun'] is not None:
        func   = vectorDict[choice]['fun']
        params = vectorDict[choice]['prm']

        if choice in ['sc'] and len(optArgsStr) == 3:
            params[0] = optArgsStr

        if choice in ['sb'] and len(optArgsStr) == 1:
            params = optArgsStr

        if choice in ['sas','sds','sns'] and len(optArgsStr) == 1:
            params[0] = optArgsStr[0]

        if choice in ['mus', 'cb'] and len(optArgsStr) > 0:
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

            if   choice == 'm'  and 'mnMnu' in v:

                if k == 'sc':  rspStr += '{}{}{}'.\
                    format(ESC+RED,   ' CLOCK CONTROL\n', ESC+TERMINATE )
                if k == 'gas': rspStr += '{}{}{}'.\
                format(ESC+RED, '\n STYLE CONTROL\n', ESC+TERMINATE )
                if k == 'gvn': rspStr += '{}{}{}'.\
                    format(ESC+RED, '\n MISC  CONTROL\n', ESC+TERMINATE )
                rspStr += ' {:3} - {}\n'.format(k, v['mnMnu'] )

            elif choice == 'tm' and 'tstMnu' in v:

                rspStr += ' {:3} - {}\n'.format(k, v['tstMnu'] )

        return rspStr          # Return to srvr for forwarding to clnt.

    rspStr = 'Invalid command'
    return rspStr              # Return to srvr for forwarding to clnt.
