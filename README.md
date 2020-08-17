# mod_jk

## Installation
- Install dependancies
```bash 
yum install -y rpm-build rpmdevtools httpd-devel gcc
```
- Create RPM build tree within user's home directory
```bash
rpmdev-setuptree
```
- Create spec file and paste the content from this repo
```bash
touch ~/rpmbuild/SPECS/mod_jk.spec
vim ~/rpmbuild/SPECS/mod_jk.spec
```
- Add changelog message
```bash
rpmdev-bumpspec --comment="Build from source" --userstring="John Doe<john.doe@example.com>" ~/rpmbuild/SPECS/mod_jk.spec
```
- Build the RPM
```bash
rpmbuild -ba ~/rpmbuild/SPECS/mod_jk.spec
```
- Install the package. RPM name could be checked in ```~/rpmbuild/RPMS/x86_64/```
```bash
yum install -y ~/rpmbuild/RPMS/x86_64/mod_jk-1.2.48-2.el7.x86_64.rpm
```
- Check the installation
```bash
rpm -qa | grep mod_jk
```
## Setup
- Load module
```bash
echo "LoadModule jk_module modules/mod_jk.so" >> ~/etc/httpd/conf.modules.d/modules.conf
```
- Create mod_jk.conf
```bash
echo "JkShmFile /var/run/httpd/jk-runtime-status
JkWorkersFile /etc/httpd/conf/workers.properties
JkLogLevel info
JkLogFile /var/log/httpd/mod_jk.log" >> ~/etc/httpd/conf.d/mod_jk.conf
```
- Create other conf files
```bash
touch /etc/httpd/conf/jkmounts.conf
vim /etc/httpd/conf/jkmounts.conf
touch /etc/httpd/conf/workers.properties
vim /etc/httpd/conf/workers.properties
```
- httpd useful commands
```bash
sudo systemctl start httpd
sudo systemctl restart httpd
sudo systemctl -l status httpd
sudo systemctl stop httpd
```
