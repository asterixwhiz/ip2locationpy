#Example Build#

##Pre-Req's for a Build##

###Install pip###
sudo apt-get -y install python3-pip
###Splunk Addon uss framework###
sudo pip3 install splunk-add-on-ucc-framework
###Slim install###
pip install splunk-packaging-toolkit
###splunk-appinspect install###
pip install splunk-appinspect

##Suggest Build ip2locationpy##
*Where <DIR> is the path to root Directory*
*Where <VER> is the ta-version, ex 1.0.0*

cd /<DIR>/
sudo rm -R /<DIR>/output
sudo ucc-gen --source=/<DIR>/source/package --ta-version <VER>
sudo chown -R owner:owner /<DIR>/output
sudo rm -rf /<DIR>/output/ip2locationpy/lib/aiohttp/.hash/
sudo find /<DIR>/output -type d -exec chmod 755 {} +
sudo find /<DIR>/output -type f -exec chmod 644 {} +
sudo rm -R  /<DIR>/output/ip2locationpy/lib/*.dist-info
slim package /<DIR>/output/ip2locationpy
**Optional appinspect" splunk-appinspect inspect /<DIR>/ip2locationpy-<VER>.tar.gz  --included-tags cloud --included-tags self-service**


##Suggest Deployment of the ip2locationpy in Test##
*Where <DIR> is the path to root Directory*
*Where <VER> is the ta-version, ex 1.0.0*
*Where <USERNAME>:<PASS> is the Username:Password to your Splunk Test enviroment*

sudo /opt/splunk/bin/splunk install app /<DIR>/ip2locationpy-<VER>.tar.gz -update 1 -auth <USERNAME>:<PASS>
sudo /opt/splunk/bin/splunk restart
