# Copyright 2016 The Johns Hopkins University Applied Physics Laboratory
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Library contains AWS VPC and VPC Subnet IP subnet allocation and lookup.

Author:
    Derek Pryor <Derek.Pryor@jhuapl.edu>
"""

##
# User configurable section. Changes here will change how addresses are generated
#
# Note: The first three (3) address in each subnet are reserved by AWS
#       http://docs.aws.amazon.com/AmazonVPC/latest/UserGuide/VPC_Subnets.html
#       Section Subnet Sizing
# Example: For 10.0.0.0/24 Subnet
#          10.0.0.0: Network address.
#          10.0.0.1: Reserved by AWS for the VPC router.
#          10.0.0.2: Reserved by AWS for mapping to the Amazon-provided DNS.
#          10.0.0.3: Reserved by AWS for future use.
#          10.0.0.255: Network broadcast address. We do not support broadcast in a VPC, therefore we reserve this address.
##

# SUBNETS contains the list of all possible subnets and is used to determine the number of a
#         given subnet. Example: 'internal' is subnet 0, 'external' is subnet 1, etc
# NOTE: Do not reorder subnets as this will bork any existing Boss stacks. If new subnets are
#       needed they should be added to the end of the list
SUBNETS = [
    'internal',
    'external',
    'a-internal',
    'b-internal',
    'c-internal',
    'd-internal',
    'e-internal',
    'a-external',
    'b-external',
    'c-external',
    'd-external',
    'e-external',
    'lambda0',
    'lambda1',
    'lambda2',
    'lambda3',
    'lambda4',
    'lambda5',
    'lambda6',
    'lambda7',
    'lambda8',
    'lambda9',
    'lambda10',
    'lambda11',
    'lambda12',
    'lambda13',
    'lambda14',
    'lambda15',
    'f-internal',
    'f-external',
]

from ipaddress import IPv4Network

class Hosts(object):
    def __init__(self, bosslet_config):
        self.domain = bosslet_config.INTERNAL_DOMAIN
        self.vpc_cidr = bosslet_config.NETWORK
        self.subnet_cidr = bosslet_config.SUBNET_CIDR

    def lookup(self, subnet):
        subnet, domain = subnet.split('.', 1)
        if domain != self.domain:
            raise ValueError("Subnet '{}' isn't part of the '{}' domain".format(subnet, self.domain))

        if subnet not in SUBNETS:
            raise ValueError("Subnet '{}' isn't a valid subnet".format(subnet))

        subnet_id = SUBNETS.index(subnet)
        vpc_net = IPv4Network(self.vpc_cidr)
        return str(list(vpc_net.subnets(new_prefix=self.subnet_cidr))[subnet_id])
        
