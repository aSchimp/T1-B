T1-B
====

T1-B = Turtle Bot 1

Installation
====

This *must* be run on a BeagleBone Black running the Debian operating system.  Get the latest image from: http://beagleboard.org/latest-images. The image used for testing was dated 2014-04-23. To check the version installed use

````
cat /boot/uboot/ID.txt
````

Make sure you can establish an SSH connection to the BeagleBone Black. Also make sure that the BBB has a persistant internet connection, either through an ethernet connection or through a USB connection to your computer.

### Setting up a persistant USB internet connection

The steps below are for Windows.

* Open the control panel, and search for "network connections" in the search box. Click "View Network Connections" in the results.
* Right-click the internet connection to share with the BeagleBone Black and select Properties. Navigate to the Sharing tab.
* Select the option to "Allow other network users to connect through this computer's Internet connection"
* Select the BeagleBone Black's network connection from the dropdown and then click OK.
* Now go back to Network Connections and right click the BeagleBone Black's network connection, and select Properties.
* Click "Internet Protocol Version 4 (TCP/IPv4)" in the list and select Properties
* Select the options to "Obtain an IP address automatically" and "obtain DNS server address automatically", and click OK

On the BeagleBone Black run the following commands

````
route add default gw 192.168.7.1
echo "nameserver 8.8.8.8" >> /etc/resolv.conf
````

Test the connection by running `ping google.com`.

Run the following command.

````
nano /opt/scripts/boot/am335x_evm.sh
````

Scroll down until you see the following lines

````
/sbin/ifconfig usb0 192.168.7.2 netmask 255.255.255.252
/usr/sbin/udhcpd -S /etc/udhcpd.conf
````

Immediately after those lines, add the following:

````
/sbin/route add default gw 192.168.7.1 metric 1
````

While you're editing that file, add the following line as well (beneath the line just added). This will allow the WiFi connection which will be setup by the installation script to work on startup. Replace 192.168.1.1 with the IP address of your router. You can find this by running `ipconfig` from a command prompt in Windows. Look for the default gateway for the wireless network connection.

````
/sbin/route add default gw 192.168.1.1 metric 2
````

Thanks to [Carl Lance](http://lanceme.blogspot.com/2013/06/windows-7-internet-sharing-for.html) for the pointers on getting this to work.

### Optionally Disable HDMI

TODO: Add an explanation here

https://learn.adafruit.com/setting-up-wifi-with-beaglebone-black/hardware

### Install Git

````
ntpdate -b -s -u pool.ntp.org
apt-get update && apt-get install git
````

### Install T1-B Software

Shutdown the BBB and plug in the USB wifi adapter. Use a WiFi adapter from [this list](http://www.elinux.org/Beagleboard:BeagleBoneBlack#WIFI_Adapters) for best results. The T1-B installation script has only been tested with the [NETGEAR N150 Wi-Fi USB Adapter (WNA1100)](http://www.amazon.com/gp/product/B0036R9XRU/ref=oh_aui_detailpage_o02_s00?ie=UTF8&psc=1). Turn the device back on.

Clone this repository into {TODO: determine best directory} using the following command.

````
cd {TODO: put directory here}
git clone https://github.com/aschimp/t1-b
````

Place your WiFi network SSID and password into the settings.cfg file.

````
cd t1-b/setup
nano settings.cfg
````

Finally, run the install script. The system will reboot several times during the installation. Log messages after rebooting will be sent to the install_log.txt file in the t1-b/setup directory.

````
chmod +x *.sh
./install.sh
````
