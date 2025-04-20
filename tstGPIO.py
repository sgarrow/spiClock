import gpiozero as gp

usedGpioPins =   [11,13,15,19,23,29,31,37,12,16,22]
unUsedGpioPins = [3,5,7,21,27,33,35,8,10,18,24,26,28,32,36,38,40]

print()
for ii in usedGpioPins:
    try:
        gp.LED( 'J8:{}'.format(ii) )
        print('  used pin {:2} no exception'.format(ii))
    except:
        print('  used pin {:2}    exception'.format(ii))

print()
for ii in unUsedGpioPins:
    try:
        gp.LED( 'J8:{}'.format(ii) )
        print('unused pin {:2} no exception'.format(ii))
    except:
        print('unused pin {:2}    exception'.format(ii))

