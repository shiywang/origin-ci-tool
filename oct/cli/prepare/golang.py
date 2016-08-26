import click
from cli.prepare.isolated_install_options import isolated_install_options
from cli.prepare.playbooks_util import playbook_path
from cli.util.preset_option import Preset
from util.playbook_runner import PlaybookRunner


def install_golang_custom_callback(ctx, param, value):
    """
    Install Go on the remote host for a given OpenShift version.
    Handles the eager `--for` option.

    :param value: version of OpenShift for which to install Golang
    """
    if not value or ctx.resilient_parsing:
        return

    install_golang(version=golang_version_for_preset(value))
    ctx.exit()


def golang_version_for_preset(preset):
    """
    Determine the Golang version for a given preset.

    :param preset: version of OpenShift for which to install Golang
    :return: the Golang version to install
    """
    if preset in [Preset.origin_master, Preset.ose_master, Preset.ose_32, Preset.ose_321, Preset.ose_33]:
        return '1.6.2'
    else:
        raise click.UsageError('No Golang preset found for OpenShift version: %s' % preset)


@click.command(
    short_help='Install Golang on remote hosts.',
    help='''
Installs the Go toolchain and source on the remote host.

The Go install can be parameterized with the Go package version that
is required, as well as the existing RPM repositories and new RPM
repositories from the web to enable when installing it.

If repositories or repository URLs are given, they will be the only
repositories enabled when the Go install occurs. Any repositories
created from repository URLs will be registered only for the Go
install and will be removed after the fact.

If a preset is chosen, default values for the other options are used
and user-provided options are ignored.

\b
Examples:
  Install Go for a specific version of OpenShift
  $ oct prepare golang --for=ose/enterprise-3.3
\b
  Install a specific Go version present in default RPM repositories
  $ oct prepare golang --version=1.4.2
\b
  Install a specific Go version from an available custom RPM repository
  $ oct prepare golang --version=1.5.3 --repo=my-custom-golang-repo
\b
  Install a specific Go version from an RPM repository available on the web
  $ oct prepare golang --version=1.6.2 --repourl=myrepo.com/golang/x86_64/
'''
)
@isolated_install_options(
    package_name='Golang',
    preset_callback=install_golang_custom_callback
)
def golang(version, repos, repourls, preset):
    """
    Installs the Go toolchain and source on the remote host.

    :param version: version of Golang to install
    :param repos: list of RPM repositories from which to install Golang
    :param repourls: list of RPM repository URLs from which to install Golang
    :param preset: version of OpenShift for which to install Golang
    """
    install_golang(version, repos, repourls)


def install_golang(version, repos=None, repourls=None):
    """
    Install Go on the remote host.

    :param version: version of Golang to install
    :param repos: list of RPM repositories from which to install Golang
    :param repourls: list of RPM repository URLs from which to install Golang
    """
    vars = dict(
        origin_ci_golang_package='golang'
    )

    if version:
        vars['origin_ci_golang_package'] += '-' + version

    if repos:
        vars['origin_ci_golang_disabledrepos'] = '*'
        vars['origin_ci_golang_enabledrepos'] = ','.join(repos)

    if repourls:
        vars['origin_ci_golang_tmp_repourls'] = repourls

    PlaybookRunner().run(
        playbook_source=playbook_path('golang'),
        vars=vars
    )