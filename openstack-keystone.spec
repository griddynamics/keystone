%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

%global with_doc 1
%global prj keystone
%define mod_name keystone
%define py_puresitedir  %{python_sitelib}

Name:           openstack-%{prj}
Epoch:          1
Release:        3
Version:        2011.3
Url:            http://www.openstack.org
Summary:        Python bindings to the OS API
License:        Apache 2.0
Vendor:         Grid Dynamics Consulting Services, Inc.
Group:          Development/Languages/Python
Source0:        %{name}-%{version}.tar.gz
Source1:        %{name}.init
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildRequires:  python-devel python-setuptools
%if 0%{?with_doc}
BuildRequires:  python-sphinx >= 0.6.0 make
%endif
BuildArch:      noarch
Requires:       python-eventlet python-lxml python-paste python-sqlalchemy python-routes python-httplib2 python-paste-deploy start-stop-daemon python-webob python-setuptools python-passlib


%description
Authentication service - proposed for OpenStack


%if 0%{?with_doc}

%package doc
Summary:        Documentation for %{name}
Group:          Documentation
Requires:       %{name} = %{epoch}:%{version}-%{release}


%description doc
Documentation for %{name}.

%endif

%prep
%setup -q -n %{name}-%{version}
sed -i 's|sqlite:///keystone|sqlite:////var/lib/keystone/keystone|' etc/keystone.conf
sed -i "s|'tenant_name'|'tenantName'|" keystone/middleware/auth_token.py


%build
python setup.py build


%install
%__rm -rf %{buildroot}

%if 0%{?with_doc}
%__make -C doc/ html PYTHONPATH=%{_builddir}/%{name}-%{version}
%endif
python setup.py install --prefix=%{_prefix} --root=%{buildroot}
mv %{buildroot}/usr/bin/keystone{,-combined}

install -d -m 755 %{buildroot}%{_sysconfdir}/%{prj}
install -m 644 etc/* %{buildroot}%{_sysconfdir}/%{prj}
install -m 644 examples/paste/nova-api-paste.ini %{buildroot}%{_sysconfdir}/%{prj}

install -d -m 755 %{buildroot}%{_sharedstatedir}/keystone
install -d -m 755 %{buildroot}%{_localstatedir}/log/%{prj}
install -d -m 755 %{buildroot}%{_localstatedir}/run/%{prj}

install -p -D -m 755 %{SOURCE1} %{buildroot}%{_initrddir}/%{prj}

%__rm -rf %{buildroot}%{py_puresitedir}/{doc,examples,tools}


%clean
%__rm -rf %{buildroot}


%pre
getent passwd keystone >/dev/null || \
useradd -r -g nobody -G nobody -d %{_sharedstatedir}/%{prj} -s /sbin/nologin \
-c "OpenStack Keystone Daemon" keystone
exit 0


%preun
if [ $1 = 0 ] ; then
    /sbin/service %{prj} stop
    /sbin/chkconfig --del %{prj}
fi


%files
%defattr(-,root,root,-)
%doc README.md HACKING LICENSE
%{py_puresitedir}/%{mod_name}*
%{_usr}/bin/*
%dir %attr(0755, keystone, nobody) %{_sharedstatedir}/%{prj}
%dir %attr(0755, keystone, nobody) %{_localstatedir}/log/%{prj}
%dir %attr(0755, keystone, nobody) %{_localstatedir}/run/%{prj}
%config(noreplace) %{_sysconfdir}/keystone
%{_sysconfdir}/rc.d/init.d/*

%if 0%{?with_doc}
%files doc
%defattr(-,root,root,-)
%doc examples doc
%endif

%changelog
