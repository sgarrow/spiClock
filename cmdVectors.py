#  C:\Users\stang\AppData\Roaming\Python\Python312\Scripts\pylint .\*.py
'''
When a client enters a command those commands are received by function 
handleClient in file server.py.  The command (string) is forwarded to
function "vector" (in this file) and the appropriate "worker" function
is then vectored to.
'''

import multiprocessing   as mp
import styleMgmtRoutines as sm
import startStopClock    as cr
import testRoutines      as tr
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
#############################################################################

# Cmds close,ks,up,rbt are handled directly in the handleClient func so they
# don't need a wrk funct, but because of way vectoring is done a func needs
# to exist. This function is never called/runs.
def dummy():
    return
#############################################################################

# Version number of the "app".
# As opposed to the version number of the "server" which is in fileIO.py
VER = ' v1.6.46 - 17-Feb-2026'
def getVer():
    appVer = VER
    srvVer = fio.VER
    rspStr = ' appVer = {} \n serVer = {}'.format(appVer, srvVer)
    return [rspStr]
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

def vector(inputStr,mpSharedDict,mpSharedDictLock): # called from handleClient.

    dfltSCPrm   = [ [], qs, mpSharedDict, mpSharedDictLock ]
    dfltSASParm = [ 'None', mpSharedDict, mpSharedDictLock, lcdCq ]

    # This dictionary embodies the worker function vector (and menu) info.
    vectorDict = {
    # GET COMMANDS
    'gas'   : { 'func' : sm.getActStyle,
                'parm' : [mpSharedDict, mpSharedDictLock],
                'menu' : 'Get Active Style'                      },

    'gds'   : { 'func' : sm.getDayStyle,
                'parm' : [mpSharedDict, mpSharedDictLock],
                'menu' : 'Get Day Style'                         },

    'gns'   : { 'func' : sm.getNightStyle,
                'parm' : [mpSharedDict, mpSharedDictLock],
                'menu' : 'Get Night Style'                       },

    'gAs'   : { 'func' : sm.getAllStyles,
                'parm' : None,
                'menu' : 'Get ALL Styles'                        },

    'gdt'   : { 'func' : sm.getDayTime,
                'parm' : [mpSharedDict, mpSharedDictLock],
                'menu' : 'Get Day Time'                          },

    'gnt'   : { 'func' : sm.getNightTime,
                'parm' : [mpSharedDict, mpSharedDictLock],
                'menu' : 'Get Night Time'                        },

    'gat'   : { 'func' : ut.getActThrds,
                'parm' : None,
                'menu' : 'Get Active Threads'                    },

    'gvn'   : { 'func' : getVer,
                'parm' : None,
                'menu' : 'Get Version Number'                    },

    # SET COMMANDS
    'sas'   : { 'func' : sm.setActStyle,
                'parm' : dfltSASParm,
                'menu' : 'Set Active Style'},

    'sds'   : { 'func' : sm.setDayStyle,
                'parm' : ['None',mpSharedDict, mpSharedDictLock],
                'menu' : 'Set Day Style'                         },

    'sns'   : { 'func' : sm.setNightStyle,
                'parm' : ['None',mpSharedDict, mpSharedDictLock],
                'menu' : 'Set Night Style'                       },

    'sdt'   : { 'func' : sm.setDayTime,
                'parm' : ['None',mpSharedDict, mpSharedDictLock],
                'menu' : 'Set Day Time'                          },

    'snt'   : { 'func' : sm.setNightTime,
                'parm' : ['None',mpSharedDict, mpSharedDictLock],
                'menu' : 'Set Night Time'                        },

    # FILE COMMANDS
    'ral'   : { 'func' : fio.readFile,
                'parm' : ['appLog.txt',[5]],
                'menu' : 'Read App Log File'                     },

    'rsl'   : { 'func' : fio.readFile,
                'parm' : ['serverLog.txt',[5]],
                'menu' : 'Read Srvr Log File'                    },

    'rse'   : { 'func' : fio.readFile,
                'parm' : ['serverException.txt',[5]],
                'menu' : 'Read Srvr Exc File'                    },

    'cal'   : { 'func' : fio.clearFile,
                'parm' : ['appLog.txt'],
                'menu' : 'Clr App Log File'                      },

    'csl'   : { 'func' : fio.clearFile,
                'parm' : ['serverLog.txt'],
                'menu' : 'Clr Srvr Log File'                     },

    'cse'   : { 'func' : fio.clearFile,
                'parm' : ['serverException.txt'],
                'menu' : 'Clr Srvr Except File'                  },

    # OTHER COMMANDS
    'sc'    : { 'func' : cr.startClk,
                'parm' : dfltSCPrm,
                'menu' : 'Start Clock'                           },

    'pc'    : { 'func' : cr.stopClk,
                'parm' : qs,
                'menu' : 'Stop Clock'                            },

    'mus'   : { 'func' : ms.mkUsrDigPikF,
                'parm' : [],
                'menu' : 'Make User Style'                       },

    'dus'   : { 'func' : ms.delUsrDigPikF,
                'parm' : dfltSASParm,
                'menu' : 'Delete User Style'                     },

    'dp'    : { 'func' : ms.displayPics,
                'parm' : [mpSharedDict, mpSharedDictLock],
                'menu' : 'Display Pics'                          },

    'up'    : { 'func' : dummy,
                'parm' : None,
                'menu' : 'Upload Pic'                            },

    'rp'    : { 'func' : ms.removePic,
                'parm' : ['None'],
                'menu' : 'Remove Pic'                            },

    'hlp'   : { 'func' : getHelp,
                'parm' : None,
                'menu' : 'Help'                                  },

    'us'    : { 'func' : su.updateSw,
                'parm' : [getVer(),'spiClock'],
                'menu' : 'Update SW'                             },

    'close' : { 'func' : dummy,
                'parm' : None,
                'menu' :'Disconnect'                             },

    'ks'    : { 'func' : dummy,
                'parm' : None,
                'menu' : 'Kill Server'                           },

    'rbt'   : { 'func' : dummy,
                'parm' : None,
                'menu' : 'Reboot RPi'                            },

    # TEST COMMANDS
    't1'    : { 'func' : tr.runTest1,
                'parm' : None,
                'menu' : 'Test 1 - Fill Color  by Pixels '       },

    't2'    : { 'func' : tr.runTest2,
                'parm' : None,
                'menu' : 'Test 2 - Fill Color  by Rows   '       },

    't3'    : { 'func' : tr.runTest3,
                'parm' : None,
                'menu' : 'Test 3 - Fill Color  by Screen '       },

    't4'    : { 'func' : tr.runTest4,
                'parm' : None,
                'menu' : 'Test 4 - Fill  Text  by Screen '       },

    't5'    : { 'func' : tr.runTest5,
                'parm' : None,
                'menu' : 'Test 5 - Fill  JPG   by Screen '       },

    't6'    : { 'func' : tr.runTest6,
                'parm' : [lcdCq,mpSharedDict, mpSharedDictLock],
                'menu' : 'Test 6 - All Styles, All Screens'      },

    't7'    : { 'func' : tr.runTest7,
                'parm' : None,
                'menu' : 'Test 7 - Chinese,    All Screens'      },

    'rh'    : { 'func' : sr.hwReset,
                'parm' : None,
                'menu' : 'Reset LCD HW Test'                     },

    'rs'    : { 'func' : sr.swReset,
                'parm' : 'scLSD',
                'menu' : 'Reset LCD SW Test'                     },

    'sb'    : { 'func' : sr.setBkLight,
                'parm' : ['1'],
                'menu' : 'LCD Backlight Test'                    },

    'lc'    : { 'func' : cm.cmds,
                'parm' : None,
                'menu' : 'List Commands Test'                    },
    }
    #####################################################

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

        try:                   # Catch exceptions in command procesing.
            if params is None:
                rsp = func()   # rsp[0] = rspStr. Vector to worker.
                return rsp[0]  # return to srvr for forwarding to clnt.

            rsp = func(params) # rsp[0] = rspStr. Vector to worker.
            return rsp[0]      # Return to srvr for forwarding to clnt.
        except Exception as e: # pylint: disable = W0718
            return str(e)

    if choice == 'm':
        tmpDic = {
        'gas' : '{}'.format(   ' === GET   COMMANDS === \n' ),
        'sas' : '{}'.format( '\n === SET   COMMANDS === \n' ),
        'ral' : '{}'.format( '\n === FILE  COMMANDS === \n' ),
        'sc'  : '{}'.format( '\n === OTHER COMMANDS === \n' ),
        't1'  : '{}'.format( '\n === TEST  COMMANDS === \n' ) }

        rspStr = ''
        for k,v in vectorDict.items():
            if k in tmpDic:
                rspStr += tmpDic[k]
            rspStr += ' {:3} - {}\n'.format(k, v['menu'] )
        return rspStr          # Return to srvr for forwarding to clnt.

    rspStr = 'Invalid command'
    return rspStr              # Return to srvr for forwarding to clnt.
