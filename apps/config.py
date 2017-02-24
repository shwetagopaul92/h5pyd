##############################################################################
# Copyright by The HDF Group.                                                #
# All rights reserved.                                                       #
#                                                                            #
# This file is part of HSDS (HDF5 Scalable Data Service), Libraries and      #
# Utilities.  The full HSDS copyright notice, including                      #
# terms governing use, modification, and redistribution, is contained in     #
# the file COPYING, which can be found at the root of the source code        #
# distribution tree.  If you do not have access to this file, you may        #
# request a copy from help@hdfgroup.org.                                     #
##############################################################################
import os
import json

class Config:
    """
    User Config state
    """
    def __init__(self, config_file=None, **kwargs):
        self._cfg = {}
        if config_file:
            self._config_file = config_file
        else:
            self._config_file = ".hscfg"
        # process config file if found
        if os.path.isfile(self._config_file):
            line_number = 0
            with open(self._config_file) as f:
                for line in f:
                    line_number += 1
                    s = line.strip()
                    if not s:
                        continue
                    if s[0] == '#':
                        # comment line
                        continue
                    fields = s.split('=')
                    if len(fields) < 2:
                        print("config file: {} line: {} is not valid".format(self._config_file, line_number))
                        continue
                    k = fields[0].strip()
                    v = fields[1].strip()
                    self._cfg[k] = v
        # override any config values with environment variable if found
        for k in self._cfg.keys():
            if k.upper() in os.environ:
                print("using env override for :", k)
                self._cfg[k] = os.environ[k.upper()]

        # finally update any values that are passed in to the constructor
        for k in kwargs.keys():
            self._cfg[k] = kwargs[k]

    def __getitem__(self, name):
        """ Get a domain  """
        return self._cfg[name]

    def __delitem__(self, name):
        """ Delete option. """
        del self._cfg[name]

    def __len__(self):
        return len(self._cfg)
         
    def __iter__(self):
        """ Iterate over config names """
        keys = self._cfg.keys()
        for key in keys:
            yield key

    def __contains__(self, name):
        return name in self._cfg

    def __repr__(self):
        return json.dumps(self._cfg)

    def keys(self):
        return self._cfg.keys()



         
 

  
  