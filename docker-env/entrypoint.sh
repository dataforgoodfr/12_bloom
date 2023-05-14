#!/bin/bash

cat /source_code/.env >> /etc/environment

/etc/init.d/rsyslog restart

ln -sf /dev/stdout /var/log/syslog

# execute CMD
echo "$@"
exec "$@"
