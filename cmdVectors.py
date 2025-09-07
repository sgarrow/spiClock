'''
When a client enters a command those commands are received by function
handleClient in file server.py.  The command (string) is forwarded to
function "vector" (in this file) and the appropriate "worker" function
is then vectored to in file cmdWorkers.py.
'''

import multiprocessing   as mp
import styleMgmtRoutines as sm
import startStopClock    as cr
import testRoutines      as tr
import spiRoutines       as sr
import makeScreen        as ms
import swUpdate          as su
import utils             as ut
import cmds              as cm
#############################################################################

lcdCq = mp.Queue() # LCD Cmd Q. mp queue must be used here.
lcdRq = mp.Queue() # LCD Rsp Q. mp queue must be used here.
clkCq = mp.Queue() # CLK Cmd Q. mp queue must be used here.
clkRq = mp.Queue() # CLK Rsp Q. mp queue must be used here.
qs    = [ lcdCq, lcdRq, clkCq, clkRq ]

ESC = '\x1b'
RED = '[31m'
TERMINATE = '[0m'

REDON  = ESC + RED
REDOFF = ESC + TERMINATE
#############################################################################
#############################################################################

def killSrvr():    # The ks handled directly in the handleClient func so it
    return         # doesn't need a wrk funct, but because of way vectoring
                   # is done a func needs to exist. Func never called/runs.
#############################################################################

def disconnect():  # Handled directly in the handleClient func so it
    return         # doesn't need a wrk funct, but because of way vectoring
                   # is done a func needs to exist. Func never called/runs.
#############################################################################
def getVer():
    VER = ' v1.4.13 - 07-Sep-2025'
    return [VER]
#############################################################################

def getHelp(prmLst):
    cmds = prmLst[0]
    vectorDict = prmLst[1]

    hlpStr = ''
    if len(cmds) == 0:
        hlpStr += ' No command specified.  Example usage: hlp sc'

    for cmd in cmds:
        try:
            docStr = vectorDict[cmd]['fun'].__doc__

            if docStr is None:
                hlpStr += ' No help for command {} yet available.\n'.format(cmd)
            else:
                hlpStr += ' Help for command {} follows:\n'.format(cmd) + docStr + '\n'

        except KeyError:
            hlpStr += ' {} is not a valid command.\n'.format(cmd)

        hlpStr += '\n'

    return [hlpStr]
#############################################################################

def vector(inputStr,styleDic,styleLk): # called from handleClient.

#    print('vector',styleDic, styleLk)
    mTxt = {
    # MAIN MENU
    'sc'  : 'Start Clock',
    'pc'  : 'Stop  Clock',
    'cb'  : 'Ctrl Brightness',

    'gas' : 'Get Active Style',
    'gds' : 'Get Day Style',
    'gns' : 'Get Night Style',
    'gAs' : 'Get ALL Styles',
    'sas' : 'Set Active Style',
    'sds' : 'Set Day Style',
    'sns' : 'Set Night Style',

    'mus' : 'Make User Style',

    'gnt' : 'Get Night Time',
    'gdt' : 'Get Day Time',
    'snt' : 'Set Night Time',
    'sdt' : 'Set Day Time',

    'dp'  : 'Disp Pics',

    'us'  : 'Update SW',
    'ral' : 'Read App Log File',
    'rsl' : 'Read Server Log File',
    'rse' : 'Read Server Except File',
    'cal' : 'Clear App Log File',
    'csl' : 'Clear Server Log File',
    'cse' : 'Clear Server Except File',

    'hlp' : 'Help',
    'gvn' : 'Get Version Number',
    'tm'  : 'Test Menu',
    'close' : 'Disconnect',

    # TEST MENU
    'rt1' : 'Run   Test 1',
    'rt2' : 'Run   Test 2',
    'rt3' : 'Run   Test 3',
    'rt4' : 'Run   Test 4',

    'rh'  : 'Reset LCD HW',
    'rs'  : 'Reset LCD SW',
    'sb'  : 'Set   LCD Backlight',

    'gat' : 'Get   Active Threads',
    'lc'  : 'List  Commands',

    'ks'  : 'Kill  Server',
    }
    dfltMDSPrm  = [ 'redOnGreen', '255','0','0', '0','0','255' ]
    dfltSCPrm   = [ [], qs, styleDic, styleLk ]
    dfltSASParm = [ 'None', styleDic, styleLk, lcdCq ]

    # This dictionary embodies the worker function vector (and menu) info.
    vectorDict = {

    # MAIN MENU (displayed when m command issued).
    # Worker Function in clockRoutines.py.
    'sc' :{ 'fun': cr.startClk,         'prm': dfltSCPrm,                    'mnMnu': mTxt['sc' ]},
    'pc' :{ 'fun': cr.stopClk,          'prm': qs,                           'mnMnu': mTxt['pc' ]},
   #'cb' :{ 'fun': cr.ctrlBright,       'prm': ['None'],                     'mnMnu': mTxt['cb' ]},

    # Worker Function in styleMgmtRoutines.py.
    'gas':{ 'fun': sm.getActiveStyle,   'prm': [styleDic,styleLk],           'mnMnu': mTxt['gas']},
    'gds':{ 'fun': sm.getDayStyle,      'prm': [styleDic,styleLk],           'mnMnu': mTxt['gds']},
    'gns':{ 'fun': sm.getNightStyle,    'prm': [styleDic,styleLk],           'mnMnu': mTxt['gns']},
    'gAs':{ 'fun': sm.getAllStyles,     'prm': None,                         'mnMnu': mTxt['gAs']},
    'sas':{ 'fun': sm.setActiveStyle,   'prm': dfltSASParm,                  'mnMnu': mTxt['sas']},
    'sds':{ 'fun': sm.setDayStyle,      'prm': ['None',styleDic,styleLk],    'mnMnu': mTxt['sds']},
    'sns':{ 'fun': sm.setNightStyle,    'prm': ['None',styleDic,styleLk],    'mnMnu': mTxt['sns']},

    # Worker Function in makeScreens.py.
    'mus':{ 'fun': ms.mkUsrDigPikF,     'prm': dfltMDSPrm,                   'mnMnu': mTxt['mus']},

    # Worker Function in styleMgmtRoutines.py.
    'gdt':{ 'fun': sm.getDayTime,       'prm': [styleDic,styleLk],           'mnMnu': mTxt['gdt']},
    'gnt':{ 'fun': sm.getNightTime,     'prm': [styleDic,styleLk],           'mnMnu': mTxt['gnt']},
    'sdt':{ 'fun': sm.setDayTime,       'prm': ['None',styleDic,styleLk],    'mnMnu': mTxt['sdt']},
    'snt':{ 'fun': sm.setNightTime,     'prm': ['None',styleDic,styleLk],    'mnMnu': mTxt['snt']},

    # Worker Function in utils.py.
    'dp' :{ 'fun': ut.displayPics,      'prm': [[],qs,styleDic,styleLk],     'mnMnu': mTxt['dp' ]},

    # Worker Function in utils.py.
    'us' :{ 'fun' : su.updateSw,        'prm': None,                         'mnMnu': mTxt['us' ]},
    'ral':{ 'fun' : ut.readFile,        'prm' : ['appLog.txt',[5]],          'mnMnu': mTxt['ral'] },
    'rsl':{ 'fun' : ut.readFile,        'prm' : ['serverLog.txt',[5]],       'mnMnu': mTxt['rsl'] },
    'rse':{ 'fun' : ut.readFile,        'prm' : ['serverException.txt',[5]], 'mnMnu': mTxt['rse'] },
    'cal':{ 'fun' : ut.clearFile,       'prm' : ['appLog.txt'],              'mnMnu': mTxt['cal'] },
    'csl':{ 'fun' : ut.clearFile,       'prm' : ['serverLog.txt'],           'mnMnu': mTxt['csl'] },
    'cse':{ 'fun' : ut.clearFile,       'prm' : ['serverException.txt'],     'mnMnu': mTxt['cse'] },

    # Worker Function in this module.
    'hlp':{ 'fun': getHelp,             'prm': None,                         'mnMnu': mTxt['hlp']},
    'gvn':{ 'fun': getVer,              'prm': None,                         'mnMnu': mTxt['gvn']},
    'tm' :{ 'fun': None,                'prm': None,                         'mnMnu': mTxt['tm' ]},
    'close':{'fun':disconnect,          'prm': None,                         'mnMnu': mTxt['close' ]},
    #####################################################

    # TEST MENU (displayed when tm command issued).
    # Worker Function in testRoutines.py.
    'rt1':{ 'fun': tr.runTest1,         'prm': None,                         'tstMnu': mTxt['rt1']},
    'rt2':{ 'fun': tr.runTest2,         'prm': [lcdCq,styleDic,styleLk],     'tstMnu': mTxt['rt2']},
    'rt3':{ 'fun': tr.runTest3,         'prm': None,                         'tstMnu': mTxt['rt3']},
    'rt4':{ 'fun': tr.runTest4,         'prm': None,                         'tstMnu': mTxt['rt4']},

    # Worker Function in spiRoutines.py.
    'rh' :{ 'fun': sr.hwReset,          'prm': None,                         'tstMnu': mTxt['rh' ]},
    'rs' :{ 'fun': sr.swReset,          'prm': 'scLSD',                      'tstMnu': mTxt['rs' ]},
    'sb' :{ 'fun': sr.setBkLight,       'prm': [0],                          'tstMnu': mTxt['sb' ]},

    # Worker Function in utils.py.
    'gat':{ 'fun': ut.getActiveThreads, 'prm': None,                       'tstMnu': mTxt['gat']},

    # Worker Function in cmds.py.
    'lc' :{ 'fun': cm.cmds,             'prm': None,                         'tstMnu': mTxt['lc' ]},

    # Worker Function in this module.
    'ks' :{ 'fun': killSrvr,            'prm': None,                         'tstMnu': mTxt['ks' ]},
    #####################################################
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

        if choice in ['sc'] and len(optArgsStr) >= 3:
            params[0] = optArgsStr

        elif choice in ['sb'] and len(optArgsStr) == 1:
            params = optArgsStr

        elif choice in ['sas','sds','sns'] and len(optArgsStr) == 1:
            params[0] = optArgsStr[0]

        elif choice in ['sdt','snt'] and len(optArgsStr) >= 6:
            params[0] = optArgsStr

        elif choice in ['mus'] and len(optArgsStr) > 0:
            params = optArgsStr

        elif choice in ['hlp']:
            params = [optArgsStr,vectorDict]

        elif choice in ['ral','rsl','rse'] and len(optArgsStr) > 0:
            params[1] = optArgsStr

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
                tmpDic = {
                'sc' : '{}'.format(  ' CLOCK COMMANDS\n'),
                'gas': '{}'.format('\n STYLE COMMANDS\n'),
                'hlp': '{}'.format('\n MISC  COMMANDS\n') }
                #'sc' : '{}{}{}'.format(REDON,  ' CLOCK COMMANDS\n',REDOFF),
                #'gas': '{}{}{}'.format(REDON,'\n STYLE COMMANDS\n',REDOFF),
                #'hlp': '{}{}{}'.format(REDON,'\n MISC  COMMANDS\n',REDOFF) }

                if k in tmpDic: rspStr += tmpDic[k]
                rspStr += ' {:3} - {}\n'.format(k, v['mnMnu'] )

            elif choice == 'tm' and 'tstMnu' in v:

                tmpDic = {
                'rt1': '{}'.format(  ' TEST  COMMANDS\n'),
                'rh' : '{}'.format('\n LCD   COMMANDS\n'),
                'gat': '{}'.format('\n MISC  COMMANDS\n') }
                #'rt1': '{}{}{}'.format(REDON,  ' TEST  COMMANDS\n',REDOFF),
                #'rh' : '{}{}{}'.format(REDON,'\n LCD   COMMANDS\n',REDOFF),
                #'gat': '{}{}{}'.format(REDON,'\n MISC  COMMANDS\n',REDOFF) }

                if k in tmpDic: rspStr += tmpDic[k]
                rspStr += ' {:3} - {}\n'.format(k, v['tstMnu'] )

        return rspStr          # Return to srvr for forwarding to clnt.

    rspStr = 'Invalid command'
    return rspStr              # Return to srvr for forwarding to clnt.
