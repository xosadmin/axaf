# axaf
AX AS-SET Filter (AXAF) - a lightweight forwarding filter based on AS-SET  
  
### Brief information  
- Supported OS: Debian 11+ / Ubuntu 20.04+  
  
### Installation  
*Prerequisite: Python3, python3-pip and bgpq4 is installed. To install dependencies, following command can be used:*
``
    apt-get install python3 python3-pip bgpq4
``
1. Clone this repo
2. Use ``pip install -r requirements.txt`` to install dependencies
3. Add configuration into config.ini*. For example of config.ini, please refer to [config.ini.example](https://github.com/xosadmin/axaf/blob/main/config.ini.example)  
4. Execute ``python3 main.py`` to generate firewall rules and IP Set entries  
  
** The ``config.ini`` should be placed in the same folder as ``main.py``.  
** The ``daemon.py`` will automatically update prefix list per 24 hours (86400 seconds). You could change this value via edit this file, or manually add ``main.py`` to crontab  
