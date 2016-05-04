"""
Code for building source-to-image
"""

import sys
import json

from tito.common import (
    get_latest_commit,
    get_latest_tagged_version,
    check_tag_exists,
    run_command,
    find_spec_file,
    get_spec_version_and_release,
    munge_specfile
)

from tito.builder import Builder

class S2IBuilder(Builder):
    """
    builder which defines 'commit' as the git hash prior to building

    Used For:
        - Packages that want to know the commit in all situations
    """

    def _setup_test_specfile(self):
        if self.test and not self.ran_setup_test_specfile:
            # If making a test rpm we need to get a little crazy with the spec
            # file we're building off. (note that this is a temp copy of the
            # spec) Swap out the actual release for one that includes the git
            # SHA1 we're building for our test package:
            sha = self.git_commit_id[:7]
            fullname = "{0}-{1}".format(self.project_name, self.display_version)
            munge_specfile(
                self.spec_file,
                sha,
                self.commit_count,
                fullname,
                self.tgz_filename,
            )

            # Custom s2i stuff follows, everything above is the standard
            # builder

            # set ldflags in spec
            cmd = '. ./hack/common.sh ; echo $(sti::build::ldflags)'
            ldflags = run_command("bash -c '{0}'".format(cmd))
            print("LDFLAGS::{0}".format(ldflags))
            update_ldflags = \
                    "sed -i 's|^%global ldflags .*$|%global ldflags {0}|' {1}".format(
                        ' '.join([ldflag.strip() for ldflag in ldflags.split()]),
                        self.spec_file
                    )
            print(run_command(update_ldflags))

            # Add bundled deps for Fedora Guidelines as per:
            # https://fedoraproject.org/wiki/Packaging:Guidelines#Bundling_and_Duplication_of_system_libraries
            provides_list = []
            with open("./Godeps/Godeps.json") as godeps:
                depdict = json.load(godeps)
                for bdep in [
                    (dep[u'ImportPath'], dep[u'Rev'])
                    for dep in depdict[u'Deps']
                ]:
                    provides_list.append(
                        "Provides: bundled(golang({0})) = {1}".format(
                            bdep[0],
                            bdep[1]
                        )
                    )
            update_provides_list = \
                "sed -i 's|^### AUTO-BUNDLED-GEN-ENTRY-POINT|{0}|' {1}".format(
                    '\\n'.join(provides_list),
                    self.spec_file
                )
            print(run_command(update_provides_list))

            self.build_version += ".git." + \
                str(self.commit_count) + \
                "." + \
                str(self.git_commit_id[:7])
            self.ran_setup_test_specfile = True

# vim:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:textwidth=0:
