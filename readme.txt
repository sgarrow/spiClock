A Raspberry Pi hosted psuedo-nixie clock that uses 320x240 SPI LCD
displays instead of actual nixie tubes.

The clock runs within a server running on the RPi.  Users can 
connect to he server with the supplied client to control the clock.

Some of the clock's code is common with another, second, project.
To prevent having to copy/paste changes/bug-fixes back and forth 
between projects, this common code resides in a third project.
Copy the shared code into the root directory of this project.

The common code can be found here:
https://github.com/sgarrow/sharedClientServerCode

Details can be found in the docs folder.

