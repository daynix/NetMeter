set terminal pngcairo nocrop enhanced size 1024,768 font "Verdana,15"
set output "TCP_4_st_2015_07_24_22-09-54_h2g_summary.png"

set title "{/=20 Bandwidth \\& CPU usage for different packet sizes}\n\n{/=18 (Host to Guest, TCP, 4 st.)}"

set xlabel "Buffer size"
set ylabel "Bandwidth (Gb/s)"
set ytics nomirror
set y2label "CPU busy time fraction"
set y2tics nomirror
set y2range [0:1]
set key bmargin center horizontal box samplen 1 width -1
set bmargin 4.6
set logscale x 2
set xtics rotate by -30

set style fill transparent solid 0.2 noborder
plot "TCP_4_st_2015_07_24_22-09-54_h2g_iperf_summary.dat" using 2:($3/1073741824.0-$4/1073741824.0):($3/1073741824.0+$4/1073741824.0) with filledcurves lc rgb "blue" notitle, \
     "" using 2:($1 != 0 ? $3/1073741824.0 : 1/0):xtic($2 < 1024.0 ? sprintf("%.0fB", $2) : ($2 < 1048576.0 ? sprintf("%.0fKB", $2/1024.0) : sprintf("%.0fMB", $2/1048576.0))) with points pt 2 ps 1.5 lw 3 lc rgb "blue" title "Mean tot. BW", \
     "" using 2:($1 == 0 ? $3/1073741824.0 : 1/0):xtic($2 < 1024.0 ? sprintf("%.0fB", $2) : ($2 < 1048576.0 ? sprintf("%.0fKB", $2/1024.0) : sprintf("%.0fMB", $2/1048576.0))) with points pt 2 ps 1.5 lw 3 lc rgb "magenta" title "Approx. BW", \
     "" using 2:($3/1073741824.0):(sprintf("%.2f Gb/s", $3/1073741824.0)) with labels offset 0.9,1.0 rotate by 90 font ",12" notitle, \
     "TCP_4_st_2015_07_24_22-09-54_h2g_mpstat_summary.dat" using 1:($2-$3):($2+$3) with filledcurves lc rgb "red" axes x1y2 notitle, \
     "" using 1:2 with points pt 1 ps 1.5 lw 3 lc rgb "red" axes x1y2 title "Mean tot. CPU"
