#!/bin/bash

source settings.cfg

workingDir=$PWD

step_one()
{
	echo "Preparing BeagleBone Black for T1-B software installation"

	echo "Setting date and time..."
	ntpdate -b -s -u pool.ntp.org

	echo "Installing script to set date/time on startup..."
	apt-get -y install ntp
	touch /var/log/ntp.log

	echo "Updating kernel to latest 3.8 version..."
	echo "After this completes the system will reboot. Installation will continue when the system starts back up. Progress will be logged to install_log.txt in the current directory."
	cd /opt/scripts/tools/
	./update_kernel.sh
	cd $workingDir
	./runonce.sh "install.sh -s 2 >> install_log.txt 2>>&1"
	reboot
}

step_two()
{
	echo "Waiting for system time to synchronize..."
	ntp-wait
	echo "Installing WiFi reset service"
	git clone https://github.com/aSchimp/beaglebone-black-wifi-reset
	cd beaglebone-black-wifi-reset
	chmod +x install.sh
	./install.sh

	echo "Configuring wireless network settings..."
	wifiInterface="$(iwconfig 2> /dev/null | grep -o '^[[:alnum:]]\+')"
	echo -e "\nauto $(wifiInterface)\niface $(wifiInterface) inet dhcp\n    wpa-ssid \"$(wifi_ssid)\"\n    wpa-psk \"$(wifi_password)\"\n" >> /etc/network/interfaces
	ifup $wifiInterface
}

usage() { echo "Usage: $0 [-s <integer>]" 1>&2; exit 1; }

while getopts ":s:" opt; do
	case "${opt}" in
		s)
			s=${OPTARG}
			re='^[0-9]+$'
			if ! [[ $s =~ $re ]]; then
			   usage
			fi
			;;
		*)
			usage
			;;
	esac
done

if [ -z "${s}" ]; then
	s=1
fi

case "${s}" in
	1)
		step_one
		;;
	2)
		step_two
		;;
esac

echo "T1-B installation successful"