#!/bin/bash
#
port=$1
bcf=/tmp/bthmacs.cfg
ecf=/tmp/ethmacs.cfg

# first handle the bluetooth devices one by one

#logger findmac called with port $1

if [ -r ${bcf} ];
then
    while read line
    do
#        logger check BTH MAC $line
        if [ "${line}" != "" ];
        then
#            logger "executing l2ping -c1 -t5 -s32 ${line}"
            l2ping -c1 -t5 -s32 ${line}
            res=$?
#            logger l2ping said $res
            if [ "${res}" -eq "141" ]; then
#                logger switching mac ON
                echo {\"MAC\": \"${line}\", \"State\": \"on\", \"Proto\": \"BTH\"} | netcat 127.0.0.1 ${port}
            else
#                logger switching mac OFF
                echo {\"MAC\": \"${line}\", \"State\": \"off\", \"Proto\": \"BTH\"} | netcat 127.0.0.1 ${port}
            fi
        fi
    done < ${bcf}
else
    logger cannot read $bcf
fi

# now find all network MAC's
arps=/tmp/arps.txt
sudo arp-scan -l | grep "192.168"|awk '{print $2}' > ${arps}

if [ -r ${ecf} ];
then
    while read line
    do
        if [ "${line}" != "" ];
        then
#            logger grep ${line} ${arps}
            grep ${line} ${arps}
            res=$?
#            logger found $res
            if [ "${res}" -eq "141" ]; then
#                logger switching mac ON
                echo {\"MAC\": \"${line}\", \"State\": \"on\", \"Proto\": \"ETH\"} | netcat 127.0.0.1 ${port}
            else
#                logger switching mac OFF
                echo {\"MAC\": \"${line}\", \"State\": \"off\", \"Proto\": \"ETH\"} | netcat 127.0.0.1 ${port}
            fi
        fi
    done < ${ecf}
fi
