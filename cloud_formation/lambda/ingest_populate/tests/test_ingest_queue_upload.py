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

import boto3
import ingest_queue_upload as iqu
#import ingest_queue_upload_master as iqum
import json
import math
import unittest
from unittest.mock import patch, MagicMock
import pprint
import ingestclient.plugins.catmaid as ic_plugs
import ingestclient.core.backend as backend

@patch('boto3.resource')
class TestIngestQueueUploadLambda(unittest.TestCase):

    def tile_count(self, kwargs):
        x = math.ceil((kwargs["x_stop"] - kwargs["x_start"]) / kwargs["x_tile_size"])
        y = math.ceil((kwargs["y_stop"] - kwargs["y_start"]) / kwargs["y_tile_size"])
        z = math.ceil((kwargs["z_stop"] - kwargs["z_start"]) / kwargs["z_tile_size"])
        t = math.ceil((kwargs["t_stop"] - kwargs["t_start"]) / kwargs["t_tile_size"])
        return x * y * z * t


    def test_all_messages_are_there(self, fake_resource):
        """
        This test will show that when tiles are being genereated by multiple lambdas, the sum of those tiles
        will be the exact same set that would be generated by a single lambda creating them all.
        Test_all_messages_are_there tests() first it creates
        set of messages that all fit into a single lambda populating a dictionary with all the values returned.
        Then it runs the create_messages 4 more times each time with the appropriate tiles_to_skip and
        MAX_NUM_ITEMS_PER_LAMBDA set. It pulls the tile key out of the dictionary to verify that all the tiles were
        accounted for.  In the end there should be no tiles left in the dictionary.

        This test can with many different values for tile sizes and starts and stop vaules and num_lambdas can be
        changed.
        Args:
            fake_resource:

        Returns:

        """

        args = {
            "upload_sfn": "IngestUpload",
            "x_start": 0,
            "x_stop": 2048,
            "y_start": 0,
            "y_stop": 2048,
            "z_start": 0,
            "z_stop": 20,
            "t_start": 0,
            "t_stop": 1,
            "project_info": [
              "3",
              "3",
              "3"
            ],
            "ingest_queue": "https://queue.amazonaws.com/...",
            "job_id": 11,
            "upload_queue": "https://queue.amazonaws.com/...",
            "x_tile_size": 1024,
            "y_tile_size": 1024,
            "t_tile_size": 1,
            "z_tile_size": 1,
            "resolution": 0,
            "items_to_skip": 0,
            'MAX_NUM_ITEMS_PER_LAMBDA': 500000,
            'z_chunk_size': 16
        }

        # Walk create_messages generator as a single lambda would and populate the dictionary with all Keys like this
        # "Chunk --- tiles".
        dict = {}
        msgs = iqu.create_messages(args)
        for msg_json in msgs:
            ct_key = self.generate_chunk_tile_key(msg_json)
            if ct_key not in dict:
                dict[ct_key] = 1
            else:
                self.fail("Dictionary already contains key: ".format(ct_key))

        # Verify correct count of tiles in dictionary
        dict_length = len(dict.keys())
        tile_count = self.tile_count(args)
        print("Tile Count: {}".format(tile_count))
        self.assertEqual(dict_length, tile_count)

        # loop through create_messages() num_lambda times pulling out each tile from the dictionary.
        num_lambdas = 4
        args["MAX_NUM_ITEMS_PER_LAMBDA"] = math.ceil(dict_length / num_lambdas)
        for skip in range(0, dict_length, args["MAX_NUM_ITEMS_PER_LAMBDA"]):
            args["items_to_skip"] = skip
            #print("Skip: " + str(skip))
            msgs = iqu.create_messages(args)
            for msg_json in msgs:
                ct_key = self.generate_chunk_tile_key(msg_json)
                if ct_key in dict:
                    del dict[ct_key]
                else:
                    self.fail("Dictionary does not contains key: ".format(ct_key))

        # Verify Dictionary has no left over tiles.
        self.assertEqual(len(dict), 0)

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

