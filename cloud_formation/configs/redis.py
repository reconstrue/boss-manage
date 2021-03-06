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

DEPENDENCIES = ['core']

"""
Create the redis configuration which consists of
  * redis cluster for cache
  * redis cluster for cache-state
  # redis cluster for cache-throttle
  * redis for session key 

The redis configuration creates cache and cache-state redis clusters for the
BOSS system. redis configuration is in a separate file to improve the update process
"""
import json

from lib.cloudformation import CloudFormationConfiguration, Arg, Ref, Arn
from lib import aws
from lib import console
from lib import constants as const
from lib.lambdas import load_lambdas_on_s3, freshen_lambda

# The timezone offset (standard time) of AWS regions to UTC/GMT
TIMEZONE_OFFSET = {
    'us-east-1': 5,
    'us-east-2': 5,
    'us-west-1': 8,
    'us-west-2': 8,
}

def create_config(bosslet_config):
    names = bosslet_config.names
    session = bosslet_config.session

    config = CloudFormationConfiguration('redis', bosslet_config)

    vpc_id = config.find_vpc()
    internal_subnets, external_subnets = config.find_all_subnets()
    sgs = aws.sg_lookup_all(session, vpc_id)

    # Create the Cache and CacheState Redis Clusters
    REDIS_PARAMETERS = {
        "maxmemory-policy": "volatile-lru",
        "reserved-memory-percent": str(const.REDIS_RESERVED_MEMORY_PERCENT),
        "maxmemory-samples": "5", # ~ 5 - 10
    }

    config.add_redis_replication("Cache",
                                 names.cache.redis,
                                 internal_subnets,
                                 [sgs[names.internal.sg]],
                                 type_=const.REDIS_CACHE_TYPE,
                                 version="3.2.4",
                                 clusters=const.REDIS_CLUSTER_SIZE,
                                 parameters=REDIS_PARAMETERS)

    config.add_redis_replication("CacheState",
                                 names.cache_state.redis,
                                 internal_subnets,
                                 [sgs[names.internal.sg]],
                                 type_=const.REDIS_TYPE,
                                 version="3.2.4",
                                 clusters=const.REDIS_CLUSTER_SIZE)

    # This one may not be created depending on the scenario type.
    if const.REDIS_SESSION_TYPE is not None:
        config.add_redis_replication("CacheSession",
                                     names.cache_session.redis,
                                     internal_subnets,
                                     [sgs[names.internal.sg]],
                                     type_=const.REDIS_SESSION_TYPE,
                                     version="3.2.4",
                                     clusters=1)

    if const.REDIS_THROTTLE_TYPE is not None:
        vpc_id = config.find_vpc()
        internal_sg = aws.sg_lookup(session, vpc_id, names.internal.sg)
        lambda_subnets, _ = config.find_all_subnets(compatibility = 'lambda')

        config.add_redis_replication("CacheThrottle",
                                     names.cache_throttle.redis,
                                     internal_subnets,
                                     [sgs[names.internal.sg]],
                                     type_=const.REDIS_THROTTLE_TYPE,
                                     version="3.2.4",
                                     clusters=1)

        config.add_lambda("CacheThrottleLambda",
                          names.cache_throttle.lambda_,
                          aws.role_arn_lookup(session, 'lambda_basic_execution'),
                          description="Reset Boss throttling metrics",
                          security_groups=[internal_sg],
                          subnets=lambda_subnets,
                          handler='index.handler',
                          timeout=120,
                          memory=1024)

        # Schedule the lambda to be executed at midnight for the timezone where the bosslet is located
        hour = TIMEZONE_OFFSET.get(bosslet_config.REGION, 0)
        schedule = 'cron(0 {} * * ? *)'.format(hour)
        config.add_cloudwatch_rule('CacheThrottleReset',
                                   name=names.cache_throttle.cw,
                                   description='Reset the current Boss throttling metrics',
                                   targets=[
                                       {
                                           'Arn': Arn('CacheThrottleLambda'),
                                           'Id': names.cache_throttle.lambda_,
                                           'Input': json.dumps({
                                                'host': names.cache_throttle.redis
                                            }),
                                       },
                                   ],
                                   schedule=schedule,
                                   depends_on=['CacheThrottleLambda'])

        config.add_lambda_permission('CacheThrottlePerms',
                                     names.cache_throttle.lambda_,
                                     principal='events.amazonaws.com',
                                     source=Arn('CacheThrottleReset'))

    return config


def generate(bosslet_config):
    """Create the configuration and save it to disk"""
    config = create_config(bosslet_config)
    config.generate()


def create(bosslet_config):
    if const.REDIS_THROTTLE_TYPE is not None:
        pre_init(bosslet_config)

    config = create_config(bosslet_config)
    config.create()

def pre_init(bosslet_config):
    load_lambdas_on_s3(bosslet_config, bosslet_config.names.cache_throttle.lambda_)

def update(bosslet_config):
    if const.REDIS_THROTTLE_TYPE is not None:
        rebuild_lambdas = console.confirm("Rebuild lambdas", default=True)
    else:
        rebuild_lambdas = False

    if rebuild_lambdas:
        pre_init(bosslet_config)

    config = create_config(bosslet_config)
    config.update()

    if rebuild_lambdas:
        freshen_lambda(bosslet_config, bosslet_config.names.cache_throttle.lambda_)

def delete(bosslet_config):
    config = CloudFormationConfiguration('redis', bosslet_config)
    config.delete()
