%global debug_package %{nil}
%define __jar_repack 0
AutoReqProv: no

%define patchlevel 241

Name:           jre1.8.0
Version:        1.8.0_%{patchlevel}
Release:        1_hpc%{?dist}
Summary:        Java Platform Standard Edition Runtime Environment
Group:          Development/Tools

License:        Java Lizenz
URL:            http://www.java.com/
Source0:        jre-8u%{patchlevel}-linux-x64.tar.gz
Source1:        jce_policy-8.zip
#Source2:        https://www.startssl.com/certs/ca.crt
Source3:        HPC-ROOT-CA-cacert.pem
Source4:        HPC-PROD-ROOT-cacert.pem
Source5:        SymantecClass3SecureServerCA-G4.pem
Source6:        heidelpay-inten-root-ca.pem
Source7:        hpchd-loc-root-ca.pem
Source8:        ca.der
Patch:          orace-java-hpc.sec.patch
BuildRequires:  curl

%if %{rhel} <= 5
BuildRoot: %{_topdir}/BUILDROOT/%{name}-%{version}-%{release}-root
%endif

%description
The Java Platform Standard Edition Runtime Environment (JRE) contains
everything necessary to run applets and applications designed for the
Java platform. This includes the Java virtual machine, plus the Java
platform classes and supporting files.

The JRE is freely redistributable, per the terms of the included license.

%prep
%setup -q -n jre%{version}
%setup -q -n jre%{version} -T -D -a 1
%patch -p1

%build
cp -a UnlimitedJCEPolicyJDK8/* lib/security/
rm -rf UnlimitedJCEPolicyJDK8

#JAVA_HOME=`pwd` bin/keytool -import -trustcacerts -alias startssl -file %{SOURCE2} -keystore lib/security/cacerts -storepass changeit --noprompt
JAVA_HOME=`pwd` bin/keytool -import -trustcacerts -alias hpc-root -file %{SOURCE3} -keystore lib/security/cacerts -storepass changeit --noprompt
JAVA_HOME=`pwd` bin/keytool -import -trustcacerts -alias hpc-prod-root -file %{SOURCE4} -keystore lib/security/cacerts -storepass changeit --noprompt
JAVA_HOME=`pwd` bin/keytool -import -trustcacerts -alias symantecinterg4 -file %{SOURCE5} -keystore lib/security/cacerts -storepass changeit --noprompt
JAVA_HOME=`pwd` bin/keytool -import -trustcacerts -alias heidelpay-inten-root  -file %{SOURCE6} -keystore lib/security/cacerts -storepass changeit --noprompt
JAVA_HOME=`pwd` bin/keytool -import -trustcacerts -alias hpchd-loc-root  -file %{SOURCE7} -keystore lib/security/cacerts -storepass changeit --noprompt
JAVA_HOME=`pwd` bin/keytool -import -trustcacerts -alias ppro-test-rootca  -file %{SOURCE8} -keystore lib/security/cacerts -storepass changeit --noprompt

%install
mkdir -p %{buildroot}%{_prefix}/java/jre%{version}
cp -a * %{buildroot}%{_prefix}/java/jre%{version}

%files
%defattr(-,root,root,755)
%dir %{_prefix}/java/jre%{version}
%{_prefix}/java/jre%{version}/*

%pre
if [ "$1" = 1 ]; then
  if [ -x /usr/local/sbin/manage_tomcats ]; then
    /usr/local/sbin/manage_tomcats stop
    /usr/local/sbin/manage_tomcats cleancache
  fi
  for i in `/bin/fgrep -l '# HPC-TAG: Java8' /etc/init.d/*`; do
    $i stop
  done
elif [ $1 -gt 1 ]; then
  if [ -x /usr/local/sbin/manage_tomcats ]; then
    /usr/local/sbin/manage_tomcats stop
    /usr/local/sbin/manage_tomcats cleancache
  fi
  for i in `/bin/fgrep -l '# HPC-TAG: Java8' /etc/init.d/*`; do
    $i stop
  done
fi

%post
if [ $1 -gt 0 ]; then
  /bin/ln -sfn %{_prefix}/java/jre%{version} %{_prefix}/java/java8
  /bin/ln -sfn %{_prefix}/java/java8/bin/java /usr/bin/java
  echo "export JAVA_HOME=%{_prefix}/java/java8" > /etc/profile.d/java.sh
  chmod 644 /etc/profile.d/java.sh
fi
if [ "$1" == 1 ]; then
  if [ -x /usr/local/sbin/manage_tomcats ]; then
    /usr/local/sbin/manage_tomcats start
  fi
  for i in `/bin/fgrep -l '# HPC-TAG: Java8' /etc/init.d/*`; do
    $i start
  done
elif [ $1 -gt 1 ]; then
  if [ -x /usr/local/sbin/manage_tomcats ]; then
    /usr/local/sbin/manage_tomcats start
  fi
  for i in `/bin/fgrep -l '# HPC-TAG: Java8' /etc/init.d/*`; do
    $i start
  done
fi

%postun
if [ "$1" = 0 ]; then
  rm -f %{_prefix}/java/java8
  rm -f /usr/bin/java
  rm -f /etc/profile.d/java.sh
fi

%changelog
