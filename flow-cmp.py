
#python 3 example
import itertools
import collections
import ipaddress
from IPython import embed
import unittest

FS_component = collections.namedtuple('FS_component', 'component_type value')
FS_nlri = collections.namedtuple('FS_nlri', 'components')

EQUAL = 0
A_HAS_PRECEDENCE = 1
B_HAS_PRECEDENCE = 2
IP_DESTINATION = 1
IP_SOURCE = 2


def flow_rule_cmp(a, b):
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
            common = min(comp_a.value.prefixlen,comp_b.value.prefixlen)
            print ('common %i' % common)
            #embed()
            if comp_a.value.supernet(new_prefix=common) == comp_b.value.supernet(new_prefix=common): #(1)
                # longest prefixlen has precedence
                print('prefixlen-compare')
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


class TestFlowCmp(unittest.TestCase):
    def test_different_listlength(self):
        a = FS_nlri(components=[
            FS_component(component_type=4, value=bytearray([0,1,2,3,4,5,6])),
            FS_component(component_type=5, value=bytearray([0,1,2,3,4,5,6])),
            ])
        b = FS_nlri(components=[
            FS_component(component_type=4, value=bytearray([0,1,2,3,4,5,6])),
            ])
        self.assertEqual(flow_rule_cmp(a, b), A_HAS_PRECEDENCE)
        a, b = b, a
        self.assertEqual(flow_rule_cmp(a, b), B_HAS_PRECEDENCE)

    def test_different_component_types(self):
        a = FS_nlri(components=[
            FS_component(component_type=4, value=bytearray([0,1,2,3,4,5,6])),
            ])
        b = FS_nlri(components=[
            FS_component(component_type=5, value=bytearray([0,1,2,3,4,5,6])),
            FS_component(component_type=6, value=bytearray([0,1,2,3,4,5,6])),
            ])
        self.assertEqual(flow_rule_cmp(a, b), A_HAS_PRECEDENCE)
        a, b = b, a
        self.assertEqual(flow_rule_cmp(a, b), B_HAS_PRECEDENCE)

    def test_equal_fs(self):
        a = FS_nlri(components=[
            FS_component(component_type=IP_DESTINATION, value=ipaddress.ip_network('10.1.0.0/16') ),
            FS_component(component_type=IP_SOURCE, value=ipaddress.ip_network('10.2.0.0/16') ),
            FS_component(component_type=4, value=bytearray([0,1,2,3,4,5,6])),
            FS_component(component_type=5, value=bytearray([0,1,2,3,4,5,6])),
            ])
        b = FS_nlri(components=[
            FS_component(component_type=IP_DESTINATION, value=ipaddress.ip_network('10.1.0.0/16') ),
            FS_component(component_type=IP_SOURCE, value=ipaddress.ip_network('10.2.0.0/16') ),
            FS_component(component_type=4, value=bytearray([0,1,2,3,4,5,6])),
            FS_component(component_type=5, value=bytearray([0,1,2,3,4,5,6])),
            ])
        self.assertEqual(flow_rule_cmp(a, b), EQUAL)

    def test_ip_prefix_same_common(self):
        a = FS_nlri(components=[
            FS_component(component_type=IP_DESTINATION, value=ipaddress.ip_network('10.0.0.0/8') ),
            ])
        b = FS_nlri(components=[
            FS_component(component_type=IP_DESTINATION, value=ipaddress.ip_network('10.1.0.0/16') ),
            ])
        self.assertEqual(flow_rule_cmp(a, b), B_HAS_PRECEDENCE)
        a, b = b, a
        self.assertEqual(flow_rule_cmp(a, b), A_HAS_PRECEDENCE)
        a = FS_nlri(components=[
            FS_component(component_type=IP_SOURCE, value=ipaddress.ip_network('10.0.0.0/8') ),
            ])
        b = FS_nlri(components=[
            FS_component(component_type=IP_SOURCE, value=ipaddress.ip_network('10.1.0.0/16') ),
            ])
        self.assertEqual(flow_rule_cmp(a, b), B_HAS_PRECEDENCE)
        a, b = b, a
        self.assertEqual(flow_rule_cmp(a, b), A_HAS_PRECEDENCE)

    def test_ip_prefix_different_common(self):
        a = FS_nlri(components=[
            FS_component(component_type=IP_DESTINATION, value=ipaddress.ip_network('10.0.0.0/8') ),
            ])
        b = FS_nlri(components=[
            FS_component(component_type=IP_DESTINATION, value=ipaddress.ip_network('11.1.0.0/16') ),
            ])
        self.assertEqual(flow_rule_cmp(a, b), A_HAS_PRECEDENCE)
        a, b = b, a
        self.assertEqual(flow_rule_cmp(a, b), B_HAS_PRECEDENCE)
        a = FS_nlri(components=[
            FS_component(component_type=IP_SOURCE, value=ipaddress.ip_network('10.0.0.0/8') ),
            ])
        b = FS_nlri(components=[
            FS_component(component_type=IP_SOURCE, value=ipaddress.ip_network('11.1.0.0/16') ),
            ])
        self.assertEqual(flow_rule_cmp(a, b), A_HAS_PRECEDENCE)
        a, b = b, a
        self.assertEqual(flow_rule_cmp(a, b), B_HAS_PRECEDENCE)

    def test_other_component_memcmp(self):
        a = FS_nlri(components=[
            FS_component(component_type=4, value=bytearray([0,1,2,3,4,5,7])),
            ])
        b = FS_nlri(components=[
            FS_component(component_type=4, value=bytearray([0,1,2,3,4,5,6])),
            ])
        self.assertEqual(flow_rule_cmp(a, b), B_HAS_PRECEDENCE)
        a, b = b, a
        self.assertEqual(flow_rule_cmp(a, b), A_HAS_PRECEDENCE)

    def test_other_component_same_common(self):
        a = FS_nlri(components=[
            FS_component(component_type=4, value=bytearray([0,1,2,3,4,5,6,7])),
            ])
        b = FS_nlri(components=[
            FS_component(component_type=4, value=bytearray([0,1,2,3,4,5,6])),
            ])
        self.assertEqual(flow_rule_cmp(a, b), A_HAS_PRECEDENCE)
        a, b = b, a
        self.assertEqual(flow_rule_cmp(a, b), B_HAS_PRECEDENCE)

    def test_other_component_different_common(self):
        a = FS_nlri(components=[
            FS_component(component_type=4, value=bytearray([0,1,2,3,4,5,6,7])),
            ])
        b = FS_nlri(components=[
            FS_component(component_type=4, value=bytearray([0,1,2,3,4,3,6])),
            ])
        self.assertEqual(flow_rule_cmp(a, b), B_HAS_PRECEDENCE)
        a, b = b, a
        self.assertEqual(flow_rule_cmp(a, b), A_HAS_PRECEDENCE)
        a = FS_nlri(components=[
            FS_component(component_type=4, value=bytearray([0,1,2,3,4,5,6,7])),
            ])
        b = FS_nlri(components=[
            FS_component(component_type=4, value=bytearray([0,1,2,3,4,6,6])),
            ])
        self.assertEqual(flow_rule_cmp(a, b), A_HAS_PRECEDENCE)
        a, b = b, a
        self.assertEqual(flow_rule_cmp(a, b), B_HAS_PRECEDENCE)

a = """
        10.0.0.0/8 10.1.0.0/16
        common = 8
        10/8, 10/8 == equal -> longest match has preference
        = 10.1.0.0/16

        10.0.0.0/8 11.0.1.0/16
        common = 8
        10/8, 11/8 == neq -> lowest value hat preference
        = 10.0.0.0/8
"""

if __name__ == '__main__':
    unittest.main()
