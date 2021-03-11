#!/bin/sh
rm -r /home/sats/code/2
/usr/share/logstash/bin/logstash -f /home/sats/buttonpython/logstash-pos.conf --config.reload.automatic --path.data /home/sats/code/2
rm -r /home/sats/code/2
/usr/share/logstash/bin/logstash -f /home/sats/buttonpython/logstash-neg.conf --config.reload.automatic --path.data /home/sats/code/2
rm -r /home/sats/code/2
/usr/share/logstash/bin/logstash -f /home/sats/buttonpython/logstash-pol.conf --config.reload.automatic --path.data /home/sats/code/2
rm -r /home/sats/code/2
/usr/share/logstash/bin/logstash -f /home/sats/buttonpython/logstash-t20.conf --config.reload.automatic --path.data /home/sats/code/2
