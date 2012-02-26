#
# spec file for package python-lettuce
#
# Copyright (c) 2011 SUSE LINUX Products GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.
#
# Please submit bugfixes or comments via http://bugs.opensuse.org/
#

Name:           python-lettuce
Version:        0.1.34
Release:        gd
Url:            http://github.com/gabrielfalcao/lettuce
Summary:        Behaviour Driven Development for python
License:        GPL
Group:          Development/Languages/Python
Source:         lettuce-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildRequires:  python-devel
BuildRequires:  python-lxml
BuildRequires:  python-setuptools
BuildRequires:  python-mox
BuildRequires:  python-nose
BuildRequires:  python-sphinx
BuildRequires:  python-tornado
Requires:       Django >= 1.1.1
Requires:       python-lxml python-setuptools python-mox python-nose python-sphinx python-tornado
BuildArch:      noarch

%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

%description
lettuce is a behaviour driven development module in the spirit of cucumber.

%prep
%setup -q -n lettuce-%{version}

%build
export CFLAGS="%{optflags}"
python setup.py build

%install
python setup.py install --prefix=%{_prefix} --root=%{buildroot} --record=INSTALLED_FILES.txt

%clean
rm -rf %{buildroot}

%files -f INSTALLED_FILES.txt
%defattr(-,root,root,-)
%{python_sitelib}/lettuce

%changelog
* Sun Feb 26 2012 skosyrev@griddynamics.com
- Updated to 0.1.34
  * Fetched from upstream at commit 6ca571b47
* Mon Aug 29 2011 toms@suse.de
- Updated to 0.1.32
  * Closed issue#138
  * Closed issue#166
  * Merge pull request issue#164 (0.1.31)
  * Merge pull request issue#161
  * Merge pull request issue#159
  * Improved docs (0.1.30)
  * Using multiprocessing instead of threading (0.1.29)
  * Closed issue#150 (0.1.28)
  * Merge pull request issue#153
  * Merge pull request issue#151
  * Added Japanese support
  * Merge pull request issue#141
  * Merge pll request issue#136
* Fri Jul 22 2011 toms@suse.de
- Initial version 0.1.27
