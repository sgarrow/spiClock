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
import rpiShellCmds      as sc
import spiRoutines       as sr
import makeScreen        as ms
import swUpdate          as su
import fileIO            as fio
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

def uploadPic():   # Handled directly in the handleClient func so it
    return         # doesn't need a wrk funct, but because of way vectoring
                   # is done a func needs to exist. Func never called/runs.
#############################################################################

def getVer():
    VER = ' v1.6.14 - 27-Nov-2025'
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

    dfltSCPrm   = [ [], qs, styleDic, styleLk ]
    dfltSASParm = [ 'None', styleDic, styleLk, lcdCq ]

    # This dictionary embodies the worker function vector (and menu) info.
    vectorDict = {
    # GET COMMANDS
    'gas':{ 'fun': sm.getActStyle,  'prm':[styleDic,styleLk],         'menu':'Get Active Style'  },
    'gds':{ 'fun': sm.getDayStyle,  'prm':[styleDic,styleLk],         'menu':'Get Day Style'     },
    'gns':{ 'fun': sm.getNightStyle,'prm':[styleDic,styleLk],         'menu':'Get Night Style'   },
    'gAs':{ 'fun': sm.getAllStyles, 'prm':None,                       'menu':'Get ALL Styles'    },
    'gdt':{ 'fun': sm.getDayTime,   'prm':[styleDic,styleLk],         'menu':'Get Day Time'      },
    'gnt':{ 'fun': sm.getNightTime, 'prm':[styleDic,styleLk],         'menu':'Get Night Time'    },
    'gat':{ 'fun': ut.getActThrds,  'prm':None,                       'menu':'Get Active Threads'},
    'gvn':{ 'fun': getVer,          'prm':None,                       'menu':'Get Version Number'},

    # SET COMMANDS
    'sas':{ 'fun': sm.setActStyle,  'prm':dfltSASParm,                'menu':'Set Active Style'  },
    'sds':{ 'fun': sm.setDayStyle,  'prm':['None',styleDic,styleLk],  'menu':'Set Day Style'     },
    'sns':{ 'fun': sm.setNightStyle,'prm':['None',styleDic,styleLk],  'menu':'Set Night Style'   },
    'sdt':{ 'fun': sm.setDayTime,   'prm':['None',styleDic,styleLk],  'menu':'Set Day Time'      },
    'snt':{ 'fun': sm.setNightTime, 'prm':['None',styleDic,styleLk],  'menu':'Set Night Time'    },

    # FILE COMMANDS
    'ral':{ 'fun': fio.readFile,    'prm':['appLog.txt',[5]],         'menu':'Read App Log File' },
    'rsl':{ 'fun': fio.readFile,    'prm':['serverLog.txt',[5]],      'menu':'Read Srvr Log File'},
    'rse':{ 'fun': fio.readFile,    'prm':['serverException.txt',[5]],'menu':'Read Srvr Exc File'},
    'cal':{ 'fun': fio.clearFile,   'prm':['appLog.txt'],             'menu':'Clr App Log File'  },
    'csl':{ 'fun': fio.clearFile,   'prm':['serverLog.txt'],          'menu':'Clr Srvr Log File' },
    'cse':{ 'fun': fio.clearFile,   'prm':['serverException.txt'],  'menu':'Clr Srvr Except File'},

    # OTHER COMMANDS
    'sc' :{ 'fun': cr.startClk,     'prm':dfltSCPrm,                  'menu':'Start Clock'       },
    'pc' :{ 'fun': cr.stopClk,      'prm':qs,                         'menu':'Stop Clock'        },
    'mus':{ 'fun': ms.mkUsrDigPikF, 'prm':[],                         'menu':'Make User Style'   },
    'dus':{ 'fun': ms.delUsrDigPikF,'prm':dfltSASParm,                'menu':'Delete User Style' },
    'dp' :{ 'fun': ms.displayPics,  'prm':[[],qs,styleDic,styleLk],   'menu':'Display Pics'     },
    'up' :{ 'fun': uploadPic,       'prm':None,                       'menu':'Upload Pic'        },
    'rp' :{ 'fun': ms.removePic,    'prm':['None'],                   'menu':'Remove Pic'        },
    'us' :{ 'fun': su.updateSw,     'prm':None,                       'menu':'Update SW'         },
    'hlp':{ 'fun': getHelp,         'prm':None,                       'menu':'Help'              },
    'close':{'fun':disconnect,      'prm':None,                       'menu':'Disconnect'        },
    'ks' :{ 'fun': killSrvr,        'prm':None,                       'menu':'Kill Server'       },
    'rb' :{ 'fun': sc.rebootRpi,    'prm':None,                       'menu':'Reboor RPi'        },

    # TEST COMMANDS
    'rt1':{ 'fun': tr.runTest1,     'prm':None,                       'menu':'Run Test 1'        },
    'rt2':{ 'fun': tr.runTest2,     'prm':[lcdCq,styleDic,styleLk],   'menu':'Run Test 2'        },

    'rh' :{ 'fun': sr.hwReset,      'prm':None,                       'menu':'Reset LCD HW Test' },
    'rs' :{ 'fun': sr.swReset,      'prm':'scLSD',                    'menu':'Reset LCD SW Test' },
    'sb' :{ 'fun': sr.setBkLight,   'prm':['1'],                      'menu':'LCD Backlight Test'},
    'lc' :{ 'fun': cm.cmds,         'prm':None,                       'menu':'List Commands Test'},
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

        if  choice in ['sc','sdt','snt','dus','sas','sds','sns','sb'] \
            and len(optArgsStr) > 0:
            params[0] = optArgsStr

        elif choice in ['ral','rsl','rse'] \
            and len(optArgsStr) > 0:
            params[1] = optArgsStr

        elif choice in ['mus','rp'] \
            and len(optArgsStr) > 0:
            params    = optArgsStr

        elif choice in ['hlp']:
            params = [optArgsStr,vectorDict]

        #try:                   # Catch exceptions in command procesing.
        if params is None:
            rsp = func()   # rsp[0] = rspStr. Vector to worker.
            return rsp[0]  # return to srvr for forwarding to clnt.

        rsp = func(params) # rsp[0] = rspStr. Vector to worker.
        return rsp[0]      # Return to srvr for forwarding to clnt.
        #except Exception as e: # pylint: disable = W0718
        #    return str(e)

    if choice == 'm':
        rspStr = ''
        tmpDic = {
        'gas' : '{}'.format(   ' === GET   COMMANDS === \n' ),
        'sas' : '{}'.format( '\n === SET   COMMANDS === \n' ),
        'ral' : '{}'.format( '\n === FILE  COMMANDS === \n' ),
        'sc'  : '{}'.format( '\n === OTHER COMMANDS === \n' ),
        'rt1' : '{}'.format( '\n === TEST  COMMANDS === \n' ) }
        for k,v in vectorDict.items():

            if k in tmpDic:
                rspStr += tmpDic[k]
            rspStr += ' {:3} - {}\n'.format(k, v['menu'] )

        return rspStr          # Return to srvr for forwarding to clnt.

    rspStr = 'Invalid command'
    return rspStr              # Return to srvr for forwarding to clnt.
