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
############################################################################
#############################################################################

def killSrvr():    # The ks handled directly in the handleClient func so it
    return         # doesn't need a wrk funct, but because of way vectoring
                   # is done a func needs to exist. Func never called/runs.
#############################################################################

def getVer():
    VER = ' v1.1.1 - 30-Apr-2025'
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
def vector(inputStr): # called from handleClient. inputStr from client.

    menuTxt = {
    'sc'  : 'Start Clock',
    'pc'  : 'stoP  Clock',
    'cb'  : 'Ctrl  Brightness',
    'tm'  : 'Test  Menu',

    'rt1' : 'Run Test 1',
    'rt2' : 'Run Test 2',
    'rt3' : 'Run Test 3',

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
    'sc' : { 'func': cr.startClk,         'parm': [[],qs],       'mainMnu': menuTxt['sc' ]},
    'pc' : { 'func': cr.stopClk,          'parm': qs,            'mainMnu': menuTxt['pc' ]},
    'cb' : { 'func': cr.controlBrightness,'parm': ['None'],      'mainMnu': menuTxt['cb' ]},
    'tm' : { 'func': None,                'parm': None,          'mainMnu': menuTxt['tm' ]},

    # Worker Function in testRoutines.py.
    'rt1': { 'func': tr.runTest1,         'parm': None,          'testMnu': menuTxt['rt1']},
    'rt2': { 'func': tr.runTest2,         'parm': lcdCq,         'testMnu': menuTxt['rt2']},
    'rt3': { 'func': tr.runTest3,         'parm': None,          'testMnu': menuTxt['rt3']},

    # Worker Function in spiRoutines.py.
    'rh' : { 'func': sr.hwReset,          'parm': None,          'mainMnu': menuTxt['rh' ]},
    'rs' : { 'func': sr.swReset,          'parm': 'scLSD',       'mainMnu': menuTxt['rs' ]},
    'sb' : { 'func': sr.setBkLight,       'parm': [0],           'mainMnu': menuTxt['sb' ]},

    # Worker Function in styleMgmtRoutines.py.
    'gas': { 'func': sm.getActiveStyle,   'parm': None,          'mainMnu': menuTxt['gas']},
    'sas': { 'func': sm.setActiveStyle,   'parm': ['None',lcdCq],'mainMnu': menuTxt['sas']},

    'gAs': { 'func': sm.getAllStyles,     'parm': None,          'mainMnu': menuTxt['gAs']},

    'gds': { 'func': sm.getDayStyle,      'parm': None,          'mainMnu': menuTxt['gds']},
    'sds': { 'func': sm.setDayStyle,      'parm': ['None'],      'mainMnu': menuTxt['sds']},

    'gns': { 'func': sm.getNightStyle,    'parm': None,          'mainMnu': menuTxt['gns']},
    'sns': { 'func': sm.setNightStyle,    'parm': ['None'],      'mainMnu': menuTxt['sns']},

    # Worker Function in makeScreens.py.
    'mus': { 'func': ms.mkUserDigPikFile, 'parm': dfltMDSPrm,    'mainMnu': menuTxt['mus']},

    # Worker Function in cmds.py.
    'lc' : { 'func': cm.cmds,             'parm': None,          'mainMnu': menuTxt['lc' ]},

    # Worker Function in this module.
    'ks' : { 'func': killSrvr,            'parm': None,          'mainMnu': menuTxt['ks' ]},
    'gat': { 'func': getActiveThreads,    'parm': None,          'mainMnu': menuTxt['gat']},
    'gvn': { 'func': getVer,              'parm': None,          'mainMnu': menuTxt['gvn']},
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
            if   choice == 'm'  and 'mainMnu' in v:
                rspStr += ' {:3} - {}\n'.format(k, v['mainMnu'] )
            elif choice == 'tm' and 'testMnu' in v:
                rspStr += ' {:3} - {}\n'.format(k, v['testMnu'] )
        return rspStr          # Return to srvr for forwarding to clnt.

    rspStr = 'Invalid command'
    return rspStr              # Return to srvr for forwarding to clnt.
