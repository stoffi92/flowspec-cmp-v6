import unittest

from flow_cmp_v6 import *

flow_rule_cmp = flow_rule_cmp_v6

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
            FS_IPv6_prefix_component(ipaddress.IPv6Network('0200::/16'), offset=4, component_type=IP_DESTINATION),
            FS_IPv6_prefix_component(ipaddress.IPv6Network('0100::/16'), offset=4, component_type=IP_SOURCE),
            FS_component(component_type=4, value=bytearray([0,1,2,3,4,5,6])),
            FS_component(component_type=5, value=bytearray([0,1,2,3,4,5,6])),
            ])
        b = FS_nlri(components=[
            FS_IPv6_prefix_component(ipaddress.IPv6Network('0200::/16'), offset=4, component_type=IP_DESTINATION),
            FS_IPv6_prefix_component(ipaddress.IPv6Network('0100::/16'), offset=4, component_type=IP_SOURCE),
            FS_component(component_type=4, value=bytearray([0,1,2,3,4,5,6])),
            FS_component(component_type=5, value=bytearray([0,1,2,3,4,5,6])),
            ])
        self.assertEqual(flow_rule_cmp(a, b), EQUAL)

    def test_ip_prefix_same_common(self):
        a = FS_nlri(components=[
            FS_IPv6_prefix_component(ipaddress.IPv6Network('0200::/8'), offset=4, component_type=IP_DESTINATION),
            ])
        b = FS_nlri(components=[
            FS_IPv6_prefix_component(ipaddress.IPv6Network('0201::/16'), offset=4, component_type=IP_DESTINATION),
            ])
        self.assertEqual(flow_rule_cmp(a, b), B_HAS_PRECEDENCE)
        a, b = b, a
        self.assertEqual(flow_rule_cmp(a, b), A_HAS_PRECEDENCE)
        a = FS_nlri(components=[
            FS_IPv6_prefix_component(ipaddress.IPv6Network('0200::/8'), offset=4, component_type=IP_SOURCE),
            ])
        b = FS_nlri(components=[
            FS_IPv6_prefix_component(ipaddress.IPv6Network('0201::/16'), offset=4, component_type=IP_SOURCE),
            ])
        self.assertEqual(flow_rule_cmp(a, b), B_HAS_PRECEDENCE)
        a, b = b, a
        self.assertEqual(flow_rule_cmp(a, b), A_HAS_PRECEDENCE)

    def test_ip_prefix_different_common(self):
        a = FS_nlri(components=[
            FS_IPv6_prefix_component(ipaddress.IPv6Network('0200::/8'), offset=4, component_type=IP_DESTINATION),
            ])
        b = FS_nlri(components=[
            FS_IPv6_prefix_component(ipaddress.IPv6Network('0301::/16'), offset=4, component_type=IP_DESTINATION),
            ])
        self.assertEqual(flow_rule_cmp(a, b), A_HAS_PRECEDENCE)
        a, b = b, a
        self.assertEqual(flow_rule_cmp(a, b), B_HAS_PRECEDENCE)
        a = FS_nlri(components=[
            FS_IPv6_prefix_component(ipaddress.IPv6Network('0200::/8'), offset=4, component_type=IP_SOURCE),
            ])
        b = FS_nlri(components=[
            FS_IPv6_prefix_component(ipaddress.IPv6Network('0301::/16'), offset=4, component_type=IP_SOURCE),
            ])
        self.assertEqual(flow_rule_cmp(a, b), A_HAS_PRECEDENCE)
        a, b = b, a
        self.assertEqual(flow_rule_cmp(a, b), B_HAS_PRECEDENCE)

    def test_ip_prefix_different_offset(self):
        a = FS_nlri(components=[
            FS_IPv6_prefix_component(ipaddress.IPv6Network('0200::/8'), offset=3, component_type=IP_DESTINATION),
            ])
        b = FS_nlri(components=[
            FS_IPv6_prefix_component(ipaddress.IPv6Network('0301::/16'), offset=4, component_type=IP_DESTINATION),
            ])
        self.assertEqual(flow_rule_cmp(a, b), A_HAS_PRECEDENCE)
        a, b = b, a
        self.assertEqual(flow_rule_cmp(a, b), B_HAS_PRECEDENCE)
        a = FS_nlri(components=[
            FS_IPv6_prefix_component(ipaddress.IPv6Network('0200::/8'), offset=3, component_type=IP_SOURCE),
            ])
        b = FS_nlri(components=[
            FS_IPv6_prefix_component(ipaddress.IPv6Network('0301::/16'), offset=4, component_type=IP_SOURCE),
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


if __name__ == '__main__':
    unittest.main()
