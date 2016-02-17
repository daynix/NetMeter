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
from re import sub
from os.path import isdir, join
from os import makedirs, listdir
from datetime import datetime
from subprocess import Popen
from glob import glob

########### May requires changing  #############
gnuplot_path = r'gnuplot'
######### Don't change unless needed ###########
iperf_datacolumn = 2
logo_background = '{/=30 [}&{/:Bold=22 DayniX}{/=30 ]}'
logo_bg_location = 'screen 0.94, screen 0.99'
logo_bg_color = '#be202e'
logo_foreground = '&{/=30 [}{/:Bold=22 DayniX}&{/=30 ]}'
logo_fg_location = 'screen 0.94, screen 0.995'
logo_fg_color = '#1e6378'
logo_name = '{/=10 Daynix Computing ltd.}'
logo_name_location = 'screen 0.94, screen 0.945'
################################################

rundate = datetime.now().strftime('%Y_%m_%d_%H-%M-%S')

def findfiles(d):
    one2two_iperf = [f for f in listdir(d) if f.endswith('one2two_iperf_summary.dat')]
    one2two_mpstat = [f for f in listdir(d) if f.endswith('one2two_mpstat_summary.dat')]
    two2one_iperf = [f for f in listdir(d) if f.endswith('two2one_iperf_summary.dat')]
    two2one_mpstat = [f for f in listdir(d) if f.endswith('two2one_mpstat_summary.dat')]
    filelist = [one2two_iperf, one2two_mpstat, two2one_iperf, two2one_mpstat]
    protocols = [False for i in range(4)]
    streams = [False for i in range(4)]
    for i in range(4):
        if len(filelist[i]) > 1:
            print('The following files found in ' + d + ':')
            for f in filelist[i]:
                print(f)

            print('Expecting to find only one file of each kind in NM output directory!')
            sys.exit(1)
        elif not len(filelist[i]):
            filelist[i] = False
        else:
            params = filelist[i][0].split('_')
            filelist[i] = join(d, filelist[i][0])
            protocols[i] = params[0]
            streams[i] = params[1]

    protoset = set([p for p in protocols if p])
    if len(protoset) > 1:
        print('Error! Found tests using different protocols in ' + d + '.')
        sys.exit(1)

    streamset = set([s for s in streams if s])
    if len(streamset) > 1:
        print('Error! Found tests using different stream numbers in ' + d + '.')
        sys.exit(1)

    (protocols,) = protoset
    (streams,) = streamset

    return filelist, protocols, streams


def get_rate_factor(n):
    factor = 1.0
    for x in ['b/s', 'Kb/s', 'Mb/s', 'Gb/s']:
        if n < 1000.0:
            return x, factor

        n /= 1000.0
        factor *= 1000.0

    return 'Tb/s', factor


def get_iperf_metadata(f):
    data = np.loadtxt(f)
    datamax = np.amax(data[:,iperf_datacolumn])
    test_status = data[:,0]
    non_failed_test_status = test_status[(test_status >= 0).nonzero()]
    allOK = np.all(non_failed_test_status)
    anyOK = np.any(non_failed_test_status)
    if allOK:
        status = 'all_OK'
    elif anyOK:
        status = 'some_OK'
    else:
        status = 'none_OK'

    return datamax, status


def gen_net_pointplots(status, type):
    if type == 'old':
        color = 'red'
        err_color = 'cyan'
        lw = '4'
    else:
        color = 'blue'
        err_color = 'magenta'
        lw = '3'

    if status == 'all_OK':
        return ('     "" using 2:($1 >= 0 ? $3/rf : 1/0):xtic(printxsizes($2)) with points '
                'pt 2 ps 0.8 lw ' + lw + ' lc rgb "' + color + '" title "Mean - ' + type + '", \\\n')
    else:
        content = ('     "" using 2:($1 == 0 ? $3/rf : 1/0):xtic(printxsizes($2)) with points '
                   'pt 2 ps 0.8 lw ' + lw + ' lc rgb "' + err_color + '" title "Approx. - ' + type + '", \\\n')

    if status == 'some_OK':
        content = ('     "" using 2:($1 >= 0 ? $3/rf : 1/0):xtic(printxsizes($2)) with points '
                   'pt 2 ps 0.8 lw ' + lw + ' lc rgb "' + color + '" title "Mean - ' + type + '", \\\n') + content

    return content


def iperf_plot_block(data_unit, dir_title, old_datfile, new_datfile):
    old_max, old_status = get_iperf_metadata(old_datfile)
    new_max, new_status = get_iperf_metadata(new_datfile)
    BW_units, rate_factor = get_rate_factor(max(old_max, new_max))
    content = (
               'set ylabel "Bandwidth (' + BW_units + ')"\n'
               'set xlabel "' + data_unit + ' size"\n'
               'set yrange [0:*]\n'
               'rf = ' + str(rate_factor) + '\n'
               'set title "{/=18 ' + dir_title + '}"\n'
               'plot "' + old_datfile + '" using ($1 >= 0 ? $2 : 1/0):($3/rf-$4/rf):($3/rf+$4/rf) with filledcurves lc rgb "red" notitle, \\\n'
              )
    content += gen_net_pointplots(old_status, 'old')
    content += '     "" using ($1 < 0 ? $2 : 1/0):(0):(sprintf("Old failed!")) with labels offset 0.9,2.5 rotate by 90 tc rgb "red" font ",12" notitle, \\\n'
    content += '     "' + new_datfile + '" using ($1 >= 0 ? $2 : 1/0):($3/rf-$4/rf):($3/rf+$4/rf) with filledcurves lc rgb "blue" notitle, \\\n'
    content += gen_net_pointplots(new_status, 'new')
    content += '     "" using ($1 < 0 ? $2 : 1/0):(0):(sprintf("New failed!")) with labels offset 0.9,7.0 rotate by 90 tc rgb "blue" font ",12" notitle\n'
    return content


def mpstat_plot_block(data_unit, dir_title, old_datfile, new_datfile):
    if old_datfile and new_datfile:
        content = (
                   'set ylabel "CPU busy time fraction"\n'
                   'set xlabel "' + data_unit + '"\n'
                   'set yrange [0:1]\n'
                   'set title "{/=18 ' + dir_title + '}"\n'
                   'plot "' + old_datfile + '" using 1:($2-$3):($2+$3) with'
                   ' filledcurves lc rgb "red" notitle, \\\n'
                   '     "" using 1:2:xtic(printxsizes($1)) with points pt 1'
                   ' ps 0.8 lw 4 lc rgb "red" title "Mean tot. CPU - old", \\\n'
                   '     "' + new_datfile + '" using 1:($2-$3):($2+$3) with'
                   ' filledcurves lc rgb "blue" notitle, \\\n'
                   '     "" using 1:2:xtic(printxsizes($1)) with points pt 1'
                   ' ps 0.8 lw 3 lc rgb "blue" title "Mean tot. CPU - new"\n'
                  )
    else:
        content = (
                   'set object rectangle from screen 0.52,0.05 to screen 0.96,0.845 behind fc rgb "#ffffee"\n'
                   'set label "{/=30 No CPU results found}" at screen 0.74, screen 0.47 center\n'
                  )

    return content


def write_comp_gp(old_d, new_d, out_basename):
    raw_data_subdir = "raw-data"
    old_files, old_proto, old_streams = findfiles(join(old_d, raw_data_subdir))
    new_files, new_proto, new_streams = findfiles(join(new_d, raw_data_subdir))
    old_name = sub('[^0-9a-zA-Z/]+', '-', old_d)
    new_name = sub('[^0-9a-zA-Z/]+', '-', new_d)
    if old_proto == new_proto == 'TCP':
        data_unit = 'Buffer'
    elif old_proto == new_proto == 'UDP':
        data_unit = 'Datagram'
    else:
        data_unit = 'Buffer/Datagram'

    one2two_block = True
    two2one_block = True
    content = (
               'set terminal pdfcairo color enhanced rounded size 29.7cm,21.0cm font "Verdana,15"\n'
               'set output "' + out_basename + '.pdf"\n'
               '\n'
               'set size 0.49,0.45\n'
               'set ytics nomirror\n'
               'set key bmargin center horizontal box samplen 1 width -1\n'
               'set bmargin 4.6\n'
               'set logscale x 2\n'
               'set xtics rotate by -30\n'
               'set style fill transparent solid 0.2 noborder\n'
               'printxsizes(x) = x < 1024.0 ? sprintf("%.0fB", x) : (x < 1048576.0 ? sprintf("%.0fKB", x/1024.0) : sprintf("%.0fMB", x/1048576.0))\n'
               '\n'
               'set label "Old: {/=18 ' + old_name + ' [' + old_proto +', ' + old_streams +' st.]}\\\n'
               '       \\n\\nNew: {/=18 ' + new_name + ' [' + new_proto +', ' + new_streams +' st.]}" at screen 0.01, screen 0.99\n'
               'set label "{/=22 Bandwidth Comparison}" at screen 0.254, screen 0.91 center\n'
               'set label "{/=22 CPU Usage Comparison}" at screen 0.756,  screen 0.91 center\n'
               'set label "' + logo_background + '" at ' + logo_bg_location + ' center tc rgb "' + logo_bg_color + '"\n'
               'set label "' + logo_foreground + '" at ' + logo_fg_location + ' center tc rgb "' + logo_fg_color + '"\n'
               'set label "' + logo_name + '" at ' + logo_name_location + ' center\n'
               '\n'
              )
    if (not old_files[2]) or (not new_files[2]):
        content += 'set object rectangle from screen 0,0.45 to screen 1.0,0.88 behind fc rgb "#ffcccc"\n'
        one2two_block = False

    if not new_files[2]:
        content += 'set label "{/=30 No new Ctient 1 to Client 2 results found}" at screen 0.5, screen 0.72 center\n'

    if not old_files[2]:
        content += 'set label "{/=30 No old Ctient 1 to Client 2 results found}" at screen 0.5, screen 0.68 center\n'

    if not one2two_block:
        content += '\n'

    if (not old_files[0]) or (not new_files[0]):
        content += 'set object rectangle from screen 0,0 to screen 1.0,0.45 behind fc rgb "#ffcccc"\n'
        two2one_block = False

    if not new_files[0]:
        content += 'set label "{/=30 No new Client 2 to Client 1 results found}" at screen 0.5, screen 0.27 center\n'

    if not old_files[0]:
        content += 'set label "{/=30 No old Client 2 to Client 1 results found}" at screen 0.5, screen 0.23 center\n'

    if not two2one_block:
        content += '\n'

    content += '\nset multiplot\n'
    if one2two_block:
        dir_title = 'Client 1 to Client 2'
        content += 'set origin 0.0,0.45\n'
        content += iperf_plot_block(data_unit, dir_title, old_files[0], new_files[0])
        content += '\nset origin 0.495,0.45\n'
        content += mpstat_plot_block(data_unit, dir_title, old_files[1], new_files[1])

    if two2one_block:
        dir_title = 'Client 2 to Client 1'
        content += '\nset origin 0.0,0.0\n'
        content += iperf_plot_block(data_unit, dir_title, old_files[2], new_files[2])
        content += '\nset origin 0.495,0.0\n'
        content += mpstat_plot_block(data_unit, dir_title, old_files[3], new_files[3])

    content += 'unset multiplot\n'
    scriptfile = out_basename + '.plt'
    with open(scriptfile, 'w') as outfile:
        outfile.write(content)


def main():
    if len(sys.argv) != 4:
        print('Usage: ' + sys.argv[0] + ' <OLD DIR1>,<OLD DIR2>,... <NEW DIR1>,<NEW DIR2>,... <OUTPUT DIR>')
        sys.exit(1)

    olddirs = sys.argv[1].split(',')
    olddirs = [glob(d)[0] for d in olddirs]
    newdirs = sys.argv[2].split(',')
    newdirs = [glob(d)[0] for d in newdirs]
    outdir = sys.argv[3]

    if len(olddirs) != len(newdirs):
        print('Error! The number of old directories must be equal to the number of new ones.')
        sys.exit(1)

    for (o,n) in zip(olddirs,newdirs):
        if not isdir(o):
            print('Directory ' + o + ' does not exist!')
            sys.exit(1)
        elif not isdir(n):
            print('Directory ' + n + ' does not exist!')
            sys.exit(1)

    if not isdir(outdir):
        try:
            makedirs(outdir)
        except:
            print('The output directory (' + outdir + ') could not be created. Exiting.')
            sys.exit(1)

    print('The output directory is: ' + outdir)

    count = 0
    for (o,n) in zip(olddirs,newdirs):
        count += 1
        out_basename = join(outdir, rundate + '_comp_' + format(count, '04d'))
        write_comp_gp(o, n, out_basename)
        p = Popen([gnuplot_path, out_basename + '.plt'])
        p.wait()


if __name__ == "__main__":
    main()
