# Copyright 2018 The Johns Hopkins University Applied Physics Laboratory
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

import boto3
import json

def handler(event, context):
    try:
        sqs = boto3.resource('sqs')
        args = json.loads(event['Records'][0]['Sns']['Message'])
        queue_arn = args['dlq_arn']
        try:
            queue = sqs.Queue(queue_arn)
            queue.load()
        except:
            print("Target queue '{}' no longer exists".format(queue_arn))
            return
        queue.send_message(MessageBody = json.dumps(event))
    except:
        print("Event: {}".format(json.dumps(event, indent=3)))
        raise
