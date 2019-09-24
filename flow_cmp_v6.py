"""
Copyright (c) 2019 IETF Trust and the persons identified as authors
of draft-ietf-idr-flow-spec-v6. All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, is permitted pursuant to, and subject to the license
terms contained in, the Simplified BSD License set forth in Section
4.c of the IETF Trust’s Legal Provisions Relating to IETF Documents
(http://trustee.ietf.org/license-info).
"""

import itertools
import collections
import ipaddress


EQUAL = 0
A_HAS_PRECEDENCE = 1
B_HAS_PRECEDENCE = 2
IP_DESTINATION = 1
IP_SOURCE = 2

FS_component = collections.namedtuple('FS_component', 'component_type value')


class FS_IPv6_prefix_component:
    def __init__(self, prefix, offset=0, component_type=IP_DESTINATION):
        self.offset = offset
        self.component_type = component_type
        # make sure if offset != 0 that non of the first offset bits
        # are set in the prefix
        self.value = prefix
        if offset != 0:
            i = ipaddress.IPv6Interface((self.value.network_address, offset))
            if i.network.network_address != ipaddress.ip_address('0::0'):
                raise ValueError('Bits set in the offset')


class FS_nlri(object):
    """
    FS_nlri class implementation that allows sorting.

    By calling .sort() on a array of FS_nlri objects these will be sorted
    according to the flow_rule_cmp algorithm.

    Example:
    nlri = [ FS_nlri(components=[
             FS_component(component_type=4, value=bytearray([0,1,2,3,4,5,6])),
             ]),
             FS_nlri(components=[
             FS_component(component_type=5, value=bytearray([0,1,2,3,4,5,6])),
             FS_component(component_type=6, value=bytearray([0,1,2,3,4,5,6])),
             ]),
           ]
    nlri.sort() # sorts the array accorinding to the algorithm
    """
    def __init__(self, components = None):
        """
        components: list of type FS_component
        """
        self.components = components

    def __lt__(self, other):
        # use the below algorithm for sorting
        result = flow_rule_cmp(self, other)
        if result == B_HAS_PRECEDENCE:
            return True
        else:
            return False


def flow_rule_cmp_v6(a, b):
    """
    Implementation of the flowspec sorting algorithm in draft-ietf-idr-flow-spec-v6.
    """
    for comp_a, comp_b in itertools.zip_longest(a.components,
                                           b.components):
        # If a component type does not exist in one rule
        # this rule has lower precedence
        if not comp_a:
            return B_HAS_PRECEDENCE
        if not comp_b:
            return A_HAS_PRECEDENCE
        # Higher precedence for lower component type
        if comp_a.component_type < comp_b.component_type:
            return A_HAS_PRECEDENCE
        if comp_a.component_type > comp_b.component_type:
            return B_HAS_PRECEDENCE
        # component types are equal -> type specific comparison
        if comp_a.component_type in (IP_DESTINATION, IP_SOURCE):
            if comp_a.offset < comp_b.offset:
                return A_HAS_PRECEDENCE
            if comp_a.offset < comp_b.offset:
                return B_HAS_PRECEDENCE
            # both components have the same offset
            # assuming comp_a.value, comp_b.value of type
            # ipaddress.IPv6Network
            # and the offset bits are reset to 0 (since they are not
            # represented in the NLRI)
            if comp_a.value.overlaps(comp_b.value):
                # longest prefixlen has precedence
                if comp_a.value.prefixlen > comp_b.value.prefixlen:
                    return A_HAS_PRECEDENCE
                if comp_a.value.prefixlen < comp_b.value.prefixlen:
                    return B_HAS_PRECEDENCE
                # components equal -> continue with next component
            elif comp_a.value > comp_b.value:
                return B_HAS_PRECEDENCE
            elif comp_a.value < comp_b.value:
                return A_HAS_PRECEDENCE
        else:
            # assuming comp_a.value, comp_b.value of type bytearray
            if len(comp_a.value) == len(comp_b.value):
                if comp_a.value > comp_b.value:
                    return B_HAS_PRECEDENCE
                if comp_a.value < comp_b.value:
                    return A_HAS_PRECEDENCE
                # components equal -> continue with next component
            else:
                common = min(len(comp_a.value), len(comp_b.value))
                if comp_a.value[:common] > comp_b.value[:common]:
                    return B_HAS_PRECEDENCE
                elif comp_a.value[:common] < comp_b.value[:common]:
                    return A_HAS_PRECEDENCE
                # the first common bytes match
                elif len(comp_a.value) > len(comp_b.value):
                    return A_HAS_PRECEDENCE
                else:
                    return B_HAS_PRECEDENCE
    return EQUAL
