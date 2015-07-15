# Network Peformance Testing with NetMeter

## Summary

To automate the Iperf testing procedures and to present the test results graphically, in easily understandable format, the NetMeter script can be used. It has the functionality of performing Iperf tests between a host and a guest (in both directions) with different packet sizes, varying amount of streams, and varying test times. The results are reported on an html page with a clear graphical representation. Besides the graphs, all the data files (raw and processed) and the scripts that are used to draw the plots are saved. This is done so that, for example, a need for modifications in one of the tests or plots will not require performing an entire run again, but rather the modification of a single text file. The script is also aware of the Iperf freezes, that are quite common in certain scenarios (small packet sizes on fast networks, for example).

Being in the initial stages of development, this script is still missing some features.  
To name a few:

* Sanity check for the arguments: practically no checks for the correctness of the arguments are performed.
* Code elegance - there are few repeating code blocks here and there.
* Early Iperf freeze awareness: currently a wait equal to a single test duration is required in order to detect a freeze.

In the longer run, some flexibility may be added, to allow more kinds of tests and test scenarios.

## Prerequisites:

In order to run the NetMeter one needs:

* On the host:
 * Python 3
 * Numpy (for Python 3)
 * Winexe
 * Iperf 2 (_IMPORTANT_: Version 2.0.5 or later, _i.e._ the **latest** version!)
 * gnuplot
* On the guest:
 * Iperf 2 (**The latest version as well**! Windows builds can be obtained from https://iperf.fr)

## Options:

For now, all the options are set at the beginning of the script file. They are all mandatory.  
These options are:

* `export_dir`: [string] Export directory. The results will be saved there (example: `'/home/daynix/out'`).
* `remote_addr`: [string] IP of the guest (example: `'10.0.1.114'`).
* `local_addr`: [string] Ip of the host, which the guest can connect to (example: `'10.0.0.157'`).
* `remote_iperf`: [raw string] Path to the Iperf executable on the guest (example: `r'C:\iperf\iperf.exe'`).
* `local_iperf`: [string] Path to the Iperf executable on the host (local). (Example: `'iperf'`)
* `gnuplot_bin`: [string] Path to the gnuplot executable on the host (local). (Example: `'gnuplot'`)
* `test_range`: [iterable] A list of packet sizes to test (preferably as powers of 2). (Example: `[2**x for x in range(5,17)]` - for sizes of  32B to 64KB)
* `run_duration`: [int] The duration of a single run, in seconds. Must be at least 20, preferable at least 120 (example: `300`).
* `streams`: [int] The desired number of streams (example: `1`).
* `protocols`: [iterable] The desired protocol(s). The value MUST be one of 3 possibilities: `['TCP']` | `['UDP']` | `['TCP', 'UDP']`.
* `creds`: [string] A path to the credentials file for Windows access, which consists of three lines: `username=<USERNAME>`, `password=<PASSWORD>`, and `domain=<DOMAIN>`. (Example: `'creds.dat'`)
* `title`: [string] A title for the test. Needs to be short and informative, appears as the title of the output html page. For the page to look good, the title needs to be no longer than 80 characters. (example: `'Some Informative Title'`)
* `debug`: [boolean] Turn the debugging mode on or off. In the debugging mode all Iperf commands executed will be shown. (Example: `True`)

## Running:

After obtaining all the prerequisites and configuring the network device on the guest, just run `python3 NetMeter.py`. If all is correct, it will present you with the progress, and after all the tests will run, an html page with a summary of all the results will appear in the designated output directory, in a subdirectory named as the time when the run began.
