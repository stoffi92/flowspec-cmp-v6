import itertools
import collections
import ipaddress


EQUAL = 0
A_HAS_PRECEDENCE = 1
B_HAS_PRECEDENCE = 2
IP_DESTINATION = 1
IP_SOURCE = 2

FS_component = collections.namedtuple('FS_component', 'component_type value')


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


def flow_rule_cmp(a, b):
    """
    Implementation of the flowspec sorting algorithm in draft-ietf-idr-rfc5575bis-04.
    """
    for comp_a, comp_b in itertools.zip_longest(a.components, b.components):
        # If the types differ, the rule with lowest numeric type value has
        # higher precedence (and thus will match before) than the rule that
        # doesn't contain that component type.
        if not comp_a:
            return B_HAS_PRECEDENCE
        if not comp_b:
            return A_HAS_PRECEDENCE
        if comp_a.component_type < comp_b.component_type:
            return A_HAS_PRECEDENCE
        if comp_a.component_type > comp_b.component_type:
            return B_HAS_PRECEDENCE
        # If the component types are the same, then a type- specific comparison
        # is performed.
        if comp_a.component_type in (IP_DESTINATION, IP_SOURCE):
            # For IP prefix values (IP destination and source prefix) precedence
            # is given to the lowest IP value of the common prefix length; if
            # the common prefix is equal, then the most specific prefix has
            # precedence.

            # assuming comp_a.value, comp_b.value of type ipaddress
            if comp_a.value.overlaps(comp_b.value):
                # longest prefixlen has precedence
                if comp_a.value.prefixlen > comp_b.value.prefixlen:
                    return A_HAS_PRECEDENCE
                if comp_a.value.prefixlen < comp_b.value.prefixlen:
                    return B_HAS_PRECEDENCE
                # otherwise supernet the ip component is equal -
                # continue with next component
            elif comp_a.value > comp_b.value:
                return B_HAS_PRECEDENCE
            elif comp_a.value < comp_b.value:
                return A_HAS_PRECEDENCE
            # equal value cannot happen here since this is covered
            # in the branch(1) above
        else:
            # For all other component types, unless otherwise specified, the
            # comparison is performed by comparing the component data as a
            # binary string using the memcmp() function as defined by the ISO C
            # standard. For strings of different lengths, the common prefix is
            # compared.  If equal, the longest string is considered to have
            # higher precedence than the shorter one.

            # assuming comp_a.value, comp_b.value of type bytearray
            if len(comp_a.value) == len(comp_b.value):
                if comp_a.value > comp_b.value:
                    return B_HAS_PRECEDENCE
                if comp_a.value < comp_b.value:
                    return A_HAS_PRECEDENCE
                # otherwise this component is equal -
                # continue with next component
            else:
                common = min(len(comp_a.value), len(comp_b.value))
                if comp_a.value[:common] > comp_b.value[:common]:
                    return B_HAS_PRECEDENCE
                elif comp_a.value[:common] < comp_b.value[:common]:
                    return A_HAS_PRECEDENCE
                # the first common characters match, the longer string
                # has precedence
                elif len(comp_a.value) > len(comp_b.value):
                    return A_HAS_PRECEDENCE
                else:
                    return B_HAS_PRECEDENCE
    return EQUAL
