#!/usr/bin/env python
import os
import shutil
import argparse
import subprocess
import ConfigParser
import logging

import argconfig
import config

ConfigFromFile = argconfig.argconfig
ConfigFromFile.add_path( os.path.join( os.path.expanduser('~'),  '.bb') )

class bb(dict):

    metakey = {
                'INSTALLDIR' : 'install_dir',
                'BUILDDIR' : 'build_dir',
                'SOURCEDIR' : 'source_dir',
                'MODULEDIR' : 'module_dir',
                'MODULEFILE' : 'module_file',
              }

    keys_directory = ['source_dir', 'build_dir', 'install_dir', 'module_dir']

    def __init__ (self, *args, **kwargs):

       # from *args
       for d in args:
          for key, value in d.items():
             self[key] = value

       # from **kwargs
       for key, value in kwargs.items():
          self[key] = value

       # logger
       self._logger = self._set_logger()

       if self['read_from_config']:
          key_to_update = self._get_options(self['name'])
          # remove name from key_to_update
          key_to_update.remove('name')
          for k in key_to_update:
              self[k] = self._get_key(self['name'], k)

       if self['read_from_config']:
          self['session'] = self['session'].split()

       self.update({k:v for k,v in kwargs.iteritems() if v})

       if self['read_from_config']:
           if 'name' in self._get_options(self['name']):
               self['name'] = self._get_key(self['name'], 'name')

       if self.get('version'):
           _version = [None, None, None]
           for i, item in enumerate(self['version'].split('.')):
               _version[i] = item
           self['major'], self['minor'], self['patch'] = _version


       self['version']      = ".".join([i for i in self['major'], self['minor'] if i])
       self['version_full'] = ".".join([i for i in self['major'], self['minor'], self['patch'] if i])

       self['name_version'] = "%s-%s" % (self['name'], self['version'])
       self['name_version_full'] = "%s-%s" % (self['name'], self['version_full'])

       self['source_dir'] = os.path.join( self['source_dir_base'], self['name'], self['name_version_full'] )
       self['build_dir'] = os.path.join( self['build_dir_base'], self['name'], self['name_version_full'] )
       self['install_dir'] = os.path.join( self['install_dir_base'], self['name'], self['version_full'] )

       # module
       self['module_dir'] = os.path.join( self['module_dir_base'], self['name'] )
       self['module_file'] = os.path.join( self['module_dir'], self['version'] )


       if self['read_from_config']:
           for k in key_to_update:
               self[k] = self._sub_metakey(self[k])


    def __str__(self):
      s='\n'
      for k, v in sorted(self.items()):
          s += "%s %s\n" % (k.ljust(20, '.'), v)
      return s

    def __call__(self):
        for todo in self['session']:
            print "#", getattr(self, todo).__name__
            getattr(self, todo)()


    def _set_logger(self):
        """Define logger."""

        _format = "# [BB] %(message)s"

        _logger = logging.getLogger()
        _formatter = logging.Formatter(_format)
        _logger.setLevel(logging.DEBUG)
        stream_log_handler = logging.StreamHandler()
        stream_log_handler.setFormatter(_formatter)
        _logger.addHandler(stream_log_handler)

        return _logger

    def _sub_metakey(self, value):
        """Substitute metakey with key of packege."""
        for str_old, str_new in self.metakey.items():
            if str_old in value:
               value = value.replace(str_old, self[str_new])
        return value

    def get_sections(self):
        """Return all sections from config files."""
        l = []
        for file_cfg in ConfigFromFile.get_file_list():
            cp = ConfigParser.SafeConfigParser(allow_no_value=True)
            cp.read( file_cfg )
            l.extend(cp.sections())
        return l

    def _get_options(self, section):
        """Return all keys in section from config files."""
        l = []
        for file_cfg in ConfigFromFile.get_file_list():
            cp = ConfigParser.SafeConfigParser(allow_no_value=True)
            cp.read( file_cfg )
            l.extend(cp.options(section))
        return l

    def _get_key(self, section, key):
        """Return value of key in section from config files."""
        value = None
        for file_cfg in ConfigFromFile.get_file_list():
            cp = ConfigParser.SafeConfigParser(allow_no_value=True)
            cp.read( file_cfg )
            try:
               value = cp.get(section, key)
            except ConfigParser.NoOptionError:
               pass
        return value

    def _chdir(self, dir_, remove=True):
        """Make and change directory.
           If directory already exists remove it.
        """
        if os.path.isdir(dir_) and remove:
           shutil.rmtree(dir_)
           os.makedirs(dir_)
        print "cd ", dir_
        os.chdir(dir_)

    def _make_dirs(self):
        """Make package directories."""
        for k in self.keys_directory:
            d = self[k]
            if not os.path.exists(d):
                os.makedirs(d)

    def _remove_dirs(self):
        """Remove package directories."""
        for k in self.keys_directory:
            d = self[k]
            if os.path.exists(d):
                shutil.rmtree(d)

    def download(self):
        """Execute procedure to download package."""
        self._logger.info(self['download'])
        # go to source-dir
        self._chdir(self['source_dir'], remove=True)
        subprocess.call(self['download'], shell=True)

    def build(self):
        """Execute procedure to build package."""
        self._logger.info(self['build'])
        # go to build-dir
        self._chdir(self['build_dir'])
        subprocess.call(self['build'], shell=True)

    def install(self):
        """Execute procedure to install package."""
        self._logger.info(self['install'])
        # go to build-dir
        self._chdir(self['build_dir'], remove=False)
        subprocess.call(self['install'], shell=True)

    def module(self):
        """Execute procedure to make module of package."""
        self._logger.info(self['module'])
        subprocess.call(self['module'], shell=True)

    def remove(self):
        """Execute procedure to remove package."""
        self._remove_dirs()


def main():

   parser = argparse.ArgumentParser(prog='bb',
                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)


   parser.add_argument('--bb-version', action='version',
                       version='%(prog)s ' + config.version,
                       help='Print bb version.')


   parser_package = parser.add_argument_group('package options')

   parser_package.add_argument('-n', '--name',
                               dest = 'name',
                               default = '',
                               help = 'Name of package.')

   parser_package.add_argument('-v', '--version',
                               dest = 'version',
                               help = 'Version of package (Major.Minor.Patch).')

   parser_package.add_argument('-M', '--major',
                               dest = 'major',
                               help = 'Major version.')

   parser_package.add_argument('-m', '--minor',
                               dest = 'minor',
                               help = 'Minor version.')

   parser_package.add_argument('-p', '--patch',
                               dest = 'patch',
                               help = 'Patch revision.')

   parser_package.add_argument('--remove',
                               dest = 'remove',
                               action = 'store_true',
                               help = 'Remove module.')


   parser_config = parser.add_argument_group('configuration file options')

   parser_config.add_argument('-c', '--config',
                              dest = 'read_from_config',
                              action = 'store_true',
                              help = 'Read package settings from configuration file.')

   parser_config.add_argument('-l', '--list',
                              dest = 'list_from_config',
                              action = 'store_true',
                              help = 'List package settings from configuration file.')


   parser_procedure = parser.add_argument_group('procedure options')

   parser_procedure.add_argument('--session',
                                 dest = 'session',
                                 choices = ['download', 'build', 'install', 'module'],
                                 nargs = '+',
                                 default = [],
                                 help = 'Define steps to follow for installing package.')

   parser_procedure.add_argument('--download',
                                 dest = 'download',
                                 help = 'Define procedure to download package.')

   parser_procedure.add_argument('--build',
                                 dest = 'build',
                                 help = 'Define proceure to build package.')

   parser_procedure.add_argument('--install',
                                 dest = 'install',
                                 help = 'Define procedure to install package')

   parser_procedure.add_argument('--module',
                                 dest = 'module',
                                 help = 'Define procedure for module file of package.')


   parser_directory = parser.add_argument_group('directory options')

   parser_directory.add_argument('--source-dir',
                                 dest = 'source_dir_base',
                                 default = os.path.join( os.getcwd(), 'source'),
                                 action = ConfigFromFile,
                                 argkey = 'source-dir',
                                 section = 'directory',
                                 help = 'Base directory for sources.')

   parser_directory.add_argument('--build-dir',
                                 dest = 'build_dir_base',
                                 default = os.path.join( os.getcwd(), 'build'),
                                 action = ConfigFromFile,
                                 argkey = 'build-dir',
                                 section = 'directory',
                                 help = 'Base directory for builds.')

   parser_directory.add_argument('--install-dir',
                                 dest = 'install_dir_base',
                                 default = os.path.join( os.getcwd(), 'install'),
                                 action = ConfigFromFile,
                                 argkey = 'install-dir',
                                 section = 'directory',
                                 help = 'Base directory for installs.')

   parser_directory.add_argument('--module-dir',
                                 dest = 'module_dir_base',
                                 default = os.path.join( os.getcwd(), 'module'),
                                 action = ConfigFromFile,
                                 argkey = 'module-dir',
                                 section = 'directory',
                                 help = 'Base directory for module files.')

   args = parser.parse_args()


   b = bb(**vars(args))


   if args.list_from_config:
      packs = b.get_sections()
      print "\n".join(packs)

   elif args.remove:
      b.remove()

   else:
      b()



if __name__ == "__main__":
    main()

