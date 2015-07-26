# Network Peformance Testing with NetMeter

## Summary

To automate the Iperf testing procedures between a virtual machine and its host, and to present the test results graphically, in easily understandable format, the NetMeter script can be used. It has the functionality of performing Iperf tests between a host and a guest (in both directions) with different packet sizes, varying amount of streams, and varying test times. The results are reported on an html page with a clear graphical representation. Besides the graphs, all the data files (raw and processed) and the scripts that are used to draw the plots are saved. This is done so that, for example, a need for modifications in one of the tests or plots will not require performing an entire run again, but rather the modification of a single text file. NetMeter is also aware of Iperf malfunctions, which are quite common in certain scenarios.

Because all the data and the plot-drawing scripts are preserved and can be changed manually or by scripting, NetMeter can also be used in other scenarios than those for which it was written.

Being in the initial stages of development, NetMeter is still missing some features. Currently, it works only between a host Linux machine, and a Windows guest. In the longer run, it should also be able to measure the bandwidth between two guests, and the guests may run Windows or Linux.

## Prerequisites:

In order to run the NetMeter one needs:

* On the host:
 * Python 3
 * Numpy (for Python 3)
 * Winexe
 * Iperf 2 (_IMPORTANT_: Version 2.0.8 or later, _i.e._ the **latest** version!)
 * gnuplot
* On the guest:
 * Iperf 2 (**The latest version as well**! Windows builds can be obtained from http://sourceforge.net/projects/iperf2/files)

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
* `shutdown`: [boolean] Set to `True` in order to shut down the guest after all the tests are done, `False` otherwise. Useful when doing long/overnight tests.
* `debug`: [boolean] Turn the debugging mode on or off. In the debugging mode all Iperf commands executed will be shown. (Example: `True`)

## Running:

After obtaining all the prerequisites and configuring the network device on the guest, just run `python3 NetMeter.py`. If all is correct, it will present you with the progress, and after all the tests will run, an html page with a summary of all the results will appear in the designated output directory, in a subdirectory named as the time when the run began.

_IMPORTANT_: Make sure that a firewall does not interfere with the connections!

## Sample output:

A sample output can be seen [here](http://daynix.github.io/NetMeter/SamplePage.html).
This page was generated automatically, by NetMeter, during a standard test scenario. Notice the distinctive markings for the troublesome tests on the two main plots, "By Buffer Size", ("Approx. BW" in the legend) and the warnings on the corresponding individual plots (in their top left corner). These tests alone can be run manually again, and the same generated gnuplot scripts can be used to plot their new results.

All the generated scripts and files for this page are residing on [this branch](https://github.com/daynix/NetMeter/tree/gh-pages).

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
