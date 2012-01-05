%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

%define mod_name keystone
%define py_puresitedir  %{python_sitelib}

Name:           openstack-keystone
Version:        2011.3.1
Release:        3
Url:            http://www.openstack.org
Summary:        Python bindings to the OS API
License:        Apache 2.0
Vendor:         Grid Dynamics Consulting Services, Inc.
Group:          Development/Languages/Python
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildRequires:  python-devel python-setuptools python-sphinx >= 0.6.0 make
BuildArch:      noarch
Requires:       python-eventlet python-lxml python-paste python-sqlalchemy python-routes python-httplib2 python-paste-deploy start-stop-daemon python-webob python-setuptools python-passlib


%description
Authentication service - proposed for OpenStack


%package doc
Summary:        Documentation for %{name}
Group:          Documentation
Requires:       %{name} = %{version}-%{release}


%description doc
Documentation for %{name}.


%prep
%setup -q -n %{name}-%{version}
sed -i 's|sqlite:///keystone|sqlite:////var/lib/keystone/keystone|' etc/keystone.conf
sed -i 's|log_file = keystone.log|log_file = /var/log/keystone/keystone.log|' etc/keystone.conf


%build
python setup.py build


%install
%__rm -rf %{buildroot}

%__make -C doc/ html PYTHONPATH=%{_builddir}/%{name}-%{version}
python setup.py install --prefix=%{_prefix} --root=%{buildroot}
mv %{buildroot}/usr/bin/keystone{,-combined}

install -d -m 755 %{buildroot}%{_sysconfdir}/%{mod_name}
install -m 644 etc/* %{buildroot}%{_sysconfdir}/%{mod_name}
install -d -m 755 %{buildroot}%{_sysconfdir}/nova
install -m 644 examples/paste/auth_*ini %{buildroot}%{_sysconfdir}/nova
install -m 644 examples/paste/nova-api-paste.ini %{buildroot}%{_sysconfdir}/nova/api-paste.ini.keystone.example

install -d -m 755 %{buildroot}%{_sharedstatedir}/keystone
install -d -m 755 %{buildroot}%{_localstatedir}/log/%{mod_name}
install -d -m 755 %{buildroot}%{_localstatedir}/run/%{mod_name}

install -p -D -m 755 redhat/%{name}.init %{buildroot}%{_initrddir}/%{name}

%__rm -rf %{buildroot}%{py_puresitedir}/{doc,examples,tools}


%clean
%__rm -rf %{buildroot}


%pre
getent passwd keystone >/dev/null || \
useradd -r -g nobody -G nobody -d %{_sharedstatedir}/keystone -s /sbin/nologin \
-c "OpenStack Keystone Daemon" keystone
exit 0


%preun
if [ $1 = 0 ] ; then
    /sbin/service %{name} stop
    /sbin/chkconfig --del %{name}
fi


%files
%defattr(-,root,root,-)
%doc README.md HACKING LICENSE
%{py_puresitedir}/%{mod_name}*
%{_usr}/bin/*
%dir %attr(0755, keystone, nobody) %{_sharedstatedir}/%{mod_name}
%dir %attr(0755, keystone, nobody) %{_localstatedir}/log/%{mod_name}
%dir %attr(0755, keystone, nobody) %{_localstatedir}/run/%{mod_name}
%config(noreplace) %{_sysconfdir}/nova/*
%config(noreplace) %{_sysconfdir}/keystone
%{_sysconfdir}/rc.d/init.d/*


%files doc
%defattr(-,root,root,-)
%doc examples doc

%changelog
