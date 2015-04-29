# Network Peformance Testing with NetMeter

## Summary

To automate the Iperf testing procedures described previously, and to present the test results graphically, in easily understandable format, a script is under development now. It already has the functionality of performing Iperf tests between host and guest (in both directions) on different packet sizes, with varying amount of streams, and to export an html page with a graphical representation of the results. Besides the graphs, all the data files (raw and processed) and the scripts that are used to draw the plots are saved. This is done so that, for example, a need for modifications in one of the tests or plots will not require performing an entire run again, but rather the modification of a single text file. The script is also aware of the Iperf freezes, that are quite common in certain scenarios (small packet sizes on fast networks, for example).

On the other hand, being in the initial stages of development, it is still missing some vital features.  
To name a few:

* Argument parsing: for now, all the arguments need to be set inside the script.
* Sanity check for the arguments: no checks for the correctness of the arguments are performed yet.
* Export of results to a different directory than the one the script is in.
* Code elegance - there are few repeating code blocks here and there.
* Early Iperf freeze awareness: now it has to wait until the run finishes in order to detect a freeze.
* Graceful interrupt handling.

These features are easy to implement and will be added in the nearest future. In the longer run, some flexibility may be added, to allow more kinds of tests and test scenarios.

## Prerequisites:

In order to run the NetMeter one needs:

* On the host:
 * Python 3
 * Numpy (for Python 3)
 * Iperf 2 (_IMPORTANT_: Version 2.0.5 or later, i.e. the **latest** version)!
 * gnuplot
* On the guest:
 * Iperf 2 (**The latest version as well**! Windows builds can be obtained from https://iperf.fr)

## Options:

For now, all the options are set at the very end of the script file. They are all mandatory.  
These options are:

* `remote_addr`: [string] IP of guest (example: `'10.0.1.114'`)
* `local_addr`: [string] Ip of host, which the guest can connect to. (example: `'10.0.0.157'`)
* `remote_iperf`: [string] Path to the Iperf executable on the guest. (example: `'C:\iperf\iperf.exe'`)
* `local_iperf`: [string] Path to the Iperf executable on the host (local). (example: `'iperf'`)
* `gnuplot_bin`: [string] Path to the gnuplot executable on the host (local). (example: `'gnuplot'`)
* `test_range`: [iterable] A list of packet sizes to test (preferably as powers of 2). (example: `[2**x for x in range(5,17)]  #32B --> 64KB` )
* `run_duration`: [int] The duration of a single run, in seconds. Must be at least 20, preferable at least 120. (example: `300` )
* `streams`: [int] The desired number of streams. (example: `1`)
* `creds`: [string] A path to the credentials file for Windows access, which consists of three lines: 'username=<USERNAME>', 'password=<PASSWORD>', and 'domain=<DOMAIN>'. (example: `'creds.dat'`)
* `title`: [string] A title for the test. Needs to be short and informative, appears as the title of the output html page. For the page to look good, the title needs to be no longer than 80 characters. (example: `'Some Informative Title'`)

## Running:

After obtaining all the prerequisites and configuring the network device on the guest, just run "`python3 NetMeter.py`". If all is correct, it will present you with the progress, and after all tests are done, an html page with a summary of all the results will appear in the same directory as the script.

