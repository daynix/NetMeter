#!/usr/bin/env python3
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

# Import configuration
from NetMeterConfig import *

rundate = datetime.now().strftime('%Y_%m_%d_%H-%M-%S')
logo = (
        'data:image/png;base64,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'
        'SUVORK5CYII='
       )


class Connect(object):
    def __init__(self, access_method, ip, conn_name, iperf_bin, ssh_port = 22,
                 creds = None):
        self.conn_type = basename(access_method)
        self.conn_name = conn_name
        self.creds = creds
        self.ip = ip
        self.ssh_port = ssh_port
        self.verify_credsfile()
        self.iperf_cmd = [iperf_bin]
        if self.conn_type == 'local':
            self.stop_iperf = ['killall', '-9', basename(iperf_bin)]
        elif self.conn_type == 'ssh':
            self.auth = [access_method, '-i', self.key, '-p', str(ssh_port), '-l', self.username,
                         '-o', 'UserKnownHostsFile=/dev/null', '-o', 'StrictHostKeyChecking=no',
                         '-o', 'BatchMode=yes', '-o', 'LogLevel=ERROR', ip]
            self.stop_iperf = ['killall', '-9', basename(iperf_bin)]
            self.shutdown_command = ['sudo', 'shutdown', '-h', 'now']
        elif self.conn_type == 'winexe':
            self.auth = [access_method, '-A',  self.creds, '//' + ip]
            self.stop_iperf = ['taskkill /im ' + basename(iperf_bin) + ' /f']
            self.shutdown_command = ['shutdown /t 10 /s /f']
        else:
            print('\033[91mConnection method not supported.\033[0m Exiting.')
            sys.exit(1)

    def islocal(self):
        if self.conn_type == 'local':
            return True
        else:
            return False

    def getname(self):
        return self.conn_name

    def get_command(self, args, outfile = None, errfile = None):
        if args == 'stop_iperf':
            cmd = self.stop_iperf
        else:
            cmd = self.iperf_cmd + args

        if outfile:
            if self.conn_type == 'local':
                self.print_cmd = ' '.join(cmd)
            else:
                self.print_cmd = ' '.join(self.auth) + ' "' + ' '.join(cmd) + '"'

            err_redirect = ''

            if (errfile):
                err_redirect = ' 2> ' + errfile

            return self.print_cmd, ' > ' + outfile + err_redirect

        if self.conn_type == 'local':
            return cmd
        else:
            return self.auth + [' '.join(cmd)]

    def shutdown(self):
        if self.conn_type != 'local':
            print('Shutting down ' + self.conn_name + '...')
            if self.conn_type == 'ssh':
                self.auth = self.auth[:-1] + ['-t'] + [self.auth[-1]]

            p = Popen(self.auth + self.shutdown_command)
            p.wait()
            sleep(10)

    def verify_credsfile(self):
        if self.conn_type != 'local' and (not isfile(self.creds)):
            print('\033[91mCredentials file "' + self.creds + '" not found.\033[0m Exiting.')
            sys.exit(1)

        if self.conn_type == 'ssh':
            with open(self.creds) as c:
                try:
                    credsline = c.readline().strip().split('=', maxsplit=1)
                    if credsline[0].strip() == 'username':
                        self.username = credsline[1].strip()
                    else:
                        raise

                    credsline = c.readline().strip().split('=', maxsplit=1)
                    if credsline[0].strip() == 'key':
                        self.key = credsline[1].strip()
                    else:
                        raise

                except:
                    print('\033[91mError: Please verify that the username and the key '
                          'are specified correctly in ' + self.creds +'!\033[0m')
                    sys.exit(1)

            if not isfile(self.key):
                print('\033[93mSSH key file not found.\033[0m')
                create_key_trys = 4
                while create_key_trys:
                    ns = input('Create the keypair "' + self.key + '{,.pub}" and transfer it to ' + self.conn_name + '? (Y/n) ')
                    if ns in ['', 'Y', 'y']:
                        p = Popen(['ssh-keygen', '-t', 'rsa', '-b', '4096', '-f',
                                   self.key, '-N', '', '-C',
                                   '"NetMeter_test-' + rundate + '"'])
                        p.wait()
                        p = Popen(['ssh-copy-id', '-i', self.key + '.pub', '-p',
                                   str(self.ssh_port), self.username + '@' + self.ip])
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


def tprint(str):
    print(time_header() + str)


def interrupt_exit(signal, frame):
    print('\n\033[91mInterrupted by user. Exiting.\033[0m')
    sys.exit(1)


def yes_and_no(y, n):
    if y and (not n):
        return 1
    else:
        return 0


def gen_tcp_win_msg(tcpwin):
    if tcpwin:
        return ', w=' + str(tcpwin)
    else:
        return ''


def dir_prep(dir, subdir):
    data_path = join(dir, subdir)
    if not isdir(data_path):
        try:
            makedirs(data_path)
        except:
            print('The output directory (' + data_path +
                  ') can not be created. Exiting.')
            sys.exit(1)

    print('The output directory is set to: \033[93m' + dir + '\033[0m')


def cmd_print(text, conn_name, dir_time):
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
            logfile.write(time_header() + conn_name + ': ' + print_log + '\n')

    if debug:
        print('####### Debug mode on #######\n' +
              'Command:\n' + print_cmd + '\n' +
              '#############################')


def place_images(direction, protocol, summary_img, image_list, print_unit,
                 cl1_pretty_name, cl2_pretty_name, all_failed = False):
    if direction == 'one2two':
        from_dev = cl1_pretty_name
        to_dev = cl2_pretty_name
    else:
        from_dev = cl2_pretty_name
        to_dev = cl1_pretty_name

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


def gen_html(title, one2two_summary, two2one_summary, one2two_images, two2one_images, html_outname,
             protocol, streams, all_one2two_failed, all_two2one_failed, print_unit, localpart,
             cl1_pretty_name, cl2_pretty_name, tcpwin):
    if localpart:
        CPU_note = 'and CPU '
    else:
        CPU_note = ''

    tcp_win_msg = gen_tcp_win_msg(tcpwin)
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
               '#one2two {\n'
               '    width: 50%;\n'
               '    float: left;\n'
               '    height: auto !important;\n'
               '    height: 100%;\n'
               '    min-height: 100%;\n'
               '}\n'
               '#two2one {\n'
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
               '<title>Iperf ' + cl1_pretty_name + ' &#8596; ' + cl2_pretty_name
               + ' Bandwidth ' + CPU_note + 'Performance Report</title>\n'
               '</head>\n'
               '<body>\n'
               '<div id="header">\n'
               )
    content += ('    <h3>' + title + ' [' + protocol + ', ' + str(streams) + ' st.' + tcp_win_msg + ']</h3>\n'
                '</div>\n'
                '<div id="container">\n'
               )
    content += place_images('one2two', protocol, one2two_summary, one2two_images,
                            print_unit, cl1_pretty_name, cl2_pretty_name,
                            all_one2two_failed)
    content += place_images('two2one', protocol, two2one_summary, two2one_images,
                            print_unit, cl1_pretty_name, cl2_pretty_name,
                            all_two2one_failed)
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
        thousand = 1000.0
    else:
        s = 'B'
        thousand = 1024.0

    for x in ['' + s, 'K' + s, 'M' + s, 'G' + s]:
        if num < thousand:
            return "%3.2f" % num, x, str(factor)

        num /= thousand
        factor *= thousand

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
        lines_to_remove = np.hstack(
                                    np.array([
                                              np.arange(first_for_removal[i],remove_before_lines[i])
                                              for i in np.arange(first_for_removal.size)
                                             ], dtype=object)
                                   ).astype(int)
        # Remove the extra lines
        iperf_data = np.delete(iperf_data, lines_to_remove, axis=0)
        if not server_fault:
            server_fault = 'too_many'

    ### End connection ammount check
    iperf_data = iperf_data[:,[0,2]].reshape((num_conn, iperf_data.shape[0]//num_conn, 2))
    iperf_data = np.ma.masked_array(iperf_data, np.isnan(iperf_data))
    mean_times = np.mean(iperf_data[:,:,0], axis=0)
    iperf_stdev = np.std(iperf_data[:,:,1], axis=0) * np.sqrt(num_conn)
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
                    try:
                        time = datetime.strptime(tmp_lst[0] + tmp_lst[1], '%I:%M:%S%p')
                    except ValueError:
                        time = datetime.strptime(tmp_lst[0], '%H:%M:%S')

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


def write_gp(gp_outname, net_dat_file, proc_dat_file, img_file, net_rate,
             protocol, streams, print_unit, cl1_pretty_name, cl2_pretty_name,
             plot_type = 'singlesize', direction = 'one2two', finished = True,
             server_fault = False, packet_size = 0.0, tcpwin = None):
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

    if direction == 'one2two':
        plot_subtitle = cl1_pretty_name + ' to ' + cl2_pretty_name
    else:
        plot_subtitle = cl2_pretty_name + ' to ' + cl1_pretty_name

    if proc_dat_file:
        proc_plot = ('     "' + proc_dat_file + '" using 1:($2-$3):($2+$3) with filledcurves lc rgb "red" axes x1y2 notitle, \\\n'
                     '     "" using 1:2 with points pt 1 ps 1.5 lw 3 lc rgb "red" axes x1y2 title "Mean tot. CPU"\n')
        y2_axis = ('set y2label "CPU busy time fraction"\n'
                   'set y2tics nomirror\n'
                   'set y2range [0:1]\n')
        rmargin = ''
    else:
        proc_plot = ''
        y2_axis = ''
        rmargin = 'set rmargin 4.5\n'

    tcp_win_msg = gen_tcp_win_msg(tcpwin)
    warning_message = ''
    if not finished:
        warning_message = 'set label "Warning:\\nTest failed to finish!\\nResults may not be accurate!" at screen 0.01, screen 0.96 tc rgb "red"\n'
    elif isinstance(server_fault, str) and server_fault == 'too_few':
        warning_message = 'set label "Warning:\\nToo few connections!\\nResults may not be accurate!" at screen 0.01, screen 0.96 tc rgb "red"\n'
    elif isinstance(server_fault, str) and server_fault == 'too_many':
        warning_message = 'set label "Warning:\\nToo many connections!\\nResults may not be accurate!" at screen 0.01, screen 0.96 tc rgb "red"\n'

    plot_net_data = plot_iperf_data(server_fault, plot_type, net_dat_file)
    content = (
               'set terminal pngcairo nocrop enhanced size 1024,768 font "Verdana,15"\n'
               'set output "' + img_file + '"\n'
               '\n'
               'set title "{/=20 ' + plot_title + '}\\n\\n{/=18 (' + plot_subtitle + ', ' + protocol + ', ' + str(streams) + ' st.' + tcp_win_msg + ')}"\n'
               + rate_format + warning_message +
               '\n'
               'set xlabel "' + x_title + '"\n'
               'set ylabel "Bandwidth (' + rate_units + ')"\n'
               'set ytics nomirror\n'
               + y2_axis +
               'set key bmargin center horizontal box samplen 1 width -1\n'
               'set bmargin 4.6\n' + rmargin
               + rotate_xtics + formatx +
               '\n'
               'rf = ' + rate_factor + '  # rate factor\n'
               + stats_calc + log2_scale +
               'set style fill transparent solid 0.2 noborder\n'
               'set autoscale xfix\n'
               'plot ' + plot_net_data + labels_above_points + failed_labels + proc_plot
              )
    with open(gp_outname, 'w') as outfile:
        outfile.write(content)


def set_protocol_opts(protocol, tcpwin, client = True):
    if protocol == 'TCP' and tcpwin:
        return ['-w', str(tcpwin)]
    elif protocol == 'TCP':
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


def run_server(protocol, init_name, dir_time, conn, tcpwin):
    iperf_args = ['-s', '-i', '10', '-y', 'C']
    protocol_opts = set_protocol_opts(protocol, tcpwin, client = False)
    iperf_args += protocol_opts
    conn_name = conn.getname()
    iperf_command, output = conn.get_command(iperf_args, init_name + '_iperf.dat', init_name + '_iperf.err')
    print('Starting server on ' + conn_name + '...')
    cmd_print(iperf_command, conn_name, dir_time)
    p = Popen(iperf_command + output, shell=True)
    sleep(10)


def run_client(server_addr, runtime, p_size, streams, init_name, dir_time,
               protocol, conn, localpart, tcpwin):
    p_size = bend_max_size(p_size, protocol)
    repetitions, mod = divmod(runtime, 10)
    if not mod:
        runtime += 1

    iperf_args =  ['-c', server_addr, '-t', str(runtime), '-l', str(p_size),
                   '-P', str(streams)]
    protocol_opts = set_protocol_opts(protocol, tcpwin)
    iperf_args += protocol_opts
    iperf_command, output = conn.get_command(iperf_args, init_name + '_iperf_client.out', init_name + '_iperf_client.err')
    source_name = conn.getname()
    size_name = get_round_size_name(p_size)
    tprint('Running ' + size_name + ' test from ' + source_name + '. (Duration: '
          + str(timedelta(seconds = repetitions * 10 + mod)) + ')')
    conn_name = conn.getname()
    cmd_print(iperf_command, conn_name, dir_time)
    iperf_proc = Popen(iperf_command + output, shell=True)
    if localpart:
        mpstat_proc = Popen('mpstat -P ALL 10 ' + str(repetitions) + ' > ' + init_name + '_mpstat.dat', shell=True)
        mpstat_proc.wait()
    else:
        sleep(10 * repetitions)

    sleep(2)
    waitcount = 1  # Positive integer. Number of 10 sec intervals to wait for the client to finish.
    while iperf_proc.poll() == None:
        # iperf_proc.poll() may be "False" or "None". Here we want "None" specifically, thus "not iperf_proc.poll()" won't work.
        if waitcount:
            tprint('\033[93mThe Iperf test is not over yet.\033[0m Waiting for 10 more seconds...')
            sleep(10)
            waitcount -= 1
        else:
            iperf_proc.kill()
            sleep(2)

    if not iperf_proc.poll():
        tprint('\033[92mThe ' + size_name + ' test finished.\033[0m Waiting for 10 seconds.')
        sleep(10)
        return True, repetitions
    else:
        tprint('\033[91mThe Iperf test failed to finish.\033[0m Skipping in 10 seconds.')
        sleep(10)
        return False, repetitions


def stop_server(conn, dir_time):
    conn_name = conn.getname()
    iperf_stop_command = conn.get_command('stop_iperf')
    print('Stopping previous Iperf instances on ' + conn_name + '...')
    cmd_print(iperf_stop_command, conn_name, dir_time)
    p = Popen(iperf_stop_command, stdout=PIPE, stderr=PIPE)
    p.wait()
    out, err = p.communicate()
    if 'found' in str(err):
        print('None were running.')
        return
    elif (out or err):
        print(((out + err).strip()).decode('ascii', errors='ignore'))

    sleep(10)


def run_tests(cl1_conn, cl2_conn, cl1_test_ip, cl2_test_ip, runtime, p_sizes,
              streams, timestamp, test_title, protocol, tcpwin, export_dir):
    series_time = str(timedelta(seconds = 2 * len(p_sizes) * (runtime + 30) + 20))
    tprint('\033[92mStarting ' + protocol + ' tests.\033[0m Expected run time: ' + series_time)
    top_dir_name = timestamp + '_' + protocol + '_' + str(streams) + '_st'
    common_filename = protocol + '_' + str(streams) + '_st_' + timestamp
    print_unit = 'Buffer' if protocol == 'TCP' else 'Datagram'
    raw_data_subdir="raw-data"
    dir_prep(join(export_dir, top_dir_name), raw_data_subdir)
    dir_time = join(export_dir, top_dir_name, raw_data_subdir, common_filename)
    html_name = join(export_dir, top_dir_name, common_filename + ".html")
    one2two_images = []
    two2one_images = []
    all_one2two_failed = False
    all_two2one_failed = False
    stop_server(cl1_conn, dir_time)
    stop_server(cl2_conn, dir_time)
    if cl1_conn.islocal() or cl2_conn.islocal():
        localpart = True
    else:
        localpart = False

    connlist = [
                [cl1_conn, cl2_conn, 'one2two', cl2_test_ip, one2two_images, 'Plotting cl1 --> cl2 summary...'],
                [cl2_conn, cl1_conn, 'two2one', cl1_test_ip, two2one_images, 'Plotting cl2 --> cl1 summary...']
               ]
    for c in connlist:
        [client_conn, server_conn, direction, server_addr, image_list, plot_message] = c
        tot_iperf_mean = -1.0
        iperf_tot = []
        mpstat_tot = []
        for p in p_sizes:
            size_name = format(p, '05d') + 'B'
            init_name = dir_time + '_' + direction + '_' + size_name
            iperf_sumname = dir_time + '_' + direction + '_iperf_summary'
            mpstat_sumname = dir_time + '_' + direction + '_mpstat_summary'
            combined_sumname = dir_time + '_' + direction + '_summary'
            print('++++++++++++++++++++++++++++++++++++++++++++++++++')
            try:
                run_server(protocol, init_name, dir_time, server_conn, tcpwin)
                test_completed, repetitions = run_client(server_addr, runtime, p, streams,
                                                         init_name, dir_time, protocol,
                                                         client_conn, localpart, tcpwin)
                stop_server(server_conn, dir_time)
                print('Parsing results...')
                if localpart:
                    mpstat_array, tot_mpstat_mean, tot_mpstat_stdev = get_mpstat_data_single(init_name + '_mpstat.dat')
                    mpstat_tot.append([ p, tot_mpstat_mean, tot_mpstat_stdev ])
                    export_single_data(mpstat_array, init_name + '_mpstat_processed.dat')
                    mpstat_single_file = basename(init_name + '_mpstat_processed.dat')
                else:
                    mpstat_single_file = None

                (iperf_array, tot_iperf_mean, tot_iperf_stdev, server_fault) =\
                get_iperf_data_single(init_name + '_iperf.dat', protocol, streams, repetitions)
                if server_fault == 'too_few':
                    print('\033[93mWARNING:\033[0m The server received fewer connections than expected.')
                elif server_fault == 'too_many':
                    print('\033[93mWARNING:\033[0m The server received more connections than expected.')

            except ValueError as err:
                tprint('\033[91mERROR:\033[0m ' + err.args[0] + ' Skipping test...')
                image_list.append(get_round_size_name(p, gap = True))
                iperf_tot.append([ -1, p, 0, 0, 0 ])
                print('==================================================')
                continue

            # Get the "humanly readable" rate and its units.
            # This is just to put in the output data file, not for any calculations.
            # The units will be constant, and will be fixed after the first measurement.
            try:
                hr_net_rate = tot_iperf_mean / float(rate_factor)
            except:
                _, rate_units, rate_factor = get_size_units_factor(tot_iperf_mean, rate=True)
                hr_net_rate = tot_iperf_mean / float(rate_factor)

            export_single_data(iperf_array, init_name + '_iperf_processed.dat')
            write_gp(init_name + '.plt', basename(init_name + '_iperf_processed.dat'),
                     mpstat_single_file, basename(init_name + '.png'),
                     tot_iperf_mean, protocol, streams, print_unit, cl1_pretty_name,
                     cl2_pretty_name, plot_type = 'singlesize', direction = direction,
                     finished = test_completed, server_fault = server_fault,
                     packet_size = p, tcpwin = tcpwin)
            print('Plotting...')
            pr = Popen([gnuplot_bin, basename(init_name + '.plt')],
                       cwd = dirname(dir_time))
            pr.wait()
            image_list.append(join(raw_data_subdir, basename(init_name + '.png')))
            iperf_tot.append([ yes_and_no(test_completed, server_fault), p,
                              tot_iperf_mean, tot_iperf_stdev, hr_net_rate ])
            print('==================================================')

        if tot_iperf_mean > 0.0:
            print(plot_message)
            np.savetxt(iperf_sumname + '.dat', iperf_tot, fmt='%g',
                       header= ('TestOK ' + print_unit +
                                'Size(B) BW(b/s) Stdev(b/s) BW(' +
                                rate_units + ')'))

            if localpart:
                np.savetxt(mpstat_sumname + '.dat', mpstat_tot, fmt = '%g',
                           header = print_unit + 'Size(B) Frac Stdev')
                mpstat_ser_file = basename(mpstat_sumname + '.dat')
            else:
                mpstat_ser_file = None

            non_failed_BW = [l[2] for l in iperf_tot if l[2]]
            tot_iperf_mean = sum(non_failed_BW)/len(non_failed_BW)
            write_gp(combined_sumname + '.plt', basename(iperf_sumname + '.dat'),
                     mpstat_ser_file, basename(combined_sumname + '.png'),
                     tot_iperf_mean, protocol, streams, print_unit, cl1_pretty_name,
                     cl2_pretty_name, plot_type = 'multisize', direction = direction,
                     server_fault = np.array(iperf_tot)[:,0], packet_size = np.mean(p_sizes),
                     tcpwin = tcpwin)
            pr = Popen([gnuplot_bin, basename(combined_sumname + '.plt')], cwd=dirname(dir_time))
            pr.wait()
        elif direction == 'one2two':
            all_one2two_failed = True
        else:
            all_two2one_failed = True

    print('Exporting html...')
    gen_html(test_title,
             join(raw_data_subdir, common_filename + '_one2two_summary.png'),
             join(raw_data_subdir, common_filename + '_two2one_summary.png'),
             one2two_images, two2one_images, html_name, protocol, streams,
             all_one2two_failed, all_two2one_failed, print_unit, localpart,
             cl1_pretty_name, cl2_pretty_name, tcpwin)


class Multitest(object):
    def __init__(self, cl1_conn, cl2_conn, cl1_test_ip, cl2_test_ip, runtime,
                 p_sizes, timestamp, test_title, tcpwin, export_dir):
        self.cl1_conn    = cl1_conn
        self.cl2_conn    = cl2_conn
        self.cl1_test_ip = cl1_test_ip
        self.cl2_test_ip = cl2_test_ip
        self.runtime     = runtime
        self.p_sizes     = p_sizes
        self.timestamp   = timestamp
        self.test_title  = test_title
        self.tcpwin      = tcpwin
        self.export_dir  = export_dir

    def run_tests_for_protocols(self, streams, proto_list):
        for p in proto_list:
            run_tests(self.cl1_conn, self.cl2_conn, self.cl1_test_ip,
                      self.cl2_test_ip, self.runtime, self.p_sizes, streams,
                      self.timestamp, self.test_title, p, self.tcpwin,
                      self.export_dir)

    def run_tests_for_streams(self, stream_list, proto_list):
        for s in stream_list:
            if str(s).isdigit():
                self.run_tests_for_protocols(s, proto_list)
            else:
                print('\033[91mERROR:\033[0m Can not test for ' + s +
                      ' streams. Please verify that the number of streams'
                      ' is a positive integer.')
                sys.exit(1)


if __name__ == "__main__":
    # Interrupt handling
    signal.signal(signal.SIGINT, interrupt_exit)
    # Getting connections
    cl1_conn = Connect(access_method_cl1, cl1_conn_ip, 'cl1', cl1_iperf, ssh_port_cl1, creds_cl1)
    cl2_conn = Connect(access_method_cl2, cl2_conn_ip, 'cl2', cl2_iperf, ssh_port_cl2, creds_cl2)
    # Write message
    if (len(protocols) > 1) or (len(streams) > 1):
        total_time = str(timedelta(seconds = (2 * len(test_range) * (run_duration + 32) + 20) *
                         len(protocols) * len(streams)))
        tprint('\033[92mStarting tests for protocols: ' + ', '.join(protocols) + '.\033[0m')
        tprint('\033[92mUsing ' + ','.join(str(s) for s in streams) + ' stream(s).\033[0m')
        tprint('\033[92mExpected total run time: \033[0m' + '\033[91m' + total_time + '\033[0m')

    # Run tests
    testinsts = Multitest(cl1_conn, cl2_conn, cl1_test_ip, cl2_test_ip,
                          run_duration, test_range, rundate, title,
                          tcp_win_size, export_dir)
    testinsts.run_tests_for_streams(streams, protocols)
    # Shut down the clients if needed.
    # IF ONE OF THE CLIENTS IS LOCAL, IT WILL NOT SHUT DOWN.
    if shutdown:
        cl1_conn.shutdown()
        cl2_conn.shutdown()
