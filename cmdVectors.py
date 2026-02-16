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
VER = ' v1.6.41 - 15-Feb-2026'
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
    'gas'   : { 'fun'  : sm.getActStyle,        
                'prm'  : [mpSharedDict, mpSharedDictLock],
                'menu' : 'Get Active Style'                      },

    'gds'   : { 'fun'  : sm.getDayStyle,        
                'prm'  : [mpSharedDict, mpSharedDictLock],
                'menu' : 'Get Day Style'                         },

    'gns'   : { 'fun'  : sm.getNightStyle,      
                'prm'  : [mpSharedDict, mpSharedDictLock],
                'menu' : 'Get Night Style'                       },

    'gAs'   : { 'fun'  : sm.getAllStyles,       
                'prm'  : None,                           
                'menu' : 'Get ALL Styles'                        },

    'gdt'   : { 'fun'  : sm.getDayTime,         
                'prm'  : [mpSharedDict, mpSharedDictLock],
                'menu' : 'Get Day Time'                          },

    'gnt'   : { 'fun'  : sm.getNightTime,       
                'prm'  : [mpSharedDict, mpSharedDictLock],
                'menu' : 'Get Night Time'                        },

    'gat'   : { 'fun'  : ut.getActThrds,        
                'prm'  : None,                           
                'menu' : 'Get Active Threads'                    },

    'gvn'   : { 'fun'  : getVer,                
                'prm'  : None,                           
                'menu' : 'Get Version Number'                    },

    # SET COMMANDS
    'sas'   : { 'fun'  : sm.setActStyle,        
                'prm'  : dfltSASParm,                           
                'menu' : 'Set Active Style'},

    'sds'   : { 'fun'  : sm.setDayStyle,        
                'prm'  : ['None',mpSharedDict, mpSharedDictLock],
                'menu' : 'Set Day Style'                         },

    'sns'   : { 'fun'  : sm.setNightStyle,      
                'prm'  : ['None',mpSharedDict, mpSharedDictLock],
                'menu' : 'Set Night Style'                       },

    'sdt'   : { 'fun'  : sm.setDayTime,         
                'prm'  : ['None',mpSharedDict, mpSharedDictLock],
                'menu' : 'Set Day Time'                          },

    'snt'   : { 'fun'  : sm.setNightTime,       
                'prm'  : ['None',mpSharedDict, mpSharedDictLock],
                'menu' : 'Set Night Time'                        },

    # FILE COMMANDS
    'ral'   : { 'fun'  : fio.readFile,          
                'prm'  : ['appLog.txt',[5]],         
                'menu' : 'Read App Log File'                     },

    'rsl'   : { 'fun'  : fio.readFile,          
                'prm'  : ['serverLog.txt',[5]],      
                'menu' : 'Read Srvr Log File'                    },

    'rse'   : { 'fun'  : fio.readFile,          
                'prm'  : ['serverException.txt',[5]],
                'menu' : 'Read Srvr Exc File'                    },

    'cal'   : { 'fun'  : fio.clearFile,         
                'prm'  : ['appLog.txt'],             
                'menu' : 'Clr App Log File'                      },

    'csl'   : { 'fun'  : fio.clearFile,         
                'prm'  : ['serverLog.txt'],          
                'menu' : 'Clr Srvr Log File'                     },

    'cse'   : { 'fun'  : fio.clearFile,         
                'prm'  : ['serverException.txt'],    
                'menu' : 'Clr Srvr Except File'},

    # OTHER COMMANDS
    'sc'    : { 'fun'  : cr.startClk,           
                'prm'  : dfltSCPrm,                         
                'menu' : 'Start Clock'                           },

    'pc'    : { 'fun'  : cr.stopClk,            
                'prm'  : qs,                                
                'menu' : 'Stop Clock'                            },

    'mus'   : { 'fun'  : ms.mkUsrDigPikF,       
                'prm'  : [],                                
                'menu' : 'Make User Style'                       },

    'dus'   : { 'fun'  : ms.delUsrDigPikF,      
                'prm'  : dfltSASParm,                       
                'menu' : 'Delete User Style'                     },

    'dp'    : { 'fun'  : ms.displayPics,        
                'prm'  : [mpSharedDict, mpSharedDictLock],
                'menu' : 'Display Pics'                          },

    'up'    : { 'fun'  : dummy,                 
                'prm'  : None,                              
                'menu' : 'Upload Pic'                            },

    'rp'    : { 'fun'  : ms.removePic,          
                'prm'  : ['None'],                          
                'menu' : 'Remove Pic'                            },

    'us'    : { 'fun'  : su.updateSw,           
                'prm'  : getVer(),                          
                'menu' : 'Update SW'                             },

    'hlp'   : { 'fun'  : getHelp,               
                'prm'  : None,                              
                'menu' : 'Help'                                  },

    'close' : { 'fun'  : dummy,                 
                'prm'  : None,                             
                'menu' :'Disconnect'                             },

    'ks'    : { 'fun'  : dummy,                 
                'prm'  : None,                              
                'menu' : 'Kill Server'                           },

    'rbt'   : { 'fun'  : dummy,                 
                'prm'  : None,                              
                'menu' : 'Reboot RPi'                            },

    # TEST COMMANDS
    't1'    : { 'fun'  : tr.runTest1,             
                'prm'  : None,                       
                'menu' : 'Test 1 - Fill Color  by Pixels '       },

    't2'    : { 'fun'  : tr.runTest2,             
                'prm'  : None,                       
                'menu' : 'Test 2 - Fill Color  by Rows   '       },

    't3'    : { 'fun'  : tr.runTest3,             
                'prm'  : None,                       
                'menu' : 'Test 3 - Fill Color  by Screen '       },

    't4'    : { 'fun'  : tr.runTest4,             
                'prm'  : None,                       
                'menu' : 'Test 4 - Fill  Text  by Screen '       },

    't5'    : { 'fun'  : tr.runTest5,             
                'prm'  : None,                       
                'menu' : 'Test 5 - Fill  JPG   by Screen '       },

    't6'    : { 'fun'  : tr.runTest6,             
                'prm'  : [lcdCq,mpSharedDict, mpSharedDictLock],   
                'menu' : 'Test 6 - All Styles, All Screens'      },

    't7'    : { 'fun'  : tr.runTest7,             
                'prm'  : None,                       
                'menu' : 'Test 7 - Chinese,    All Screens'      },

    'rh'    : { 'fun'  : sr.hwReset,              
                'prm'  : None,                       
                'menu' : 'Reset LCD HW Test'                     },

    'rs'    : { 'fun'  : sr.swReset,              
                'prm'  : 'scLSD',                    
                'menu' : 'Reset LCD SW Test'                     },

    'sb'    : { 'fun'  : sr.setBkLight,           
                'prm'  : ['1'],                      
                'menu' : 'LCD Backlight Test'                    },

    'lc'    : { 'fun'  : cm.cmds,                 
                'prm'  : None,                       
                'menu' : 'List Commands Test'                    },
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
        if callable(params):
            params = params()

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
        't1'  : '{}'.format( '\n === TEST  COMMANDS === \n' ) }
        for k,v in vectorDict.items():

            if k in tmpDic:
                rspStr += tmpDic[k]
            rspStr += ' {:3} - {}\n'.format(k, v['menu'] )

        return rspStr          # Return to srvr for forwarding to clnt.

    rspStr = 'Invalid command'
    return rspStr              # Return to srvr for forwarding to clnt.
