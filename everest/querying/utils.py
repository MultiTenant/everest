"""
This file is part of the everest project. 
See LICENSE.txt for licensing, CONTRIBUTORS.txt for contributor information.

Created on Dec 19, 2011.
"""

from everest.entities.attributes import EntityAttributeKinds
from everest.querying.interfaces import IFilterSpecificationFactory
from everest.querying.interfaces import IOrderSpecificationFactory
from pyramid.threadlocal import get_current_registry
from sqlalchemy.orm.interfaces import MANYTOMANY
from sqlalchemy.orm.interfaces import MANYTOONE
from sqlalchemy.orm.interfaces import ONETOMANY

__docformat__ = 'reStructuredText en'
__all__ = ['OrmAttributeInspector',
           'get_filter_specification_factory',
           'get_order_specification_factory',
           ]


def get_filter_specification_factory():
    """
    Returns the object registered as filter specification factory utility.
    
    :returns: object implementing 
        :class:`everest.querying.interfaces.IFilterSpecificationFactory
    """
    reg = get_current_registry()
    return reg.getUtility(IFilterSpecificationFactory)


def get_order_specification_factory():
    """
    Returns the object registered as order specification factory utility.
    
    :returns: object implementing 
        :class:`everest.querying.interfaces.IOrderSpecificationFactory
    """
    reg = get_current_registry()
    return reg.getUtility(IOrderSpecificationFactory)


class OrmAttributeInspector(object):
    """
    Helper class inspecting class attributes mapped by the ORM.
    """

    __cache = {}

    def __init__(self, orm_class):
        """
        :param orm_class: ORM class to inspect mapped attributes of.
        """
        self.__orm_class = orm_class

    @staticmethod
    def inspect(orm_class, attribute_name):
        """
        :param attribute_name: name of the mapped attribute to inspect.
        :returns: list of 2-tuples containing information about the inspected
          attribute (first element: mapped entity attribute kind; second 
          attribute: mapped entity attribute) 
        """
        key = (orm_class, attribute_name)
        elems = OrmAttributeInspector.__cache.get(key)
        if elems is None:
            elems = OrmAttributeInspector.__inspect(key)
            OrmAttributeInspector.__cache[key] = elems
        return elems

    @staticmethod
    def __inspect(key):
        orm_class, attribute_name = key
        elems = []
        entity_type = orm_class
        ent_attr_tokens = attribute_name.split('.')
        count = len(ent_attr_tokens)
        for idx, ent_attr_token in enumerate(ent_attr_tokens):
            entity_attr = getattr(entity_type, ent_attr_token)
            kind, attr_type = OrmAttributeInspector.__classify(entity_attr)
            if idx == count - 1:
                # We are at the last name token - this must be a TERMINAL
                # or an ENTITY.
                if kind == EntityAttributeKinds.AGGREGATE:
                    raise ValueError('Invalid attribute name "%s": the '
                                     'last element (%s) references an '
                                     'aggregate attribute.'
                                     % (attribute_name, ent_attr_token))
            else:
                if kind == EntityAttributeKinds.TERMINAL:
                    # We should not get here - the last attribute was a
                    # terminal.
                    raise ValueError('Invalid attribute name "%s": the '
                                     'element "%s" references a terminal '
                                     'attribute.'
                                     % (attribute_name, ent_attr_token))
                entity_type = attr_type
            elems.append((kind, entity_attr))
        return elems

    @staticmethod
    def __classify(attr):
        # Looks up the entity attribute kind and target type for the given
        # entity attribute.
        # We look for an attribute "property" to identify mapped attributes
        # (instrumented attributes and attribute proxies).
        if not hasattr(attr, 'property'):
            raise ValueError('Attribute "%s" is not mapped.' % attr)
        # We detect terminals by the absence of an "argument" attribute of
        # the attribute's property.
        if not hasattr(attr.property, 'argument'):
            kind = EntityAttributeKinds.TERMINAL
            target_type = None
        else: # We have a relationship.
            target_type = attr.property.argument
            if attr.property.direction in (ONETOMANY, MANYTOMANY):
                if not attr.property.uselist:
                    # 1:1
                    kind = EntityAttributeKinds.ENTITY
                else:
                    kind = EntityAttributeKinds.AGGREGATE
            elif attr.property.direction == MANYTOONE:
                kind = EntityAttributeKinds.ENTITY
            else:
                raise ValueError('Unsupported relationship direction "%s".'
                                 % attr.property.direction)
        return kind, target_type
