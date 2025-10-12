#!/usr/bin/env bash

echo "Welcome to AXAF Installer."

if [[ $(whoami) != "root" ]]; then
  echo "Error: You are not using root user to run this script. Exiting..."
  exit 1
fi

if [[ -d "/opt/axaf" ]]; then
  echo "Warning: AXAF is already installed. Press Enter to override program (configure will be preserved)."
  read cont
else
  mkdir -p "/opt/axaf"
fi

echo "Installing dependencies..."
DEBIAN_FRONTEND=noninteractive apt install iptables-persistent ipset-persistent python3 python3-pip bgpq4 -y
pip3 -r install requirements.txt --break-system-package

echo "Copying files..."
cp -r "*.py" /opt/axaf
cat>>/opt/axaf/config.ini<<EOF
[rpki_verify]
enable = False

EOF

echo "Install AXAF as a service..."
cp -fr axaf.service /etc/systemd/system
systemctl daemon-reload
systemctl enable axaf

echo "Install complete. The program is located at /opt/axaf"
echo "Please finish config.ini before start the AXAF service."