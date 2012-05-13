"""

This file is part of the everest project. 
See LICENSE.txt for licensing, CONTRIBUTORS.txt for contributor information.

Created on May 8, 2012.
"""
from collections import defaultdict
import inspect

__docformat__ = 'reStructuredText en'
__all__ = ['RepresenterConfiguration',
           ]

# Configuration option name declarations.

_MAPPING_CONFIG_OPTION = 'mapping'
VALID_CONFIG_OPTIONS = []

IGNORE_OPTION = 'ignore'
IGNORE_ON_READ_OPTION = 'ignore_on_read'
IGNORE_ON_WRITE_OPTION = 'ignore_on_write'
WRITE_AS_LINK_OPTION = 'write_as_link'
REPR_NAME_OPTION = 'repr_name'
VALID_MAPPING_OPTIONS = [IGNORE_OPTION,
                         IGNORE_ON_READ_OPTION,
                         IGNORE_ON_WRITE_OPTION,
                         WRITE_AS_LINK_OPTION,
                         REPR_NAME_OPTION,
                         ]

class RepresenterConfiguration(object):
    """
    Class maintaining representer configuration options.

    At present, this can also be used as base class for containers declaring 
    representer configuration data as static class attributes. However, this
    usage is discouraged and should be replaced with the new ZCML based
    declaration syntax.

    Representer configuration objects maintain two kinds of configuration
    data:
    
    1) Generic options. These can be any key:value pairs. Derived 
       classes need to declare the names of valid option names in the 
       :cvar:`_config_options` class variable. 
    
    2) Mapping options. These are kept in a dictionary mapping the mapped
       attribute name to a dictionary of mapping options. Valid mapping 
       option name for a given attribute are:

       repr_name :
         The name to use for this attribute in the representation.
       write_as_link :
         Write this mapped attribute as a link rather than as a full
         representation.
       ignore_on_read:
         Ignore this attribute when reading a representation.
       ignore_on_write:
         Ignore this attribute when writing a representation.
       ignore :
         Ignore this attribute when creating a representation. This is short
         for setting both ignore_on_read and ignore_on_write
            
       Derived classes may add more allowed mapping options; the names of 
       these additional options must be declared in the 
       :cvar:`_mapping_option_names` class variable.
    """

    #: List of allowed configuration option names.
    _config_option_names = VALID_CONFIG_OPTIONS
    #: List of allowed mapping option names.
    _mapping_option_names = VALID_MAPPING_OPTIONS

    def __init__(self, options=None, mapping_options=None):
        # FIXME: remove this when old-style configuration classes are gone
        self.__options, self.__mapping_options = self.__build()
        if not options is None:
            for option_name, option_value in options.iteritems():
                self.set_option(option_name, option_value)
        if not mapping_options is None:
            for attr_name, attr_mp_options in mapping_options.iteritems():
                for mp_opt_name, mp_opt_value in attr_mp_options.iteritems():
                    self.set_mapping_option(attr_name,
                                            mp_opt_name, mp_opt_value)

    def get_option(self, name):
        """
        Returns the value for the specified generic configuration option.

        :returns: configuration option value or `None`, if the option was not
          set.
        """
        self.__validate_option_name(name)
        return self.__options.get(name, None)

    def set_option(self, name, value):
        """
        Sets the specified generich configuration option to the given value.
        """
        self.__validate_option_name(name)
        self.__options[name] = value

    def get_options(self):
        """
        Returns a copy of the generic configuration options
        """
        return self.__options.copy()

    def set_mapping_option(self, attribute_name, option_name, option_value):
        self.__validate_mapping_option_name(option_name)
        mp_options = self.__mapping_options.setdefault(attribute_name, {})
        mp_options[option_name] = option_value

    def get_mapping_option(self, attribute_name, option_name):
        self.__validate_mapping_option_name(option_name)
        return self.__mapping_options[attribute_name].get(option_name)

    def get_mapping_options(self, attribute_name=None):
        """
        Returns a copy of the mapping options for the given attribute name
        or a copy of all mapping options, if no attribute name is provided. 
        All options that were not explicitly configured are given a default 
        value of `None`.

        :returns: mapping options dictionary (including default `None` values)
        """
        if attribute_name is None:
            opts = defaultdict(self.__new_mapping_options)
            for attr, mp_options in self.__mapping_options.iteritems():
                opts[attr] = dict([(opt_name, mp_options.get(opt_name))
                                   for opt_name in self._mapping_option_names])
        else:
            attr_mp_options = self.__mapping_options[attribute_name]
            opts = dict([(opt_name, attr_mp_options.get(opt_name))
                         for opt_name in self._mapping_option_names])
        return opts

    def __new_mapping_options(self):
        return dict([(opt_name, None)
                     for opt_name in self._mapping_option_names])

    def __build(self):
        options = {}
        mapping_options = defaultdict(dict)
        for base in self.__class__.__mro__[::-1]:
            for attr, value in base.__dict__.items():
                # Ignore protected/private/magic class attributes.
                if attr.startswith('_'):
                    continue
                # Ignore attributes that are public methods.
                if inspect.isfunction(value):
                    continue
                # Validate all others.
                self.__validate_option_name(attr)
                # The mapping is updated rather than replaced.
                if attr == _MAPPING_CONFIG_OPTION:
                    # Check that all mapping option dictionaries have only
                    # valid option keys, then update.
                    for attr_name, attr_mp_options in value.iteritems():
                        for mp_opt_name in attr_mp_options.keys():
                            self.__validate_mapping_option_name(mp_opt_name)
                        mapping_options[attr_name].update(attr_mp_options)
                else:
                    options[attr] = value
        return options, mapping_options

    def __validate_option_name(self, name):
        if not (name in self._config_option_names
                or name == _MAPPING_CONFIG_OPTION):
            raise ValueError('Invalid configuration option name "%s" for '
                             '%s representer.' %
                             (name, self.__class__.__name__))

    def __validate_mapping_option_name(self, name):
        if not name in self._mapping_option_names:
            raise ValueError('Invalid mapping option name "%s" '
                             'for %s representer.'
                             % (name, self.__class__.__name__))

