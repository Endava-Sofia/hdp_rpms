#
# Accepted parameters for 'rpmbuild':
#
# --with tests		- make tests before building

Summary: mod_jk
Name: mod_jk
Version: 1.2.48
Release: HPC1_centos7.x86_64
License: Apache.....
Group: .......
Source: http://apache.cbox.biz/tomcat/tomcat-connectors/jk/tomcat-connectors-1.2.48-src.tar.gz
BuildRoot: %{_tmppath}/samhain-%{version}-root
Packager: Kostadin Karaivanovov <kostadin.karaivanov@endava.com>
Provides: %{name}
Requires(pre): shadow-utils
Requires(post): /sbin/restorecon
BuildRequires: gcc, httpd-devel
Requires:       httpd


#%global selinux_policyver %(%{__sed} -e 's,.*selinux-policy-\\([^/]*\\)/.*,\\1,' /usr/share/selinux/devel/policyhelp || echo 0.0.0)
#%global modulename samhain

# dummy (fix configure warning)
# datarootdir = @datarootdir@

# no quotes here - aparently will be expanded literally

#%define password %(echo $PASSWORD)

#%define withpwd_prg xDSH_STANDALONE
#%define withstg_prg x

# disable automatic stripping of binaries upon installation
%define __spec_install_post %{nil}
# required because DeadRat wants to package some debug info otherwise
# (this debug info would be created by debug_install_post called
# from spec_install_post)
%define debug_package %{nil}
# Use internal dependency generator rather than external helpers?
%define _use_internal_dependency_generator     0

%description
mod_jk

#%prep
#%setup -q -n samhain-%{version}
#%setup -T -D -a 1 -q -n samhain-%{version}

%build
cd native
./configure --with-apxs=/usr/bin/apxs
make


%install
#rm -rf ${RPM_BUILD_ROOT}
# sstrip shouldn't be used since binaries will be stripped later
## cat << EOF > sstrip
## #!/bin/sh
## echo "*** SSTRIP DISABLED ***"
## EOF
make DESTDIR=${RPM_BUILD_ROOT} install
# copy script files to /var/lib/samhain so that we can use them right
# after the package is installed
#
install -m 700 native/apache-2.0/mod_jk.so usr/lib64/httpd/modules/mod_jk.so
#
# file list (helpful advice from Lars Kellogg-Stedman)
#

exit 0


%files -f sh_file_list
%defattr(-,root,root)

%attr(644,root,root) /usr/share/man/man5/samhain*
%attr(644,root,root) /usr/share/man/man8/samhain*
%attr(644,root,root) /etc/logrotate.d/samhain
%attr(600,root,root) /usr/share/selinux/packages/samhain.pp
%if "%{name}" == "yule"
%attr(750,root,samhain) /var/lib/samhain
%attr(750,yule,samhain) /var/log
%endif
%config(noreplace) /etc/samhainrc
%post 
restorecon /usr/lib64/httpd/modules/mod_jk.so 
%changelog
* Fri Jul 24 2020 Kostadin Karaivanovov
- upgrade to samhain 4.4.1
- build for CentOS7


