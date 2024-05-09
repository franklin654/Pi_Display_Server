# Server for Raspberry PI display
#### Bluetooth Service built using PySide6 the service is hosted on the local bluetooth adapter and registered in public browsing group so it can be discoverable. It uses Bluetooth RFCOMM Protocol to connect to Clients and receive requests to display either Image or a message.

## Requirements
* #### Python 3.9-12
* #### PySide6
``pip install -U PySide6``
* #### Bluez package
``sudo apt-get -y install bluez ``


## Setting up the service
* clone the git repo

``git clone https://github.com/franklin654/Pi_Display_Server.git``

* create a cron job to automatically run the service at **boot/reboot**

``(crontab -l; echo "@reboot python {path_to_repo_dir}/main.py") | crontab -``

## Start the service manually

``python {path_to_repo}/main.py``

## Deleting the service
* remove the cron job

``crontab -l | gre -v "@reboot python @reboot python {path_to_repo_dir}/main.py" | crontab -``

* remove the directory

``rm -rf {path_to_repo}``


