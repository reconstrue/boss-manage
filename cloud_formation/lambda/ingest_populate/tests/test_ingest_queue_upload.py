# Copyright 2016 The Johns Hopkins University Applied Physics Laboratory
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# lambdafcns contains symbolic links to lambda functions in boss-tools/lambda.
# Since lambda is a reserved word, this allows importing from that folder 
# without updating scripts responsible for deploying the lambda code.

import ingest_queue_upload as iqu
import hashlib
import json
import math
import unittest

class TestIngestQueueUploadLambda(unittest.TestCase):

    def tile_count(self, kwargs):
        x = math.ceil((kwargs["x_stop"] - kwargs["x_start"]) / kwargs["x_tile_size"])
        y = math.ceil((kwargs["y_stop"] - kwargs["y_start"]) / kwargs["y_tile_size"])
        z = math.ceil((kwargs["z_stop"] - kwargs["z_start"]) / kwargs["z_tile_size"])
        t = math.ceil((kwargs["t_stop"] - kwargs["t_start"]) / kwargs["t_tile_size"])
        return x * y * z * t


    def test_all_messages_are_there(self):
        """
        This test will show that when tiles are being genereated by multiple lambdas, the sum of those tiles
        will be the exact same set that would be generated by a single lambda creating them all.
        Test_all_messages_are_there tests() first it creates
        the set of expected messages for the ingest.

        Then it runs the create_messages() _n_ times each time with the appropriate items_to_skip and
        MAX_NUM_ITEMS_PER_LAMBDA set. It pulls the tile key out of the set to verify that all the tiles were
        accounted for.  In the end there should be no tiles left in the set.

        This test can with many different values for tile sizes and starts and stop vaules and num_lambdas can be
        changed.
        """

        # Loops to exercise different parameters.
        for t_stop in [1, 3]:
            for z_stop in [20, 33]:
                for y_stop in [2560, 2048, 2052]:
                    for x_stop in [2048, 2560, 1028]:
                        args = {
                            "upload_sfn": "IngestUpload",
                            "x_start": 0,
                            "x_stop": x_stop,
                            "y_start": 0,
                            "y_stop": y_stop,
                            "z_start": 0,
                            "z_stop": z_stop,
                            "t_start": 0,
                            "t_stop": t_stop,
                            "project_info": [
                              "3",
                              "3",
                              "3"
                            ],
                            "ingest_queue": "https://queue.amazonaws.com/...",
                            "job_id": 11,
                            "upload_queue": "https://queue.amazonaws.com/...",
                            "x_tile_size": 512,
                            "y_tile_size": 512,
                            "t_tile_size": 1,
                            "z_tile_size": 1,
                            "resolution": 0,
                            "items_to_skip": 0,
                            'MAX_NUM_ITEMS_PER_LAMBDA': 500000,
                            'z_chunk_size': 16
                        }

                        # Walk create_messages generator as a single lambda would
                        # and populate the dictionary with all Keys like this
                        # "Chunk --- tiles".
                        msg_set = set()
                        exp_msgs = create_expected_messages(args)
                        for msg_json in exp_msgs:
                            ct_key = self.generate_chunk_tile_key(msg_json)
                            if ct_key not in msg_set:
                                msg_set.add(ct_key)
                            else:
                                self.fail("Set already contains key: ".format(ct_key))

                        # Verify correct count of tiles in set
                        set_length = len(msg_set)
                        tile_count = self.tile_count(args)
                        print("Tile Count: {}".format(tile_count))
                        self.assertEqual(set_length, tile_count)

                        # Try different number of lambdas.  No need to regenerated
                        # expected messages when using different lambdas, so
                        # make a copy of the msg_set inside the loop.
                        for num_lambdas in range(3, 5):
                            with self.subTest(num_lambdas=num_lambdas, x_stop=x_stop, y_stop=y_stop, z_stop=z_stop, t_stop=t_stop):
                                # loop through create_messages() num_lambda times pulling out each tile from the set.
                                msg_set_copy = msg_set.copy()
                                args["MAX_NUM_ITEMS_PER_LAMBDA"] = math.ceil(set_length / num_lambdas)
                                for skip in range(0, set_length, args["MAX_NUM_ITEMS_PER_LAMBDA"]):
                                    args["items_to_skip"] = skip
                                    #print("Skip: " + str(skip))
                                    msgs = iqu.create_messages(args)
                                    for msg_json in msgs:
                                        ct_key = self.generate_chunk_tile_key(msg_json)
                                        if ct_key in msg_set_copy:
                                            msg_set_copy.remove(ct_key)
                                        else:
                                            self.fail("Set does not contains key: ".format(ct_key))

                                # Verify set has no left over tiles.
                                self.assertEqual(len(msg_set_copy), 0)

    def generate_chunk_tile_key(self, msg_json):
        """
        Generate a key to track messages for testing.

        Args:
            msg_json (str): JSON message encoded as string intended for the upload queue.

        Returns:
            (str): Unique key identifying message.
        """
        msg = json.loads(msg_json)
        parts = msg["chunk_key"].split("&", 6)
        chunk = parts[-1].replace("&", "  ")
        parts = msg["tile_key"].split("&", 5)
        tile = parts[-1].replace("&", "  ")
        return "{} --- {}".format(chunk, tile)


def create_expected_messages(args):
    """Create all of the expected tile messages to be enqueued

    This function is from the original implementation where it used a for
    loop to skip messages to get to its starting location.  The skip code is
    removed because we want all the messages that are expected for testing
    the current implementation of ingest_queue_upload.create_messages().

    Args:
        args (dict): Same arguments as populate_upload_queue()

    Returns:
        list: List of strings containing Json data
    """

    tile_size = lambda v: args[v + "_tile_size"]
    range_ = lambda v: range(args[v + '_start'], args[v + '_stop'], tile_size(v))

    # DP NOTE: generic version of
    # BossBackend.encode_chunk_key and BiossBackend.encode.tile_key
    # from ingest-client/ingestclient/core/backend.py
    def hashed_key(*args):
        base = '&'.join(map(str,args))

        md5 = hashlib.md5()
        md5.update(base.encode())
        digest = md5.hexdigest()

        return '&'.join([digest, base])

    count_in_offset = 0

    for t in range_('t'):
        for z in range(args['z_start'], args['z_stop'], args['z_chunk_size']):
            for y in range_('y'):
                for x in range_('x'):
                    num_of_tiles = min(args['z_chunk_size'], args['z_stop'] - z)

                    for tile in range(z, z + num_of_tiles):
                        if count_in_offset == 0:
                            print("Finished skipping tiles")

                        chunk_x = int(x / tile_size('x'))
                        chunk_y = int(y / tile_size('y'))
                        chunk_z = int(z / args['z_chunk_size'])
                        chunk_key = hashed_key(num_of_tiles,
                                               args['project_info'][0],
                                               args['project_info'][1],
                                               args['project_info'][2],
                                               args['resolution'],
                                               chunk_x,
                                               chunk_y,
                                               chunk_z,
                                               t)

                        count_in_offset += 1
                        if count_in_offset > args['MAX_NUM_ITEMS_PER_LAMBDA']:
                            return  # end the generator
                        tile_key = hashed_key(args['project_info'][0],
                                              args['project_info'][1],
                                              args['project_info'][2],
                                              args['resolution'],
                                              chunk_x,
                                              chunk_y,
                                              tile,
                                              t)

                        msg = {
                            'job_id': args['job_id'],
                            'upload_queue_arn': args['upload_queue'],
                            'ingest_queue_arn': args['ingest_queue'],
                            'chunk_key': chunk_key,
                            'tile_key': tile_key,
                        }

                        yield json.dumps(msg)
