#
# Accepted parameters for 'rpmbuild':
#
# --with tests		- make tests before building

Summary: File integrity and host-based IDS
Name: samhain
Version: 4.4.2
Release: HPC1_centos7.x86_64
License: GPL
Group: System Environment/Base
Source: samhain-%{version}.tar.gz
Source1: samhain_sepol_hpc.tar.gz
BuildRoot: %{_tmppath}/samhain-%{version}-root
Packager: Kostadin Karaivanovov <kostadin.karaivanov@endava.com>
Provides: %{name}
Requires(pre): shadow-utils
BuildRequires: systemd
BuildRequires:  checkpolicy, selinux-policy-devel, /usr/share/selinux/devel/policyhelp
%if "%{selinux_policyver}" != ""
Requires:       selinux-policy >= %{selinux_policyver}
%endif
Requires(post): systemd
Requires(post):   /usr/sbin/semodule, /sbin/fixfiles, samhain
Requires(postun): /usr/sbin/semodule

%global selinux_policyver %(%{__sed} -e 's,.*selinux-policy-\\([^/]*\\)/.*,\\1,' /usr/share/selinux/devel/policyhelp || echo 0.0.0)
%global modulename samhain

# dummy (fix configure warning)
# datarootdir = @datarootdir@

# no quotes here - aparently will be expanded literally

%define password %(echo $PASSWORD)

%define withpwd_prg xDSH_STANDALONE
%define withstg_prg x

# disable automatic stripping of binaries upon installation
%define __spec_install_post %{nil}
# required because DeadRat wants to package some debug info otherwise
# (this debug info would be created by debug_install_post called
# from spec_install_post)
%define debug_package %{nil}
# Use internal dependency generator rather than external helpers?
%define _use_internal_dependency_generator     0

%description
samhain is an open source file integrity and host-based intrusion
detection system for Linux and Unix. It can run as a daemon process, and
and thus can remember file changes -- contrary to a tool that runs from
cron, if a file is modified you will get only one report, while
subsequent checks of that file will ignore the modification as it is
already reported (unless the file is modified again).

samhain can optionally be used as client/server system to provide
centralized monitoring for multiple host. Logging to a (MySQL or
PostgreSQL) database is supported.

NOTE: for security reasons, if you distribute binary executables to
third parties you should point out the use of the --add-key option to
modify the key material within the executable.
This spec file is intended to facilitate installation on YOUR system.
If you use this spec file to build a SRPM for distribution to third parties,
make sure to remove the --enable-base configure option below.

%prep
%setup -q -n samhain-%{version}
%setup -T -D -a 1 -q -n samhain-%{version}

%build
%if %{?_with_tests:1}%{!?_with_tests:0}
# test installation (test #7 is only included if --with gpg has been
# specified)
for i in `seq 6` %{?_with_gpg:7}; do ./test/test.sh $i; done
%endif
#
# configure with the user-supplied arguments to './configure'
#
./configure --enable-base=1080295453,279977965  '--exec-prefix=/usr' '--mandir=/usr/share/man'
make
%if "%{withpwd_prg}" == "xDSH_WITH_CLIENT"
%if 0%{?password}
        ./samhain_setpwd samhain new %{password}
	mv samhain samhain.old
	mv samhain.new samhain
%endif
%endif

cd samhain_sepol
make NAME=targeted -f /usr/share/selinux/devel/Makefile
cd -

%install
rm -rf ${RPM_BUILD_ROOT}
# sstrip shouldn't be used since binaries will be stripped later
## cat << EOF > sstrip
## #!/bin/sh
## echo "*** SSTRIP DISABLED ***"
## EOF
make DESTDIR=${RPM_BUILD_ROOT} install
# copy script files to /var/lib/samhain so that we can use them right
# after the package is installed
#
install -m 700 samhain-install.sh init/samhain.startSystemd ${RPM_BUILD_ROOT}/var/lib/samhain
#
# file list (helpful advice from Lars Kellogg-Stedman)
#
echo "/usr/sbin/samhain" > sh_file_list
find %{buildroot}/lib/modules \! -type d -print | \
     sed 's,%{buildroot},,' >> sh_file_list

%{__install} -Dp -m0600 samhain_sepol/samhain.pp %{buildroot}%{_datarootdir}/selinux/packages/samhain.pp
%clean
rm -rf ${RPM_BUILD_ROOT}

%pre
if test "xsamhain" = "xyule"
then
    getent group samhain >/dev/null || groupadd -r samhain
    getent passwd yule >/dev/null || \
	useradd -r -g samhain -d  /var/lib/samhain -s /sbin/nologin \
	-c "samhain server daemon" yule

fi
exit 0

%post
if test "x@sh_lkm@" = x; then
   :
else
   if test -f /sbin/depmod; then
     /sbin/depmod -a
   fi
fi
if [ "$1" -ge 1 ]; then
        # Activate boot-time start up
        sed -i 's/TimeoutStartSec=infinity//' /var/lib/samhain/samhain.startSystemd
        cp /var/lib/samhain/samhain.startSystemd %{_unitdir}/samhain.service
        systemctl daemon-reload
        rm -f ./samhain.startSystemd
	if [ -f /usr/sbin/samhain_stealth ]; then
		rm -f samhain-install.sh
	fi
	shkeep=yes
	if test x"$shkeep" = xno; then
		rm -f ./samhain-install.sh
		rm -f /usr/sbin/samhain_stealth
	fi
fi

/usr/sbin/semodule -s targeted -i %{_datarootdir}/selinux/packages/samhain.pp &> /dev/null
/sbin/fixfiles -R samhain restore

%if "%{name}" != "yule"
cat << EOF

Samhain is installed but is NOT running yet, and the database of
file signatures is NOT initialized yet. Read the documentation,
review configuration files, and then (i) initialize it
(/usr/sbin/samhain -t init)
and (ii) start it manually
(systemctl start samhain.service).
You should enable it for the next boot
(systemctl enable samhain.service)


EOF
%endif
%if "%{name}" == "yule"
cat << EOF

Yule is installed but is NOT running yet, read the documentation,
review configuration files, and then start it
(/usr/sbin/yule)

It is configured to start automatically on the next boot for runlevels
[2-5].

EOF
%endif

%preun
# stop running instance of samhain, if any
if [ -f /var/run/%{name}.pid ]; then
        /usr/sbin/samhain stop
fi
if [ "$1" = 0 ]; then
    systemctl disable samhain.service
    rm /usr/lib/systemd/system/samhain.service
fi

%postun
systemctl daemon-reload
if [ $1 -eq 0 ] ; then
    /usr/sbin/semodule -s targeted -r samhain &> /dev/null
fi


%files -f sh_file_list
%defattr(-,root,root)
#%dir /var/run
%dir /var/log
%doc docs/BUGS COPYING docs/Changelog
%doc LICENSE docs/FAQ.html docs/HOWTO* docs/MANUAL-2_4.* docs/README*
/var/lib/samhain
%if "%{withstg_prg}" == "xsamhain_stealth"
        /usr/sbin/samhain_stealth
%endif
%if "%{withpwd_prg}" == "xDSH_WITH_CLIENT"
        /usr/sbin/samhain_setpwd
%endif
%if "%{withpwd_prg}" == "xDSH_WITH_SERVER"
        /usr/sbin/samhainctl
        %exclude /usr/sbin/samhain_setpwd
%endif
%attr(644,root,root) /usr/share/man/man5/samhain*
%attr(644,root,root) /usr/share/man/man8/samhain*
%attr(644,root,root) /etc/logrotate.d/samhain
%attr(600,root,root) /usr/share/selinux/packages/samhain.pp
%if "%{name}" == "yule"
%attr(750,root,samhain) /var/lib/samhain
%attr(750,yule,samhain) /var/log
%endif
%config(noreplace) /etc/samhainrc

%changelog
* Fri Jul 24 2020 Kostadin Karaivanovov
- upgrade to samhain 4.4.1
- build for CentOS7

* Mon Apr 01 2017 Thorben Fritsche
- added selinux policy module

* Tue Oct 23 2012 Rainer Wichmann
- fixes for yule installation

* Tue May 16 2006 Rainer Wichmann
- fix manual version, noticed by Imre Gergely

* Tue Apr 05 2005 Rainer Wichmann
- disable automatic stripping, use sstrip

* Thu Mar 17 2005 Rainer Wichmann
- fixes for enable-khide

* Wed Oct 20 2004 Rainer Wichmann
- more fixes for client/server detection
- fix for samhain_stealth

* Sun Aug 15 2004 Rainer Wichmann
- fix detection of client/server

* Sat Jun 19 2004 Rainer Wichmann
- replace ./test.sh $i with make test$i
- add logic for rpm-light (remove some more files after install)
- make postun posix compliant (avoid empty argument list for rm -f)

* Wed Dec 31 2003 Stijn Jonker <sjcjonker@sjc.nl>
- Fixed correctly build of yule-*-rpm
- Fixed excluding of yule_setpwd, and including of yulectl on yule build
- Fixed including of samhain_setpwd in samhain client build
- Above changes required for correct build in newer rpms,
  with defaults for abort on unpacked files due to
  %_unpackaged_files_terminate_build 1 setting
- Fixed installation text for yule, not to display samhain text
- Added /sbin/chkconfig install_name on to enable the rc scripts

* Thu Dec 11 2003 Christian Vanguers  <cva at molis dot be>
- Fixed typo in samhain.spec
- Compiled on RedHat Enterprise Linux ES 3

* Thu Mar 26 2003 Rainer Wichmann
- strip REQ_FROM_SERVER in config file path (%config(noreplace) ...)

* Sun Jan 12 2003 Rainer Wichmann <support at la-samhna dot de>
- replace %configure with ./configure

* Tue Dec 24 2002 Rainer Wichmann <support at la-samhna dot de>
- backported applicable changes to samhain.spec.in
- warn user that database must be initialized
- fix version of MANUAL in '%files'
- test for chkconfig, use only if found

* Sun Dec 22 2002 Andre Oliveira da Costa <brblueser@uol.com.br> 1.7.0
- fixed typo with _usr macro on ./configure
- stops running samhain before uninstall
- implemented conditionals to allow proper uninstalls/upgrades
- 'BuildPreReq: gpg' is considered only if '--with gpg' is provided
- run 'chkconfig' to activate samhain after installation
- warn user that samhain must be manually started after
  install/upgrade

* Fri Dec 20 2002 Rainer Wichmann <support at la-samhna dot de>
- backported to samhain.spec.in (take over user's choices from configure)
- also save samhain.startLSB and samhain.startSuSE for install-boot

* Thu Dec 19 2002 Andre Oliveira da Costa <brblueser@uol.com.br> 1.6.6
- optional parameters '--with gpg' and '--with tests'
- use of pre-defined macros whenever possible

* Wed Dec 18 2002 Andre Oliveira da Costa <brblueser@uol.com.br> 1.6.6
- Fixed installation process, avoiding hardcoded paths on the binaries
  (thks to samhain's author Rainer Wichmann)

* Mon Dec 16 2002 Andre Oliveira da Costa <brblueser@uol.com.br> 1.6.6
- First attempt to build from sources
