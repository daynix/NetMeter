# Network Performance Testing with NetMeter

## Summary

To automate the Iperf testing procedures between two clients, and to present the test results graphically, in easily understandable format, the NetMeter script can be used. It is designed to perform Iperf tests in both directions, with different packet sizes, varying amount of streams, and varying test times. The results are reported on an html page with a clear graphical representation ([sample](http://daynix.github.io/NetMeter/SamplePage.html)). Besides the graphs, all the data files (raw and processed) and the scripts that are used to draw the plots are saved. This is done so that, for example, a need for modifications in one of the tests or plots will not require performing an entire run again, but rather the modification of a single text file. NetMeter is also aware of Iperf malfunctions, which are quite common in certain scenarios.

Because all the data and the plot-drawing scripts are preserved and can be changed manually or by scripting, NetMeter can be used in many scenarios.

NetMeter works between a Linux local machine, and Linux or Windows clients, when one of the clients can be the local machine itself. CPU Measurements are provided as well in such case. NetMeter can measure the bandwidth on other network adapters than the ones it connects to for control, which adds to its flexibility.

## Prerequisites:

In order to run the NetMeter one needs:

* On the host:
    * Python 3
    * Numpy (for Python 3)
    * Winexe
    * Iperf 2 (_IMPORTANT_: Version 2.0.8 or later, _i.e._ the **latest** version!)
    * sysstat
    * gnuplot
* On the guest:
    * Linux guests:
        * SSH server.
        * Iperf 2 (**The latest version as well!**)
        * sysstat
        * Disabled firewall, or port 5001 opened.
        * `sudo` access for the testing user, preferably passwordless, at least for shutdown.
    * Windows guests:
        * Iperf 2 (**The latest version as well!** Windows builds can be obtained from [here](http://sourceforge.net/projects/iperf2/files))
        * Disabled firewall, or port 5001 opened.
        * "Administrator" account access.

## Options:

All the options are set in NetMeterConfig.py file, co-located with the main script. They are all mandatory.
These options are:

* `export_dir`: [string] Export directory. The results will be saved there.
* `cl[1|2]_conn_ip`: [string] IPs to which NetMeter will connect for control (can be the same as test IPs).
* `cl[1|2]_test_ip`: [string] IPs between which the testing will be performed (can be the same as connecting IPs).
* `cl[1|2]_iperf`: [raw string] Paths to the Iperf executables on the clients (or just the commands, if Iperf is in executable path already).
* `gnuplot_bin`: [string] Path to the gnuplot binary on the local machine (or just the command, if gnuplot is in path already).
* `test_range`: [iterable] A list of packet sizes to test (preferably as powers of 2). (Example: `[2**x for x in range(5,17)]` - for sizes of  32B to 64KB)
* `run_duration`: [int] The duration of a single run, in seconds. Must be at least 20, preferable at least 120. (Example: `300`)
* `streams`: [iterable] The desired number of streams to test. (Example: `[1, 4]`)
* `protocols`: [iterable] The desired protocol(s). The value MUST be one of 3 possibilities: `['TCP']` | `['UDP']` | `['TCP', 'UDP']`.
* `tcp_win_size`: [str or None] The desired TCP window size. Set to **None** for default. (Example: `'1M'`)
* `access_method_cl[1|2]`: [string] The access method path: `'ssh'` for Linux, `'winexe'` for Windows, or `'local'`, if the client is the local machine (the command, or full path to it).
* `ssh_port_cl[1|2]`: [string] SSH port on the client (needed only if the access is by SSH).
* `creds`: [string] A path to the credentials file. (Example: `'creds.dat'`)

  For Linux access it should contain two lines:
  ```
  username=<USERNAME>
  key=<PATH_TO_KEYFILE>
  ```
  where `<PATH_TO_KEYFILE>` is the path to the private (and unencrypted!) key to access the guest. If the key does not exist, and you are using OpenSSH, it can be generated and transferred to the guest upon the initial run of NetMeter.

  For Windows access, the creds file should contain three lines:
  ```
  username=<USERNAME>
  password=<PASSWORD>
  domain=<DOMAIN>
  ```
* `title`: [string] A title for the test. Needs to be short and informative, appears as the title of the output html page. For the page to look good, the title needs to be no longer than 80 characters. (Example: `'Some Informative Title'`)
* `cl[1|2]_pretty_name`: [string] A very short and informative name for each of the clients. This will be printed on the plots and on the report. (Example: `'Ubuntu VM'`)
* `shutdown`: [boolean] Set to `True` in order to shut down both the clients after all the tests are done, or `False` otherwise. Useful when doing long/overnight tests. _NOTE_: the local machine will **not** shut down, even if it is one of the clients.
* `debug`: [boolean] Turn the debugging mode on or off. In debugging mode all the Iperf commands that are executed will be shown.

## Running:

After obtaining all the prerequisites and configuring the network devices on the clients, just run `python3 NetMeter.py`. If all is correct, it will present you with the progress, and after all the tests will run, an html page with a summary of all the results will appear in the designated output directory, in subdirectories named by the time when the run began, the protocol, and the number of streams.

_IMPORTANT_: Make sure that a firewall does not interfere with the connections!

## Sample output:

A sample output can be seen [here](http://daynix.github.io/NetMeter/SamplePage.html). This page was generated automatically, by NetMeter, during a standard test scenario. Notice the distinctive markings for the troublesome tests on the two main plots, "By Buffer Size", ("Approx. BW" in the legend) and the warnings on the corresponding individual plots (in their top left corner). These tests alone can be run manually again, and the same generated gnuplot scripts can be used to plot their new results.

All the generated scripts and files for this page are residing on [this branch](https://github.com/daynix/NetMeter/tree/gh-pages).

## Looking at the results:

Generally, the results are presented as plots on a generated html page. But all the raw, as well as the processed, data is saved. This is done for the scenarios when more manual interaction is needed. All the raw files are placed to `raw-data` subdirectory. The files that are generated are:

(`<common>` = `<protocol>_<number of streams>_st_<date, time>`)

* `<common>_<test direction>_<buffer/datagram size>_iperf.dat`: just the raw Iperf server output.
* `<common>_<test direction>_<buffer/datagram size>_mpstat.dat`: just the raw Mpstat output (if CPU was measured).
* `<common>_<test direction>_<buffer/datagram size>_iperf_processed.dat`: the processed Iperf output. It contains 3 columns: time (relatively to the beginning of this specific measurement), the sum of the bandwidths from all the streams (obviously, if only one stream was used, the sum is just the bandwidth of this stream), and the standard deviation (if one stream is used, the standard deviation will be zero). The bandwidth units are b/s.
* `<common>_<test direction>_<buffer/datagram size>_mpstat_processed.dat`: Very similar to the above, only the measurements represent the CPU usage fraction on the local machine (these files are generated only when the local machine serves as one of the clients). Notice, that to get accurate readings here, as little as possible processes besides the test setup should run on the local machine.
* `<common>_<test direction>_iperf_summary.dat`: Summary of the Iperf results. The 5 columns represent:
    * Did the test complete correctly? (1: OK, 0: test had problems, -1: test failed entirely).
    * The buffer/datagram size (B).
    * Bandwidth (b/s).
    * Standard deviation between the measurements of the same buffer/datagram size (b/s).
    * Bandwidth (in more humanly readable format, provided for convenience).
* `<common>_<test direction>_mpstat_summary.dat`: Similar to the above, but simpler - only 3 columns:
    * The buffer/datagram size (B).
    * Total fraction of CPU used.
    * The standard deviation of CPU usage between the measurements of the same buffer/datagram size.
    * This file appears only if the CPU fraction was measured (the local machine is one of the clients).
* `<common>_<test direction>_<buffer/datagram size>.plt`: gnuplot script to generate the corresponding plot. Notice, the plots can be manipulated from their scripts, and generated by running `gnuplot <filename>`! So that any irregularities can be fixed and, annotations can be added manually to each plot!
* `<common>_<test direction>_summary.plt`: This is the gnuplot script to summarize all the data for a test in one direction (host to guest, or guest to host). Again, if automatically generated plot has some issues, they can be fixed from this script. It is also possible to add arrows, to generate the plot in an interactive format, or in vector graphics, etc. There are many other possibilities for tweaking.
* `<common>_iperf_commands.log`: A log of all the Iperf commands issued during the run.
* `<common>_<test direction>_<buffer/datagram size>_iperf.err`: Iperf server error output.
* `<common>_<test direction>_<buffer/datagram size>_iperf_client.err`: Iperf client error output.
* `<common>_<test direction>_<buffer/datagram size>_iperf_client.out`: Iperf client standard output.

## Comparing between the results of different runs:

The `NM_compare.py` script enables comparison of data from pairs of different NetMeter runs.

Usage:
```
./NM_compare.py old_dir1,old_dir2,... new_dir1,new_dir2,... output_dir
```
This will produce comparison plots between (`old_dir1` and `new_dir1`), (`old_dir2` and `new_dir2`), and so on, and write them to the output directory. The specified directories should contain the NetMeter output files.

* The results will be in the form of A4-sized pdf pages, one for each pair of compared directories, and the gnuplot scripts to (re)create them. These scripts can be adjusted as needed (default titles, colors, and so on can be changed).
* If changing the scripts, don't forget to modify the paths to the data files and the output file - in the generated scripts they are relative to the directory from which they were generated.
* Please note, that for correct operation this script relies on the default naming of the NetMeter output files.
* Tip: To unite the pages into one document, use:
  ```
  pdfunite page1.pdf page2.pdf ... output.pdf
  ```
    * `pdfunite` should be available on your system if you have Poppler installed.
    * **DO NOT FORGET** to specify the output file! Otherwise, the last results page will be overwritten!
