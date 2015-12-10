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

import numpy as np
import sys
import signal
from datetime import datetime, timedelta
from time import sleep
from subprocess import Popen, PIPE
from os import makedirs
from os.path import isdir, isfile, join
from ntpath import dirname, basename

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

rundate = datetime.now().strftime('%Y_%m_%d_%H-%M-%S')
logo = (
        'data:image/png;base64,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'
        'SUVORK5CYII='
       )


class Connect:
    def __init__(self, rem_loc):
        try:
            Connect.conn_type
        except AttributeError:
            self.verify_credsfile()

        self.rem_loc = rem_loc
        if self.rem_loc == 'local':
            self.iperf_cmd = [local_iperf]
            self.stop_iperf = ['killall', '-9', basename(local_iperf)]
        elif self.rem_loc == 'remote' and Connect.conn_type == 'ssh':
            self.auth = [access_method, '-i', Connect.key, '-p', ssh_port, '-l', Connect.username,
                         '-o', 'UserKnownHostsFile=/dev/null', '-o', 'StrictHostKeyChecking=no',
                         '-o', 'BatchMode=yes', '-o', 'LogLevel=ERROR', remote_addr]
            self.iperf_cmd = [remote_iperf]
            self.stop_iperf = ['killall', '-9', basename(remote_iperf)]
            self.shutdown_command = ['sudo', 'shutdown', '-h', 'now']
        elif self.rem_loc == 'remote' and Connect.conn_type == 'winexe':
            self.auth = [access_method, '-A',  creds, '//' + remote_addr]
            self.iperf_cmd = [remote_iperf]
            self.stop_iperf = ['taskkill /im ' + basename(remote_iperf) + ' /f']
            self.shutdown_command = ['shutdown /t 10 /s /f']
        else:
            print('\033[91mConnection method not supported.\033[0m Exiting.')
            sys.exit(1)


    def get_command(self, args, outfile = False, errfile = False):
        if args == 'stop_iperf':
            cmd = self.stop_iperf
        else:
            cmd = self.iperf_cmd + args

        if outfile:
            if self.rem_loc == 'local':
                self.print_cmd = ' '.join(cmd)
            else:
                self.print_cmd = ' '.join(self.auth) + ' "' + ' '.join(cmd) + '"'

            err_redirect = ''

            if (errfile):
                err_redirect = ' 2> ' + errfile

            return self.print_cmd, ' > ' + outfile + err_redirect

        if self.rem_loc == 'local':
            return cmd
        else:
            return self.auth + [' '.join(cmd)]


    def shutdown(self):
        if self.rem_loc == 'remote':
            print('Shutting down the guest...')
            if Connect.conn_type == 'ssh':
                self.auth = self.auth[:-1] + ['-t'] + [self.auth[-1]]

            p = Popen(self.auth + self.shutdown_command)
            p.wait()
            sleep(10)
        else:
            print('\033[91mYou asked to shut down the host. It must be a mistake!\033[0m')


    def verify_credsfile(self):
        if not isfile(creds):
            print('\033[91mCredentials file "' + creds + '" not found.\033[0m Exiting.')
            sys.exit(1)

        Connect.conn_type = basename(access_method)
        if Connect.conn_type == 'ssh':
            with open(creds) as c:
                try:
                    credsline = c.readline().strip().split('=', maxsplit=1)
                    if credsline[0].strip() == 'username':
                        Connect.username = credsline[1].strip()
                    else:
                        raise

                    credsline = c.readline().strip().split('=', maxsplit=1)
                    if credsline[0].strip() == 'key':
                        Connect.key = credsline[1].strip()
                    else:
                        raise

                except:
                    print('\033[91mError: Please verify that the username and the key '
                          'are specified correctly in the creds file!\033[0m')
                    sys.exit(1)

            if not isfile(Connect.key):
                print('\033[93mSSH key file not found.\033[0m')
                create_key_trys = 4
                while create_key_trys:
                    ns = input('Create the keypair "' + Connect.key + '*" and transfer it to the guest? (Y/n) ')
                    if ns in ['', 'Y', 'y']:
                        p = Popen(['ssh-keygen', '-t', 'rsa', '-b', '4096', '-f',
                                   Connect.key, '-N', '', '-C',
                                   '"NetMeter_test-' + rundate + '"'])
                        p.wait()
                        p = Popen(['ssh-copy-id', '-i', Connect.key + '.pub', '-p',
                                   ssh_port, Connect.username + '@' + remote_addr])
                        p.wait()
                        print('OK')
                        break
                    elif ns in ['N', 'n']:
                        sys.exit(1)
                    else:
                        create_key_trys -= 1

                else:
                    sys.exit(1)


def time_header():
    return datetime.now().strftime('[ %H:%M:%S ] ')


def interrupt_exit(signal, frame):
    print('\n\033[91mInterrupted by user. Exiting.\033[0m')
    sys.exit(1)


def yes_and_no(y, n):
    if y and (not n):
        return 1
    else:
        return 0


def dir_prep(d):
    if not isdir(d):
        try:
            makedirs(d)
        except:
            print('The output directory (' + d + ') could not be created. Exiting.')
            sys.exit(1)

    print('The output directory is set to: \033[93m' + d + '\033[0m')


def cmd_print(text, rem_loc, dir_time):
    if isinstance(text, str):
        # The command is a string
        print_cmd = text
        # The last quoted string
        try:
            print_log = text.rsplit('"', 2)[1]
        except:
            print_log = text

    else:
        # The command is a list
        print_cmd = text[:]
        print_log = ' '.join(print_cmd)
        if basename(print_cmd[0]) == 'winexe' or basename(print_cmd[0]) == 'ssh':
            print_log = print_cmd[-1]
            # So that the passed command would be quoted, as it is actually passed this way.
            print_cmd[-1] = '"' + print_cmd[-1] + '"'

        print_cmd = ' '.join(print_cmd)

    with open(dir_time + '_iperf_commands.log', 'a') as logfile:
            logfile.write(time_header() + rem_loc[:3] + ': ' + print_log + '\n')

    if debug:
        print('####### Debug mode on #######\n' +
              'Command:\n' + print_cmd + '\n' +
              '#############################')


def place_images(direction, protocol, summary_img, image_list, print_unit, all_failed = False):
    if direction == 'h2g':
        from_dev = 'Host'
        to_dev = 'Guest'
    else:
        from_dev = 'Guest'
        to_dev = 'Host'

    content = (
               '    <div id=' + direction + '>\n'
               '        <h1>' + from_dev + ' &#8594; ' + to_dev + ' Results</h1>\n'
               '        <hr>\n'
               '        <h2>By ' + print_unit + ' Size</h2>\n'
               )
    if all_failed:
        content += (
                    '        <div id="missing"><div></br></br>'
                    '<h2>NOTICE: All tests failed to finish!</h2>'
                    '</br></br><h3>(See below...)</h3></div></div>\n'
                    )
    else:
        content += '        <img src="' + summary_img + '">\n'

    content += (
                '        <hr>\n'
                '        <h2>By Time</h2>\n'
                )
    for f in image_list:
        if f.split('.')[-1] == 'png':
            content += '        <img src="' + f + '">\n'
        else:
            content += (
                        '        <div id="missing"><div><h2>' + print_unit + ' size: '
                        + f +
                        '</h2><h3>(' + from_dev + ' to ' + to_dev + ', ' + protocol + ')</h3></br></br></br><h1>'
                        'Test failed to finish</h1></div></div>\n'
                        )

    content += '    </div>\n'
    return content


def gen_html(title, h2g_summary, g2h_summary, h2g_images, g2h_images, html_outname,
             protocol, streams, all_h2g_failed, all_g2h_failed, print_unit):
    content = (
               '<!doctype html>\n'
               '<html>\n'
               '<head>\n'
               '<meta charset="utf-8" />\n'
               '<style>\n'
               'body {\n'
               '    background-color: #eeffff;\n'
               '    font-family: Verdana, Helvetica, sans-serif;\n'
               '    height: 100%;\n'
               '    margin: 0px;\n'
               '    text-align: center;\n'
               '}\n'
               '#container {\n'
               '    width: 100%;\n'
               '    min-width: 800px;\n'
               '    height: 100%;\n'
               '}\n'
               '#header, #footer {\n'
               '    display: inline-block;\n'
               '    width: 100%;\n'
               '    min-width: 800px;\n'
               '    padding: 0.3em 0px;\n'
               '    background-color: #eeeeee;\n'
               '    background-image: url("' + logo + '");\n'
               '    background-repeat: no-repeat;\n'
               '    background-position: 10px 50%;\n'
               '}\n'
               '#h2g {\n'
               '    width: 50%;\n'
               '    float: left;\n'
               '    height: auto !important;\n'
               '    height: 100%;\n'
               '    min-height: 100%;\n'
               '}\n'
               '#g2h {\n'
               '    background-color: #ffffee;\n'
               '    width: 50%;\n'
               '    float: right;\n'
               '    height: auto !important;\n'
               '    height: 100%;\n'
               '    min-height: 100%;\n'
               '}\n'
               '#missing {\n'
               '    position: relative;\n'
               '    width: 90%;\n'
               '    max-width: 1024px;\n'
               '    padding-bottom: 67.5%;\n'
               '    margin: 5px auto;\n'
               '    background-color: #ffcccc;\n'
               '    z-index: 10;\n'
               '}\n'
               '#missing > div {\n'
               '    position: absolute;\n'
               '    width: 100%;\n'
               '    padding: 1em;\n'
               '    z-index: 20;\n'
               '}\n'
               'img {\n'
               '    max-width: 90%;\n'
               '    margin: 5px auto;\n'
               '    display: block;\n'
               '}\n'
               'h1 {\n'
               '    margin-bottom: 0px;\n'
               '}\n'
               'h3, p {\n'
               '    margin: 0px;\n'
               '}\n'
               '</style>\n'
               '<title>Iperf Host &#8596; Guest Bandwidth and CPU Usage Report</title>\n'
               '</head>\n'
               '<body>\n'
               '<div id="header">\n'
               )
    content += ('    <h3>' + title + ' [' + protocol + ', ' + str(streams) + ' st.]</h3>\n'
                '</div>\n'
                '<div id="container">\n'
               )
    content += place_images('h2g', protocol, h2g_summary, h2g_images, print_unit, all_h2g_failed)
    content += place_images('g2h', protocol, g2h_summary, g2h_images, print_unit, all_g2h_failed)
    content += (
                '</div>\n'
                '<div id="footer">\n'
                '    <p>&#169; Daynix Computing LTD</p>\n'
                '</div>\n'
                '</body>\n'
                '</html>\n'
                )
    with open(html_outname, 'w') as outfile:
        outfile.write(content)


def get_size_units_factor(num, rate=False):
    factor = 1.0
    if rate:
        s = 'b/s'
    else:
        s = 'B'

    for x in ['' + s, 'K' + s, 'M' + s, 'G' + s]:
        if num < 1024.0:
            return "%3.2f" % num, x, str(factor)

        num /= 1024.0
        factor *= 1024.0

    return "%3.2f" % num, 'T' + s, str(factor)


def get_round_size_name(i, gap = False):
    size_name = get_size_units_factor(i)
    if gap:
        return str(int(round(float(size_name[0])))) + ' ' + size_name[1]
    else:
        return str(int(round(float(size_name[0])))) + size_name[1]


def get_iperf_data_single(iperf_out, protocol, streams, repetitions):
    '''
    Notice: all entries are counted from the end, as sometimes the beginning of an
    output row can be unreadable. This is also the reason for "errors='ignore'".
    '''
    iperf_data = []
    additional_fields = 0
    if protocol == 'UDP':
        additional_fields = 5

    with open(iperf_out, encoding='utf-8', errors='ignore') as inputfile:
        for line in inputfile:
            tmp_lst = line.strip().split(',')
            if (
                not tmp_lst[0].isdigit()
                or len(tmp_lst) != (9 + additional_fields)
                or (additional_fields and float(tmp_lst[-3]) <= 0)
                or float(tmp_lst[-3 - additional_fields].split('-')[-1]) > repetitions * 10.0
               ):
                continue

            if (int(tmp_lst[-4 - additional_fields]) > 0):
                # If the link number is positive (i.e if it is not a summary, where it's -1)...
                date = datetime.strptime(tmp_lst[0], '%Y%m%d%H%M%S')
                if not iperf_data:
                    first_date = date

                time_from_start = float((date - first_date).total_seconds())
                rate = float(tmp_lst[-1 - additional_fields])
                if additional_fields:
                    # For UDP: rate = rate * (total_datagrams - lost_datagrams) / total_datagrams
                    rate = rate * (float(tmp_lst[-3]) - float(tmp_lst[-4])) / float(tmp_lst[-3])

                if (int(tmp_lst[-2 - additional_fields]) < 0) or (rate < 0.0):
                    rate = np.nan

                iperf_data.append([ time_from_start, int(tmp_lst[-4 - additional_fields]), rate ])

    if not iperf_data:
        raise ValueError('Nothing reached the server.')

    iperf_data = np.array(iperf_data)
    conns = np.unique(iperf_data[:,1])
    num_conn = conns.shape[0]
    if num_conn < streams:
        raise ValueError(str(num_conn) + ' out of ' + str(streams) + ' streams reached the server.')
    elif num_conn > streams:
        raise ValueError(str(num_conn) + ' connections reached the server (' + str(streams) + ' expected).')

    # Sort by connection number, then by date. Get indices of the result.
    bi_sorted_indices = np.lexsort((iperf_data[:,0], iperf_data[:,1]))
    iperf_data = iperf_data[bi_sorted_indices]
    ### Mechanism to check if too few or too many connections received
    # Get the index of the line after the last of each connection
    conn_ranges = np.searchsorted(iperf_data[:,1], conns, side='right')
    # Get sizes of connection blocks
    conn_count = np.diff(np.insert(conn_ranges, 0, 0))
    server_fault = False
    conn_reached = conn_count.min()
    if conn_reached < repetitions:
        # If there was at least one occasion when there were fewer connections than expected
        server_fault = 'too_few'
        repetitions = conn_reached

    # Get indices of connection block sizes that are bigger than expected (if any)
    where_extra_conn = (conn_count > repetitions).nonzero()[0]
    if where_extra_conn.size:
        ## If there were connection blocks bigger than expected
        # Get indices of lines after the last (n+1) for removal
        remove_before_lines = conn_ranges[where_extra_conn]
        # Get the amount of extra lines
        amount_lines_to_remove = [remove_before_lines[0] - repetitions * (where_extra_conn[0] + 1)]
        for i in where_extra_conn[1:]:
            amount_lines_to_remove.append(conn_ranges[i] - repetitions * (i + 1) - sum(amount_lines_to_remove))

        # Get the first lines to remove
        first_for_removal = remove_before_lines - amount_lines_to_remove
        # Get the ranges of lines to remove
        lines_to_remove = np.array([
                                    np.arange(first_for_removal[i],remove_before_lines[i])
                                    for i in np.arange(first_for_removal.size)
                                   ]).flatten()
        # Remove the extra lines
        iperf_data = np.delete(iperf_data, lines_to_remove, axis=0)
        if not server_fault:
            server_fault = 'too_many'

    ### End connection ammount check
    #print(str(num_conn) + str(iperf_data.shape))
    iperf_data = iperf_data[:,[0,2]].reshape((num_conn, iperf_data.shape[0]/num_conn, 2))
    iperf_data = np.ma.masked_array(iperf_data, np.isnan(iperf_data))
    #iperf_mean = np.mean(iperf_data, axis=0)
    mean_times = np.mean(iperf_data[:,:,0], axis=0)
    #iperf_min = np.amin(iperf_data[:,:,1], axis=0).reshape(-1, 1)
    #iperf_max = np.amax(iperf_data[:,:,1], axis=0).reshape(-1, 1)
    #iperf_mean[:,0] = np.rint(iperf_mean[:,0])
    iperf_stdev = np.std(iperf_data[:,:,1], axis=0) * np.sqrt(num_conn)
    #return np.hstack((iperf_mean,iperf_stdev)).filled(np.nan)
    out_arr = np.vstack((mean_times, iperf_data[:,:,1].sum(axis=0), iperf_stdev)).filled(np.nan).T
    return out_arr, out_arr[:,1].mean(), out_arr[:,1].std(), server_fault


def get_mpstat_data_single(mpstat_out):
    mpstat_data = []
    tmp_row = []
    time_interval = 0.0
    with open(mpstat_out) as inputfile:
        for line in inputfile:
            tmp_lst = line.split()
            if (not any('CPU' in s for s in tmp_lst)) and tmp_lst and ('Average' not in tmp_lst[0]):
                if any('all' in s for s in tmp_lst):
                    if tmp_row:
                        mpstat_data.append(tmp_row)

                    tmp_row = []
                else:
                    tmp_row.append(float(tmp_lst[-1]))

                if not time_interval:
                    time = datetime.strptime(tmp_lst[0] + tmp_lst[1], '%I:%M:%S%p')
                    if not mpstat_data:
                        first_time = time

                    time_interval = float((time - first_time).total_seconds())

    mpstat_data.append(tmp_row)
    mpstat_data = np.array(mpstat_data)
    num_measurements, num_cpu = mpstat_data.shape
    times = np.arange(0, num_measurements * time_interval, time_interval)
    mpstat_data = (1 - mpstat_data / 100) / num_cpu
    tot_cpu_usage = mpstat_data.sum(axis=1)
    core_stdev = np.std(mpstat_data, axis=1) * np.sqrt(num_cpu)
    #mpstat_mean = np.mean(mpstat_data, axis=1)
    #mpstat_min = np.min(mpstat_data, axis=1)
    #mpstat_max = np.max(mpstat_data, axis=1)
    out_arr = np.vstack((times, tot_cpu_usage, core_stdev)).T
    return out_arr, out_arr[:,1].mean(), out_arr[:,1].std()


def export_single_data(data_processed, data_outname):
    np.savetxt(data_outname, data_processed, fmt='%g', header='TimeStamp(s) Sum Stdev')


def plot_iperf_data(passed, plot_type, net_dat_file):
    '''
    Get different types of plots for the following cases:
    1. Single size plot.
    2. Multi size plot where all tests passed OK.
    3. Multi size plot where some tests had problems.
    4. Multi size plot where all tests had problems.
    ---
    passed - Numpy array, with 1 if a test went correctly, and 0 otherwise
    plot_type - 'singlesize' or 'multisize'
    net_dat_file - the file with PROCESSED Ipref data
    '''
    x_column_points = ['1', '2', '2', '2']
    x_column_areas = ['1', '($1 >= 0 ? $2 : 1/0)', '($1 >= 0 ? $2 : 1/0)',
                      '($1 >= 0 ? $2 : 1/0)']
    condition_statement = ['', '$1 >= 0 ? ', '$1 >= 0 ? ', '$1 == 0 ? ']
    BW_column = ['2', '3', '3', '3']
    if_not_condition = ['', ' : 1/0', ' : 1/0', ' : 1/0']
    xtic_explicit = ':xtic(printxsizes($2))'
    xtic = ['', xtic_explicit, xtic_explicit, xtic_explicit]
    point_color = ['blue', 'blue', 'blue', 'magenta']
    title = ['Mean tot. BW', 'Mean tot. BW', 'Mean tot. BW', 'Approx. BW']
    initial_points = (
                      '     "" using {0}:({1}${2}/rf{3}){4} with points'
                            ' pt 2 ps 1.5 lw 3 lc rgb "{5}" title "{6}", \\\n'
                     )
    for_all_points = [initial_points.format(x_column_points[i], condition_statement[i], BW_column[i], if_not_condition[i],
                                            xtic[i], point_color[i], title[i])
                      for i in [0, 1, 2, 3]]
    std_column = ['3', '4']
    initial_areas = (
                     '"' + net_dat_file + '" using {0}:(${1}/rf-${2}/rf):'
                     '(${1}/rf+${2}/rf) with filledcurves lc rgb "blue" notitle, \\\n'
                    )
    for_all_areas = [initial_areas.format(x_column_areas[i], BW_column[i], std_column[i])
                     for i in [0, 1]]
    if plot_type == 'singlesize':
        return for_all_areas[0] + for_all_points[0]
    elif passed.all():
        return for_all_areas[1] + for_all_points[1]
    elif passed[(passed >= 0).nonzero()].any():
        return for_all_areas[1] + for_all_points[2] + for_all_points[3]
    else:
        return for_all_areas[1] + for_all_points[3]


def write_gp(gp_outname, net_dat_file, proc_dat_file, img_file, net_rate, protocol, streams, print_unit,
             plot_type = 'singlesize', direction = 'h2g', finished = True,
             server_fault = False, packet_size = 0.0):
    try:
        net_rate, rate_units, rate_factor = get_size_units_factor(net_rate, rate=True)
        rate_format = ''
    except:
        net_rate = '???'
        rate_units = 'b/s'
        rate_factor = '1.0'
        rate_format = 'set format y "%.1tx10^%T"\n'

    packet_size = get_round_size_name(packet_size, gap = True)
    if plot_type == 'singlesize':
        plot_title = print_unit + ' size: ' + packet_size + ', Av. rate: ' + net_rate + ' ' + rate_units
        x_title = 'Time (s)'
        labels_above_points = ''
        failed_labels = ''
        stats_calc = ''
        log2_scale = ''
        rotate_xtics = ''
        formatx = ''
    else:
        plot_title = 'Bandwidth \\\\& CPU usage for different packet sizes'
        x_title = print_unit + ' size'
        labels_above_points = ('     "" using 2:($1 >= 0 ? $3/rf : 1/0)'
                               ':(sprintf("%.2f ' + rate_units + '", $3/rf))'
                               ' with labels offset 0.9,1.0 rotate by 90'
                               ' font ",12" notitle, \\\n')
        failed_labels = ('     "" using ($1 < 0 ? $2 : 1/0):(STATS_min/rf)'
                         ':(sprintf("Net test failed!"))'
                         ' with labels offset 0.9,2.5 rotate by 90'
                         ' tc rgb "red" font ",12" notitle, \\\n')
        stats_calc = 'stats "' + net_dat_file + '" using ($1 >= 0 ? $3 : 1/0) nooutput\n'
        log2_scale = 'set logscale x 2\n'
        rotate_xtics = 'set xtics rotate by -30\n'
        formatx = ('printxsizes(x) = x < 1024.0 ? sprintf("%.0fB", x) '
                   ': (x < 1048576.0 ? sprintf("%.0fKB", x/1024.0) '
                   ': sprintf("%.0fMB", x/1048576.0))\n')

    if direction == 'h2g':
        plot_subtitle = 'Host to Guest'
    else:
        plot_subtitle = 'Guest to Host'

    warning_message = ''
    if not finished:
        warning_message = 'set label "Warning:\\nTest failed to finish!\\nResults may not be accurate!" at screen 0.01, screen 0.96 tc rgb "red"\n'
    elif server_fault == 'too_few':
        warning_message = 'set label "Warning:\\nToo few connections!\\nResults may not be accurate!" at screen 0.01, screen 0.96 tc rgb "red"\n'
    elif server_fault == 'too_many':
        warning_message = 'set label "Warning:\\nToo many connections!\\nResults may not be accurate!" at screen 0.01, screen 0.96 tc rgb "red"\n'

    plot_net_data = plot_iperf_data(server_fault, plot_type, net_dat_file)
    content = (
               'set terminal pngcairo nocrop enhanced size 1024,768 font "Verdana,15"\n'
               'set output "' + img_file +'"\n'
               '\n'
               'set title "{/=20 ' + plot_title + '}\\n\\n{/=18 (' + plot_subtitle + ', ' + protocol + ', ' + str(streams) + ' st.)}"\n'
               + rate_format + warning_message +
               '\n'
               'set xlabel "' + x_title + '"\n'
               'set ylabel "Bandwidth (' + rate_units + ')"\n'
               'set ytics nomirror\n'
               'set y2label "CPU busy time fraction"\n'
               'set y2tics nomirror\n'
               'set y2range [0:1]\n'
               'set key bmargin center horizontal box samplen 1 width -1\n'
               'set bmargin 4.6\n'
               + rotate_xtics + formatx +
               '\n'
               'rf = ' + rate_factor + '  # rate factor\n'
               + stats_calc + log2_scale +
               'set style fill transparent solid 0.2 noborder\n'
               'set autoscale xfix\n'
               'plot ' + plot_net_data + labels_above_points + failed_labels +
               '     "' + proc_dat_file + '" using 1:($2-$3):($2+$3) with filledcurves lc rgb "red" axes x1y2 notitle, \\\n'
               '     "" using 1:2 with points pt 1 ps 1.5 lw 3 lc rgb "red" axes x1y2 title "Mean tot. CPU"\n'
              )
    with open(gp_outname, 'w') as outfile:
        outfile.write(content)


def set_protocol_opts(protocol, client = True):
    if protocol == 'TCP':
        return []
    elif protocol == 'UDP':
        if client:
            return ['-u', '-b', '1000000M']
        else:
            return ['-u']

    else:
        print('Protocol must be either "TCP" or "UDP". Exiting.')
        sys.exit(1)


def bend_max_size(size, protocol):
    if (protocol == 'UDP') and (size > 65507) and (size <= 65536):
        # Allow 2**16 (64KB) UDP tests to pass (ignore up to 29 bytes)
        return 65507
    elif (protocol == 'UDP') and (size > 65536):
        raise ValueError('Datagram size too big for UDP.')
    else:
        return size


def run_server(protocol, p_size, init_name, dir_time, rem_loc):
    p_size = bend_max_size(p_size, protocol)
    iperf_args = ['-s', '-i', '10', '-l', str(p_size), '-y', 'C']
    protocol_opts = set_protocol_opts(protocol, client = False)
    iperf_args += protocol_opts
    iperf_command, output = Connect(rem_loc).get_command(iperf_args, init_name + '_iperf.dat', init_name + '_iperf.err')
    print('Starting ' + rem_loc + ' server...')
    cmd_print(iperf_command, rem_loc, dir_time)
    p = Popen(iperf_command + output, shell=True)
    sleep(10)


def run_client(server_addr, runtime, p_size, streams, init_name, dir_time, protocol, rem_loc):
    p_size = bend_max_size(p_size, protocol)
    repetitions, mod = divmod(runtime, 10)
    if not mod:
        runtime += 1

    iperf_args =  ['-c', server_addr, '-t', str(runtime), '-l', str(p_size),
                   '-P', str(streams)]
    protocol_opts = set_protocol_opts(protocol)
    iperf_args += protocol_opts
    iperf_command, output = Connect(rem_loc).get_command(iperf_args, init_name + '_iperf_client.out', init_name + '_iperf_client.err')
    direction_message = 'host to guest' if rem_loc == 'local' else 'guest to host'
    size_name = get_round_size_name(p_size)
    print(time_header() + 'Running ' + size_name + ' ' + direction_message + ' test. (Duration: '
          + str(timedelta(seconds = repetitions * 10 + mod)) + ')')
    cmd_print(iperf_command, rem_loc, dir_time)
    iperf_proc = Popen(iperf_command + output, shell=True)
    mpstat_proc = Popen('mpstat -P ALL 10 ' + str(repetitions) + ' > ' + init_name + '_mpstat.dat', shell=True)
    mpstat_proc.wait()
    sleep(2)
    waitcount = 1  # Positive integer. Number of 10 sec intervals to wait for the client to finish.
    while iperf_proc.poll() == None:
        # iperf_proc.poll() may be "False" or "None". Here we want "None" specifically, thus "not iperf_proc.poll()" won't work.
        if waitcount:
            print(time_header() + '\033[93mThe Iperf test is not over yet.\033[0m Waiting for 10 more seconds...')
            sleep(10)
            waitcount -= 1
        else:
            iperf_proc.kill()
            sleep(2)

    if not iperf_proc.poll():
        print(time_header() + '\033[92mThe ' + size_name + ' test finished.\033[0m Waiting for 10 seconds.')
        sleep(10)
        return True, repetitions
    else:
        print(time_header() + '\033[91mThe Iperf test failed to finish.\033[0m Skipping in 10 seconds.')
        sleep(10)
        return False, repetitions


def stop_server(rem_loc, dir_time):
    iperf_stop_command = Connect(rem_loc).get_command('stop_iperf')
    print('Stopping previous ' + rem_loc  + ' Iperf instances...')
    cmd_print(iperf_stop_command, rem_loc, dir_time)
    p = Popen(iperf_stop_command, stdout=PIPE, stderr=PIPE)
    p.wait()
    out, err = p.communicate()
    if 'found' in str(err):
        print('None were running.')
        return
    elif (out or err):
        print(((out + err).strip()).decode('ascii', errors='ignore'))

    sleep(10)


def run_tests(remote_addr, local_addr, runtime, p_sizes, streams, timestamp,
              test_title, protocol, export_dir):
    series_time = str(timedelta(seconds = 2 * len(p_sizes) * (runtime + 30) + 20))
    print(time_header() + '\033[92mStarting ' + protocol + ' tests.\033[0m Expected run time: ' + series_time)
    top_dir_name = timestamp + '_' + protocol + '_' + str(streams) + '_st'
    common_filename = protocol + '_' + str(streams) + '_st_' + timestamp
    print_unit = 'Buffer' if protocol == 'TCP' else 'Datagram'
    raw_data_subdir="raw-data"
    dir_prep(join(export_dir, top_dir_name, raw_data_subdir))
    dir_time = join(export_dir, top_dir_name, raw_data_subdir, common_filename)
    html_name = join(export_dir, top_dir_name, common_filename + ".html")
    h2g_images = []
    g2h_images = []
    all_h2g_failed = False
    all_g2h_failed = False
    stop_server('local', dir_time)
    stop_server('remote', dir_time)
    for direction in ['h2g', 'g2h']:
        if direction == 'h2g':
            server_addr = remote_addr
            server_loc = 'remote'
            client_loc = 'local'
            image_list = h2g_images
            plot_message = 'Plotting host --> guest summary...'
        else:
            server_addr = local_addr
            server_loc = 'local'
            client_loc = 'remote'
            image_list = g2h_images
            plot_message = 'Plotting guest --> host summary...'

        tot_iperf_mean = -1.0
        iperf_tot = []
        mpstat_tot = []
        for p in p_sizes:
            size_name = get_round_size_name(p)
            init_name = dir_time + '_' + direction + '_' + size_name
            iperf_sumname = dir_time + '_' + direction + '_iperf_summary'
            mpstat_sumname = dir_time + '_' + direction + '_mpstat_summary'
            combined_sumname = dir_time + '_' + direction + '_summary'
            try:
                print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
                run_server(protocol, p, init_name, dir_time, server_loc)
                test_completed, repetitions = run_client(server_addr, runtime, p, streams,
                                                         init_name, dir_time, protocol,
                                                         client_loc)
                stop_server(server_loc, dir_time)
                print('Parsing results...')
                mpstat_array, tot_mpstat_mean, tot_mpstat_stdev = get_mpstat_data_single(init_name + '_mpstat.dat')
                mpstat_tot.append([ p, tot_mpstat_mean, tot_mpstat_stdev ])
                (iperf_array, tot_iperf_mean, tot_iperf_stdev, server_fault) =\
                get_iperf_data_single(init_name + '_iperf.dat', protocol, streams, repetitions)
                if server_fault == 'too_few':
                    print('\033[93mWARNING:\033[0m The server received fewer connections than expected.')
                elif server_fault == 'too_many':
                    print('\033[93mWARNING:\033[0m The server received more connections than expected.')

                # Get the "humanly readable" rate and its units.
                # This is just to put in the output data file, not for any calculations.
                # The units will be constant, and will be fixed after the first measurement.
                try:
                    hr_net_rate = tot_iperf_mean / float(rate_factor)
                except:
                    _, rate_units, rate_factor = get_size_units_factor(tot_iperf_mean, rate=True)
                    hr_net_rate = tot_iperf_mean / float(rate_factor)

                export_single_data(iperf_array, init_name + '_iperf_processed.dat')
                export_single_data(mpstat_array, init_name + '_mpstat_processed.dat')
                write_gp(init_name + '.plt', basename(init_name + '_iperf_processed.dat'),
                         basename(init_name + '_mpstat_processed.dat'), basename(init_name + '.png'),
                         tot_iperf_mean, protocol, streams, print_unit, plot_type = 'singlesize', direction = direction,
                         finished = test_completed, server_fault = server_fault, packet_size = p)
                print('Plotting...')
                pr = Popen([gnuplot_bin, basename(init_name + '.plt')], cwd=dirname(dir_time))
                pr.wait()
                image_list.append(join(raw_data_subdir, basename(init_name + '.png')))
                iperf_tot.append([ yes_and_no(test_completed, server_fault), p, tot_iperf_mean,
                                  tot_iperf_stdev, hr_net_rate ])
                print('============================================================')
            except ValueError as err:
                print(time_header() + '\033[91mERROR:\033[0m ' + err.args[0] + ' Skipping test...')
                image_list.append(get_round_size_name(p, gap = True))
                iperf_tot.append([ -1, p, 0, 0, 0 ])
                print('============================================================')

        if tot_iperf_mean > 0.0:
            print(plot_message)
            np.savetxt(iperf_sumname + '.dat', iperf_tot, fmt='%g',
                       header= 'TestOK ' + print_unit + 'Size(B) BW(b/s) Stdev(b/s) BW(' + rate_units + ')')
            np.savetxt(mpstat_sumname + '.dat', mpstat_tot, fmt='%g', header= print_unit + 'Size(B) Frac Stdev')
            non_failed_BW = [l[2] for l in iperf_tot if l[2]]
            tot_iperf_mean = sum(non_failed_BW)/len(non_failed_BW)
            write_gp(combined_sumname + '.plt', basename(iperf_sumname + '.dat'),
                     basename(mpstat_sumname + '.dat'), basename(combined_sumname + '.png'),
                     tot_iperf_mean, protocol, streams, print_unit, plot_type = 'multisize', direction = direction,
                     server_fault = np.array(iperf_tot)[:,0], packet_size = np.mean(p_sizes))
            pr = Popen([gnuplot_bin, basename(combined_sumname + '.plt')], cwd=dirname(dir_time))
            pr.wait()
        elif direction == 'h2g':
            all_h2g_failed = True
        else:
            all_g2h_failed = True

    print('Exporting html...')
    gen_html(test_title,
             join(raw_data_subdir, common_filename + '_h2g_summary.png'),
             join(raw_data_subdir, common_filename + '_g2h_summary.png'),
             h2g_images, g2h_images, html_name, protocol, streams,
             all_h2g_failed, all_g2h_failed, print_unit)


def run_tests_for_protocols(remote_addr, local_addr, runtime, p_sizes, streams,
                            timestamp, test_title, protocols, export_dir):
    for p in protocols:
        run_tests(remote_addr, local_addr, runtime, p_sizes,
                  streams, timestamp, test_title, p, export_dir)


def run_tests_for_streams(remote_addr, local_addr, runtime, p_sizes, streams,
                          timestamp, test_title, protocols, export_dir):
    for s in streams:
        if str(s).isdigit():
            run_tests_for_protocols(remote_addr, local_addr, runtime, p_sizes, s,
                                    timestamp, test_title, protocols, export_dir)
        else:
            print('\033[91mERROR:\033[0m Can not test for ' + s +
                  ' streams. Please verify that the number of streams is a positive integer.')
            sys.exit(1)


if __name__ == "__main__":
    # Interrupt handling
    signal.signal(signal.SIGINT, interrupt_exit)
    # Verifying credsfile existence
    Connect('remote')
    # Write message
    if (len(protocols) > 1) or (len(streams) > 1):
        total_time = str(timedelta(seconds = (2 * len(test_range) * (run_duration + 32) + 20) *
                         len(protocols) * len(streams)))
        print(time_header() + '\033[92mStarting tests for protocols: ' + ', '.join(protocols) + '.\033[0m')
        print(time_header() + '\033[92mUsing ' + ','.join(str(s) for s in streams) + ' stream(s).\033[0m')
        print(time_header() + '\033[92mExpected total run time: \033[0m' + '\033[91m' + total_time + '\033[0m')

    # Run tests
    run_tests_for_streams(remote_addr, local_addr, run_duration, test_range,
                          streams, rundate, title, protocols, export_dir)
    # Shut down the guest if needed
    if shutdown:
        Connect('remote').shutdown()
