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

# IPs of the clients for connection. [str]
# Example: '10.0.1.114'
cl1_conn_ip = '10.0.1.114'
cl2_conn_ip = '10.0.1.115'

# IPs of the clients for testing (may use the same as for connection). [str]
# Example: '192.168.100.11'
cl1_test_ip = '192.168.100.21'
cl2_test_ip = '192.168.100.22'

# Paths to the Iperf executables on the clients. [raw str]
# Example: r'C:\iperf\iperf.exe'
cl1_iperf = r'iperf'
cl2_iperf = r'C:\iperf\iperf.exe'

# Path to the gnuplot executable on the local machine. [str]
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

# The desired TCP window size. [str or None].
# Set to None for default. Example: '1M'.
tcp_win_size = None

# Remote access method path: 'ssh' (for Linux), 'winexe' (for Windows),
# or 'local' (to run on one of the clients). [str]
# Note: for ssh access, an ssh key is required! The key needs to be unencrypted.
# If not present, it will be generated (if using OpenSSH).
# Examples: 'ssh' or 'winexe' or '/home/user/bin/winexe' or 'local'
access_method_cl1 = 'ssh'
access_method_cl2 = 'winexe'

# Remote access port (needed only for ssh access). [str]
# Example: '22'
ssh_port_cl1 = '22'
ssh_port_cl2 = '22'

# A path to the credentials file for remote access. [str]
# This file should contain two or three lines:
#    username=<USERNAME> (for Windows clients it should be "Administrator", for Linux clients
#                         - any user that can at least shut down without a password via sudo.
#                         e.g. "USERNAME ALL= NOPASSWD: /sbin/shutdown -h now" in "visudo")
#    [ password=<PASSWORD> | key=<PATH_TO_KEY> ] (Password (for winexe access) or a path to the private ssh key (for ssh access))
#    domain=<DOMAIN> (Needed only for Windows clients)
# Example: 'creds.dat'
creds_cl1 = 'creds.dat'
creds_cl2 = 'creds.dat'

# A title for the test. Needs to be short and informative, appears as the title of the output html page.
# For the page to look good, the title needs to be no longer than 80 characters. [str]
# Example: 'Some Informative Title'
title = 'Test Results (5 min per run)'

# Pretty names for the clients. Should be as short as possible, and informative -
# they will appear on the plots and the report. [str]
# Examples: 'Ubuntu VM', 'e1000e', 'Win 2012'
cl1_pretty_name = 'Ubuntu VM'
cl2_pretty_name = 'W2012R2 VM'

# Shut down the the clients when all tests are over?
# This is useful when doing long/overnight tests. [bool]
# ATTENTION: It will NOT shut down the local machine, even if it is one of the clients!
# Exanple: True
shutdown = True

# Enable debugging mode?
# In the debugging mode the underlying Iperf commands will be presented. [bool]
# Exanple: True
debug = False

### End editable parameters ###
###############################
