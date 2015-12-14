#!/usr/bin/python3
#
# Copyright (c) 2015, Daynix Computing LTD (www.daynix.com)
# All rights reserved.
#
# Maintained by oss@daynix.com
#
# For documentation please refer to README.md available at https://github.com/daynix/NetMeter
#
# This code is licensed under standard 3-clause BSD license.
# See file LICENSE supplied with this package for the full license text.

##############################
##### Parameters to edit #####

# Export directory. The results will be saved there. [str]
# Example: '/home/daynix/out'
export_dir = 'out'

# IP of the guest. [str]
# Example: '10.0.1.114'
remote_addr = '10.0.1.114'

# IP of the host, which the guest can connect to. [str]
# Example: '10.0.0.157'
local_addr = '10.0.0.157'

# Path to the Iperf executable on the guest. [raw str]
# Example: r'C:\iperf\iperf.exe'
remote_iperf = r'C:\iperf\iperf.exe'

# Path to the Iperf executable on the host (local). [str]
# Example: 'iperf'
local_iperf = 'iperf'

# Path to the gnuplot executable on the host (local). [str]
# Example: 'gnuplot'
gnuplot_bin = 'gnuplot'

# A list of packet sizes to test (preferably as powers of 2). [iterable]
# Example: [2**x for x in range(5,17)]  (For sizes of 32B to 64KB)
test_range = [2**x for x in range(5,17)]

# The duration of a single run, in seconds. Must be at least 20, preferable at least 120. [int]
# Example: 300
run_duration = 300

# The desired numbers of streams. [iterable]
# Example: [1, 4]
streams = [1, 4]

# The desired protocol(s). [iterable]
# The value MUST be one of 3: ['TCP'] | ['UDP'] | ['TCP', 'UDP']
protocols = ['TCP', 'UDP']

# Remote access method path: ssh (for Linux) or winexe (for Windows) only. [str]
# Note: for ssh access, an ssh key is required! The key needs to be unencrypted.
# If not present, it will be generated (if using OpenSSH).
# Example: 'ssh' or 'winexe' or '/home/user/bin/winexe'
access_method = 'winexe'
# Remote access port (needed only for ssh access). [str]
# Example: '22'
ssh_port = '22'

# A path to the credentials file for remote access. [str]
# This file should contain two or three lines:
#    username=<USERNAME> (for Windows clients it should be "Administrator", for Linux clients
#                         - any user that can at least shut down without a password via sudo.
#                         e.g. "USERNAME ALL= NOPASSWD: /sbin/shutdown -h now" in "visudo")
#    [ password=<PASSWORD> | key=<PATH_TO_KEY> ] (Password (for winexe access) or a path to the private ssh key (for ssh access))
#    domain=<DOMAIN> (Needed only for Windows clients)
# Example: 'creds.dat'
creds = 'creds.dat'

# A title for the test. Needs to be short and informative, appears as the title of the output html page.
# For the page to look good, the title needs to be no longer than 80 characters. [str]
# Example: 'Some Informative Title'
title = 'Test Results (5 min per run)'

# Shut down the the guest when all tests are over?
# This is useful when doing long/overnight tests. [bool]
# Exanple: True
shutdown = True

# Enable debugging mode?
# In the debugging mode the underlying Iperf commands will be presented. [bool]
# Exanple: True
debug = False

### End editable parameters ###
###############################
