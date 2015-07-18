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

* `export_dir`: [string] Export directory. The results will be saved there. (Example: `'/home/daynix/out'`)
* `remote_addr`: [string] IP of the guest. (Example: `'10.0.1.114'`)
* `local_addr`: [string] Ip of the host, which the guest can connect to. (Example: `'10.0.0.157'`)
* `remote_iperf`: [raw string] Path to the Iperf executable on the guest. (Example: `r'C:\iperf\iperf.exe'`)
* `local_iperf`: [string] Path to the Iperf executable on the host (local). (Example: `'iperf'`)
* `gnuplot_bin`: [string] Path to the gnuplot executable on the host (local). (Example: `'gnuplot'`)
* `test_range`: [iterable] A list of packet sizes to test (preferably as powers of 2). (Example: `[2**x for x in range(5,17)]` - for sizes of  32B to 64KB)
* `run_duration`: [int] The duration of a single run, in seconds. Must be at least 20, preferable at least 120. (Example: `300`)
* `streams`: [iterable] The desired number of streams to test. (Example: `[1, 4]`)
* `protocols`: [iterable] The desired protocol(s). The value MUST be one of 3 possibilities: `['TCP']` | `['UDP']` | `['TCP', 'UDP']`.
* `creds`: [string] A path to the credentials file for Windows access, which consists of three lines: `username=<USERNAME>`, `password=<PASSWORD>`, and `domain=<DOMAIN>`. (Example: `'creds.dat'`)
* `title`: [string] A title for the test. Needs to be short and informative, appears as the title of the output html page. For the page to look good, the title needs to be no longer than 80 characters. (Example: `'Some Informative Title'`)
* `debug`: [boolean] Turn the debugging mode on or off. In the debugging mode all Iperf commands executed will be shown. (Example: `True`)

## Running:

After obtaining all the prerequisites and configuring the network device on the guest, just run `python3 NetMeter.py`. If all is correct, it will present you with the progress, and after all the tests will run, an html page with a summary of all the results will appear in the designated output directory, in a subdirectory named as the time when the run began.

_IMPORTANT_: Make sure that a firewall does not interfere with the connections!

## Looking at the results:

Generally, the results are presented as plots on a generated html page. But all the raw, as well as the processed, data is saved. This is done for the scenarios when more manual interaction is needed. The files that are generated are:

(`<common>` = `<protocol>_<number of streams>_st_<date, time>`)

* `<common>_<test direction>_<buffer/datagram size>_iperf.dat`: just the raw Iperf output.
* `<common>_<test direction>_<buffer/datagram size>_mpstat.dat`: just the raw Mpstat output.
* `<common>_<test direction>_<buffer/datagram size>_iperf_processed.dat`: the processed Iperf output. It contains 3 columns: time (relatively to the beginning of this specific measurement), the sum of the bandwidths from all the streams (obviously, if only one stream was used, the sum is just the bandwidth of this stream), and the standard deviation (if one stream is used, the standard deviation will be zero). The bandwidth units are b/s.
* `<common>_<test direction>_<buffer/datagram size>_mpstat_processed.dat`: Very similar to the above, only the measurements represent the CPU usage fraction on the host machine. Notice, that to get accurate readings here, as little as possible processes besides the test setup should run on the host.
* `<common>_<test direction>_iperf_summary.dat`: Summary of the Iperf results. The 5 columns represent:
 * Did the test complete correctly? (0/1)
 * The buffer/datagram size (B)
 * Bandwidth (b/s)
 * Standard deviation between the measurements of the same buffer/datagram size (b/s)
 * Bandwidth (in more humanly readable format, provided for convenience)
* `<common>_<test direction>_mpstat_summary.dat`: Similar to the above, but simpler - only 3 columns:
 * The buffer/datagram size (B)
 * Total fraction of CPU used
 * The standard deviation of CPU usage between the measurements of the same buffer/datagram size
* `<common>_<test direction>_<buffer/datagram size>.plt`: gnuplot script to generate the corresponding plot. Notice, the plots can be manipulated from their scripts, and generated by running `gnuplot <filename>`! So that any irregularities can be fixed and, annotations can be added manually to each plot!
* `<common>_<test direction>_summary.plt`: This is the gnuplot script to summarize all the data for a test in one direction (host to guest, or guest to host). Again, if automatically generated plot has some issues, they can be fixed from this script. It is also possible to add arrows, to generate the plot in an interactive format, or in vector graphics, etc. There are many other possibilities for tweaking.
