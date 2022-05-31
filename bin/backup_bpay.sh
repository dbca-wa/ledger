#!/bin/bash
DATETIME=`date +%Y%m%d-%H%M%S`
cd /mnt/external/CommBiz_WildlifeLicensing
tar cvzf /archives/rotate1/bpay_backups-$DATETIME.tar.gz *
