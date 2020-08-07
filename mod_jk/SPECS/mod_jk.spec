Name:           mod_jk
Version:        1.2.48
Release:        1%{?dist}
Summary:        Connectors between Apache and Tomcat Servlet Container

License:    Apache-2.0
URL:        http://tomcat.apache.org/connectors-doc/
Packager:   Kostadin Karaivanov <kostadin.karaivanov@endava.com>
Provides:   %{name}   
%undefine   _disable_source_fetch
Source0:    http://apache.cbox.biz/tomcat/tomcat-connectors/jk/tomcat-connectors-%{version}-src.tar.gz
%define     SHA512SUM0 955a830724a3902e29032a5d2e7603d3170334e8a383d314f6bf8539d53d9f7ee4cfa0b31cfc954acb0a13d9975ed2229de085d08de3885f8679b509924fde47
%define     connectors_root    tomcat-connectors-%{version}-src
BuildRequires: gcc make httpd-devel 
Requires:   httpd    


%description
This package provides modules for Apache to invisibly integrate Tomcat
capabilities into an existing Apache installation.

To load the module into Apache, run the command "a2enmod jk" as root.

%prep
echo "%SHA512SUM0  %SOURCE0" | sha512sum -c -
%setup -q -n %{connectors_root}

%build
cd native/
%{configure} -with-apxs=/usr/bin/apxs
%make_build

%install 
install -d -m 755 %{buildroot}%{_libdir}/httpd/modules
install -m 755 native/apache-2.0/mod_jk.so %{buildroot}%{_libdir}/httpd/modules/

%files
%defattr(-,root,root,-)
%{_libdir}/httpd/modules/*

%changelog
* Fri Aug  7 2020 larry
