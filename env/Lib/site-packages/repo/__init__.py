# coding: utf-8

from typing import Dict, Any

_package_data: Dict[str, Any] = dict(
    full_package_name='repo',
    version_info=(0, 3, 0),
    __version__='0.3.0',
    version_timestamp='2022-10-12 09:07:41',
    author='Anthon van der Neut',
    author_email='a.van.der.neut@ruamel.eu',
    description='repo supports complex repository handling',
    keywords='pypi statistics',
    entry_points='repo=repo.__main__:main',
    # entry_points=None,
    license='Copyright Ruamel bvba 2007-2022',
    since=2022,
    # status='α|β|stable',  # the package status on PyPI
    # data_files="",
    # universal=True,  # py2 + py3
    # install_requires=['ruamel.std.pathlib', ],
    tox=dict(env='3',),  # *->all p->pypy
    python_requires='>=3',
)  # NOQA


version_info = _package_data['version_info']
__version__ = _package_data['__version__']


_cligen_data = """\
# all tags start with an uppercase char and can often be shortened to three and/or one
# characters. If a tag has multiple uppercase letter, only using the uppercase letters is a
# valid shortening
# Tags used:
# !Commandlineinterface, !Cli,
# !Option, !Opt, !O
  # - !Option [all, !Action store_true, !Help build sdist and wheels for all platforms]
# !PreSubparserOption, !PSO
# !Alias for a subparser
# - !DefaultSubparser  # make this (one) subparser default
# !Help, !H
# !HelpWidth 40    # width of the left side column width option details
# !Argument, !Arg
  # - !Arg [files, !Nargs '*', !H files to process]
# !Module   # make subparser function calls imported from module
# !Instance # module.Class: assume subparser method calls on instance of Class imported from module
# !Main     # function to call/class to instantiate, no subparsers
# !Action # either one of the actions in cligen subdir _action (by stem of the file) or e.g. "store_action"
# !Nargs, !N
#    provide a number, '?', '*', or +. Special code is inserted to allow for defaults when +
# !Config YAML/INI/PON  read defaults from config file
# !AddDefaults ' (default: %(default)s)'
# !Prolog (sub-)parser prolog/description text (for multiline use | ), used as subparser !Help if not set
# !Epilog (sub-)parser epilog text (for multiline use | )
# !NQS used on arguments, makes sure the scalar is non-quoted e.g for instance/method/function
#      call arguments, when cligen knows about what argument a keyword takes, this is not needed
!Cli 0:
- !Instance repo.repo.Repo
- !AddDefaults ' (default: %(default)s)'
- !Option [verbose, v, !Help increase verbosity level, !Action count]
# - !Option [distbase, !Help 'base directory for all distribution files']
# - !Config YAML
# - !PSO [config, !Help configuration file location']
- show:
  - !DefaultSubparser
  - !Help execute show related commands
# - !Option [all, !Action store_true, !Help build sdist and wheels for all platforms]
# - !Option [linux, !Action store_true, !Help build linux wheels using manylinux]
# - !Arg [args, !Nargs: '*', !H you have to do this]
# - !Prolog 'Prolog for the parser'
# - !Epilog 'Epilog for the parser'
"""
