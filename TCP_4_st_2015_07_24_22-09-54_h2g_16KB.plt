set terminal pngcairo nocrop enhanced size 1024,768 font "Verdana,15"
set output "TCP_4_st_2015_07_24_22-09-54_h2g_16KB.png"

set title "{/=20 Buffer size: 16 KB, Av. rate: 7.48 Gb/s}\n\n{/=18 (Host to Guest, TCP, 4 st.)}"

set xlabel "Time (s)"
set ylabel "Bandwidth (Gb/s)"
set ytics nomirror
set y2label "CPU busy time fraction"
set y2tics nomirror
set y2range [0:1]
set key bmargin center horizontal box samplen 1 width -1
set bmargin 4.6

set style fill transparent solid 0.2 noborder
plot "TCP_4_st_2015_07_24_22-09-54_h2g_16KB_iperf_processed.dat" using 1:($2/1073741824.0-$3/1073741824.0):($2/1073741824.0+$3/1073741824.0) with filledcurves lc rgb "blue" notitle, \
     "" using 1:($2/1073741824.0) with points pt 2 ps 1.5 lw 3 lc rgb "blue" title "Mean tot. BW", \
     "TCP_4_st_2015_07_24_22-09-54_h2g_16KB_mpstat_processed.dat" using 1:($2-$3):($2+$3) with filledcurves lc rgb "red" axes x1y2 notitle, \
     "" using 1:2 with points pt 1 ps 1.5 lw 3 lc rgb "red" axes x1y2 title "Mean tot. CPU"
