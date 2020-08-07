#
# Accepted parameters for 'rpmbuild':
#

Summary: Connectors between Apache and Tomcat Servlet Container
Name: mod_jk
Version: 1.2.48
Release: HPC1_centos7.x86_64
License: Apache-2.0
Group: Productivity/Networking/Web/Frontends
Source: http://apache.cbox.biz/tomcat/tomcat-connectors/jk/tomcat-connectors-%{version}-src.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-root
Packager: Lyubomir Geshev <lyubomir.geshev@endava.com>
Provides: %{name}
Requires(pre): shadow-utils
Requires(post): /sbin/restorecon
BuildRequires: gcc, httpd-devel
Requires:      httpd

# disable automatic stripping of binaries upon installation
%define __spec_install_post %{nil}
# required because DeadRat wants to package some debug info otherwise
# (this debug info would be created by debug_install_post called
# from spec_install_post)
%define debug_package %{nil}
# Use internal dependency generator rather than external helpers?
%define _use_internal_dependency_generator     0

%description
This package provides modules for Apache to invisibly integrate Tomcat
capabilities into an existing Apache installation.

# To load the module into Apache, run the command "a2enmod jk" as root.

%build
cd native
./configure --with-apxs=/usr/bin/apxs
make


%install
make DESTDIR=${RPM_BUILD_ROOT} install
install -m 700 native/apache-2.0/mod_jk.so usr/lib64/httpd/modules/mod_jk.so

exit 0


%files -f sh_file_list
%defattr(-,root,root)

%post 
restorecon /usr/lib64/httpd/modules/mod_jk.so 


%changelog
* Fri Aug 07 2020 Kostadin Karaivanovov
- upgrade to mod_jk 1.2.48
- build for CentOS7
