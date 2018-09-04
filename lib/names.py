# Copyright 2014 The Johns Hopkins University Applied Physics Laboratory
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

from . import hosts

class AWSNames(object):
    """
    All names are returned as dotted names (containg '.' between each component).
    Some AWS resources cannot have '.' in their name. In these cases the
    CloudFormationConfiguration add_* methods will convert '.' to '-' as needed.
    """

    def __init__(self, base):
        self.base = base
        self.base_dot = '.' + base

    @classmethod
    def create_from_lambda_name(cls, name):
        """
        Instantiate AWSNames from the name of a lambda function.  Used by
        lambdas so they can look up names of other resources.

        Args:
            name (str): Name of lambda function (ex: multiLambda-integration-boss)

        Returns:
            (AWSNames)

        """
        # Lambdas names can't have periods; restore proper name.
        dotted_name = name.replace('-', '.')
        domain = dotted_name.split('.', 1)[1]
        return cls(domain)

    ##################################
    # Generic rules for different type of AWS resources
    def subnet(self, name):
        return name + self.base_dot

    def public_dns(self, name):
        name = name.split('.')[0]
        if self.base in hosts.BASE_DOMAIN_CERTS.keys():
            dns = name + "." + hosts.BASE_DOMAIN_CERTS[self.base]
        else:
            stack = self.base.split('.')[0]
            dns = "{}-{}.{}".format(name, stack, hosts.DEV_DOMAIN)
        return dns

    ##################################
    # Properties for common / well known BOSS resources
    RESOURCES = {
        "bastion": "bastion",
        "auth": "auth", # ec2 instance, security group
        "auth_db": "auth-db",
        "vault": "vault",
        "consul": "consul",
        "api": "api", # public name of endoint
        "endpoint": "endpoint",
        "endpoint_db": "endpoint-db",
        "endpoint_elb": "elb",
        "proofreader": "proofreader-web",
        "proofreader_db": "proofreader-db",
        "dns": "dns", # lambda, sns topic display name, sns topic name
        "internal": "internal", # subnet, security group, route table
        "ssh": "ssh",
        "https": "https",
        "http": "http",
        "internet": "internet",
        "meta": "bossmeta",
        'cache_session': 'cache-session',   # Redis server for Django sessions.
        "cache": "cache",                   # Redis server to cache cuboids.
        "cache_state": "cache-state",
        "cache_manager": "cachemanager",
        "cache_db": "cachedb",
        "cuboid_bucket": "cuboids",
        "multi_lambda": "multiLambda",
        "s3_index": "s3index",
        "ingest_bucket": "ingest",
        "tile_bucket": "tiles",
        "delete_tile_objs_lambda": 'deleteTileObjsLambda',
        "tile_index": "tileindex",
        "cuboid_ids_bucket": "cuboid-ids",
        "delete_tile_index_entry_lambda": 'deleteTileEntryLambda',
        "ingest_cleanup_dlq": "IngestCleanupDlq",
        "id_index": "idIndex",
        "id_count_index": "idCount",
        "s3flush_queue": "S3flush",
        "deadletter_queue": "Deadletter",
        'write_lock_topic': 'WriteLockAlert',
        'write_lock': 'WriteLockAlert',
        'vault_monitor': 'vaultMonitor',
        'consul_monitor': 'consulMonitor',
        'vault_consul_check': 'checkVaultConsul',
        'activities': 'activities',
        'delete_cuboid': 'Delete.Cuboid',
        'delete_bucket': 'delete',
        'delete_experiment': 'Delete.Experiment',
        'delete_collection': 'Delete.Collection',
        'delete_coord_frame': 'Delete.CoordFrame',
        'query_deletes': 'Query.Deletes',
        'delete_event_rule': 'deleteEventRule',
        'delete_lambda': "deleteLambda",
        'resolution_hierarchy': 'Resolution.Hierarchy',
        'downsample_volume': 'Downsample.Volume',
        'downsample_volume_lambda': 'downsampleVolumeLambda',
        'ingest_queue_populate': 'Ingest.Populate',
        'ingest_queue_upload': 'Ingest.Upload',
        'ingest_lambda': 'IngestUpload',
        'dynamo_lambda': 'dynamoLambda',
        'trigger_dynamo_autoscale': 'triggerDynamoAutoscale',
        'start_sfn_lambda': 'startSfnLambda',
        'index_id_writer_sfn': 'Index.IdWriter',
        'downsample_status': 'downsample-status',
        'downsample_dlq': 'downsample-dlq',
        'index_cuboid_supervisor_sfn': 'Index.CuboidSupervisor',
        'index_find_cuboids_sfn': 'Index.FindCuboids',
        'index_supervisor_sfn': 'Index.Supervisor',
        'index_enqueue_cuboids_sfn': 'Index.EnqueueCuboids',
        'index_fanout_enqueue_cuboids_sfn': 'Index.FanoutEnqueueCuboids',
        'index_dequeue_cuboids_sfn': 'Index.DequeueCuboids',
        'index_fanout_dequeue_cuboids_sfn': 'Index.FanoutDequeueCuboids',
        'index_fanout_id_writers_sfn': 'Index.FanoutIdWriters',
        'index_s3_writer_lambda': 'indexS3WriterLambda',
        'index_fanout_id_writer_lambda': 'indexFanoutIdWriterLambda',
        'index_write_id_lambda': 'indexWriteIdLambda',
        'index_deadletter_queue': 'indexDeadLetter',
        'index_write_failed_lambda': 'indexWriteFailedLambda',
        'index_find_cuboids_lambda': 'indexFindCuboidsLambda',
        'index_split_cuboids_lambda': 'indexSplitCuboidsLambda',
        'index_fanout_enqueue_cuboid_keys_lambda': 'indexFanoutEnqueueCuboidsKeysLambda',
        'index_batch_enqueue_cuboids_lambda': 'indexBatchEnqueueCuboidsLambda',
        'index_fanout_dequeue_cuboid_keys_lambda': 'indexFanoutDequeueCuboidsKeysLambda',
        'index_dequeue_cuboid_keys_lambda': 'indexDequeueCuboidsLambda',
        'index_get_num_cuboid_keys_msgs_lambda': 'indexGetNumCuboidKeysMsgsLambda',
        'index_check_for_throttling_lambda': 'indexCheckForThrottlingLambda',
        'index_invoke_index_supervisor_lambda': 'indexInvokeIndexSupervisorLambda',
        'index_load_ids_from_s3_lambda': 'indexLoadIdsFromS3Lambda',
        'index_cuboids_keys_queue': 'cuboidsKeys',
        'copy_cuboid_lambda': 'copyCuboidLambda',
        'copy_cuboid_dlq': 'copyCuboidDlq'
    }

    def __getattr__(self, name):
        if name not in self.RESOURCES:
            raise AttributeError("{} is not a valid BOSS AWS Resource name".format(name))

        hostname = self.RESOURCES[name]
        if name in ['write_lock_topic']:
            return hostname

        fq_hostname = hostname + self.base_dot

        # Lambda names cannot have periods, so we use dashes, instead.
        if name in ['multi_lambda', 'write_lock', 'vault_monitor', 'consul_monitor', 'vault_consul_check',
                    'delete_lambda', 'ingest_lambda', 'dynamo_lambda', 
                    'index_s3_writer_lambda', 'index_fanout_id_writer_lambda',
                    'downsample_dlq', 'downsample_volume_lambda',
                    'delete_tile_objs_lambda', 'delete_tile_index_entry_lambda',
                    'index_write_id_lambda', 'index_write_failed_lambda',
                    'index_find_cuboids_lambda', 
                    'index_fanout_enqueue_cuboid_keys_lambda',
                    'index_batch_enqueue_cuboids_lambda', 
                    'index_fanout_dequeue_cuboid_keys_lambda',
                    'index_dequeue_cuboid_keys_lambda',
                    'index_get_num_cuboid_keys_msgs_lambda',
                    'index_check_for_throttling_lambda',
                    'index_invoke_index_supervisor_lambda',
                    'index_split_cuboids_lambda',
                    'index_load_ids_from_s3_lambda',
                    'start_sfn_lambda',
                    'delete_lambda', 'ingest_lambda', 'dynamo_lambda', 'downsample_dlq', 'downsample_volume_lambda',
                    'delete_tile_objs_lambda', 'delete_tile_index_entry_lambda',
                    'copy_cuboid_lambda']:
            fq_hostname = fq_hostname.replace('.','-')

        # Queue names cannot have periods, so we capitalize each word, instead.
        if name in ['s3flush_queue', 'deadletter_queue', 'delete_cuboid', 'query_deletes',
                    'ingest_queue_populate', 'ingest_queue_upload', 'resolution_hierarchy',
                    'downsample_volume', 'delete_experiment', 'delete_collection', 'delete_coord_frame',
                    'index_deadletter_queue', 'index_cuboids_keys_queue',
                    'ingest_cleanup_dlq', 'copy_cuboid_dlq']:
            fq_hostname = "".join(map(lambda x: x.capitalize(), fq_hostname.split('.')))

        return fq_hostname

