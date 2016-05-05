#debuginfo not supported with Go
%global debug_package %{nil}
# modifying the Go binaries breaks the DWARF debugging
%global __os_install_post %{_rpmconfigdir}/brp-compress

%global gopath      %{_datadir}/gocode

%global import_path github.com/openshift/source-to-image

%global ldflags PLACEHOLDER_REPLACED_BY_TITO

%global commit c99ef8b29e94bdaf62d5d5aefa74d12af6d37e3

# docker_version is the version of docker requires by packages
%global docker_version 1.6

Name:           source-to-image
# Version is not kept up to date and is intended to be set by tito custom
# builders provided in the .tito/lib directory of this project
Version:        0.0.3
Release:        1%{?dist}
Summary:        source-to-image (s2i) a tool for building reproducible Docker images.
License:        ASL 2.0
URL:            https://github.com/openshift/%{name}
ExclusiveArch:  x86_64
Source0:        https://%{import_path}/archive/v%{version}.tar.gz
BuildRequires:  systemd
BuildRequires:  golang >= 1.4
Requires:       docker >= %{docker_version}
Requires:       iptables

#
# The following Bundled Provides entries are populated automatically by the
# OpenShift source-to-image tito custom builder found here:
#   https://github.com/openshift/source-to-image/blob/master/.tito/lib/s2i/builder/
#
# These are defined as per:
# https://fedoraproject.org/wiki/Packaging:Guidelines#Bundling_and_Duplication_of_system_libraries
#
### AUTO-BUNDLED-GEN-ENTRY-POINT

%description
Source-to-image (s2i) is a tool for building reproducible Docker images. s2i
produces ready-to-run images by injecting source code into a Docker image and
assembling a new Docker image which incorporates the builder image and built
source. The result is then ready to use with docker run. s2i supports
incremental builds which re-use previously downloaded dependencies, previously
built artifacts, etc.

%prep
%setup -q -n %{name}-%{version}

%build

# Gaming the GOPATH because bundled libs in golang
mkdir _build
pushd _build
    mkdir -p src/github.com/openshift
    ln -s $(dirs +1 -l) src/%{import_path}
popd

mkdir _thirdpartylibs
pushd _thirdpartylibs
    ln -s \
        $(dirs +1 -l)/Godeps/_workspace/src/ \
        src
popd

export GOPATH=$(pwd)/_build:$(pwd)/_thirdpartylibs:%{buildroot}%{gopath}:%{gopath}

for cmd in s2i
do
    go install -ldflags "%{ldflags}" %{import_path}/cmd/${cmd}
done

%install

install -d -m 755 %{buildroot}%{_bindir}
# Install components
for bin in s2i
do
  echo "+++ INSTALLING ${bin}"
  install -p -m 755 _build/bin/${bin} %{buildroot}%{_bindir}/${bin}
done

install -d -m 755 %{buildroot}%{_sysconfdir}/bash_completion.d
install -p -m 644 contrib/bash/s2i %{buildroot}%{_sysconfdir}/bash_completion.d/s2i

%check
go test

%files
%doc README.md CONTRIBUTING.md AUTHORS
%license LICENSE
%{_bindir}/s2i
%{_sysconfdir}/bash_completion.d/s2i

%changelog
* Wed May 04 2016 Adam Miller <maxamillion@fedoraproject.org> 0.0.3-1
- Automatic commit of package [source-to-image] release [0.0.2-1].
  (maxamillion@fedoraproject.org)

* Wed May 04 2016 Adam Miller <maxamillion@fedoraproject.org> 0.0.2-1
- new package built with tito

* Wed May 04 2016 Adam Miller <maxamillion@fedoraproject.org> - 0.0.1-1
- First package build
