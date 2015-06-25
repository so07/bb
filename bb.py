#!/usr/bin/env python
import os
import argparse
import subprocess
import ConfigParser

import argconfig

ConfigFromFile = argconfig.argconfig

class bb(dict):

    metakey = {
                'INSTALLDIR' : 'install_dir',
                'BUILDDIR' : 'build_dir',
                'SOURCEDIR' : 'source_dir',
                'MODULEDIR' : 'module_dir',
                'MODULEFILE' : 'module_file',
              }

    def __init__ (self, *args, **kwargs):

       # from *args
       for d in args:
          for key, value in d.items():
             self[key] = value

       # from **kwargs
       for key, value in kwargs.items():
          self[key] = value


       if self['read_from_config']:
          key_to_update = self._get_options(self['name'])
          for k in key_to_update:
              self[k] = self._get_key(self['name'], k)

       if self['read_from_config']:
          self['session'] = self['session'].split()

       self.update({k:v for k,v in kwargs.iteritems() if v})


       if self.get('version'):
           _version = [None, None, None]
           for i, item in enumerate(self['version'].split('.')):
               _version[i] = item
           self['major'], self['minor'], self['patch'] = _version


       self['version']      = ".".join([i for i in self['major'], self['minor'] if i])
       self['version_full'] = ".".join([i for i in self['major'], self['minor'], self['patch'] if i])

       self['name_version'] = "%s-%s" % (self['name'], self['version'])
       self['name_version_full'] = "%s-%s" % (self['name'], self['version_full'])

       self['source_dir'] = os.path.join( self['source_dir_base'], self['name_version_full'] )
       self['build_dir'] = os.path.join( self['build_dir_base'], self['name_version_full'] )
       self['install_dir'] = os.path.join( self['install_dir_base'], self['name_version'] )

       # module
       self['module_dir'] = os.path.join( self['module_dir_base'], self['name'] )
       self['module_file'] = os.path.join( self['module_dir'], self['version'] )


       if self['read_from_config']:
           for k in key_to_update:
               self[k] = self._sub_metakey(self[k])


       for k in ['source_dir', 'build_dir', 'install_dir', 'module_dir']:
           d = self[k]
           if not os.path.exists(d):
               os.makedirs(d)


    def _sub_metakey(self, value):
        for str_old, str_new in self.metakey.items():
            if str_old in value:
               value = value.replace(str_old, self[str_new])
        return value

    def _get_options(self, section):
        l = []
        for file_cfg in ConfigFromFile.get_file_list():
            cp = ConfigParser.SafeConfigParser(allow_no_value=True)
            cp.read( file_cfg )
            l.extend(cp.options(section))
        return l

    def _get_key(self, section, key):
        value = None
        for file_cfg in ConfigFromFile.get_file_list():
            cp = ConfigParser.SafeConfigParser(allow_no_value=True)
            cp.read( file_cfg )
            try:
               value = cp.get(section, key)
            except ConfigParser.NoOptionError:
               pass
        return value

    def __str__(self):
      s='\n'
      for k, v in sorted(self.items()):
          s += "%s %s\n" % (k.ljust(20, '.'), v)
      return s

    def __call__(self):
        for todo in self['session']:
            print "#", getattr(self, todo).__name__
            getattr(self, todo)()

    def download(self):
        # go to source-dir
        os.chdir(self['source_dir'])
        print "cd ", self['source_dir']
        print self['download']
        subprocess.call(self['download'], shell=True)

    def build(self):
        os.chdir(self['build_dir'])
        print "cd ", self['build_dir']
        print self['build']
        subprocess.call(self['build'], shell=True)

    def install(self):
        os.chdir(self['build_dir'])
        print "cd ", self['build_dir']
        print self['install']
        subprocess.call(self['install'], shell=True)

    def module(self):
        print self['module']
        subprocess.call(self['module'], shell=True)
        pass


def main():

   parser = argparse.ArgumentParser(prog='bb',
                                    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

   parser.add_argument('-n', '--name',
                       dest = 'name',
                       help = '')

   parser.add_argument('-v', '--version',
                       dest = 'version',
                       help = '')

   parser.add_argument('-M', '--major',
                       dest = 'major',
                       help = '')

   parser.add_argument('-m', '--minor',
                       dest = 'minor',
                       help = '')

   parser.add_argument('-p', '--patch',
                       dest = 'patch',
                       help = '')

   parser.add_argument('-c', '--config',
                       dest = 'read_from_config',
                       action = 'store_true',
                       help = '')

   parser.add_argument('--session',
                       dest = 'session',
                       choices = ['download', 'build', 'install'],
                       nargs = '+',
                       default = [],
                       help = '')

   parser.add_argument('--download',
                       dest = 'download',
                       help = '')

   parser.add_argument('--build',
                       dest = 'build',
                       help = '')

   parser.add_argument('--install',
                       dest = 'install',
                       help = '')

   parser.add_argument('--source-dir',
                       dest = 'source_dir_base',
                       default = os.path.join( os.getcwd(), 'source'),
                       action = ConfigFromFile,
                       argkey = 'source-dir',
                       section = 'directory',
                       help = '')

   parser.add_argument('--build-dir',
                       dest = 'build_dir_base',
                       default = os.path.join( os.getcwd(), 'build'),
                       action = ConfigFromFile,
                       argkey = 'build-dir',
                       section = 'directory',
                       help = '')

   parser.add_argument('--install-dir',
                       dest = 'install_dir_base',
                       default = os.path.join( os.getcwd(), 'install'),
                       action = ConfigFromFile,
                       argkey = 'install-dir',
                       section = 'directory',
                       help = '')

   parser.add_argument('--module-dir',
                       dest = 'module_dir_base',
                       default = os.path.join( os.getcwd(), 'module'),
                       action = ConfigFromFile,
                       argkey = 'module-dir',
                       section = 'directory',
                       help = '')

   args = parser.parse_args()

   b = bb(**vars(args))

   b()



if __name__ == "__main__":
    main()

