#!/usr/bin/env python3

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
Download the existing multilambda.domain.zip from the S3 bucket.  Useful when
developing and small changes need to be made to a lambda function, but a full
rebuild of the entire zip file isn't required.
"""

import argparse
import boto3
import os
import sys

import alter_path
from lib import aws
from lib import configuration

def download_lambda_zip(bosslet_config, path):
    s3 = bosslet_config.session.client('s3')
    zip_name = bosslet_config.names.multi_lambda.zip
    full_path = '{}/{}'.format(path, zip_name)
    resp = s3.get_object(Bucket=bosslet_config.LAMBDA_BUCKET, Key=zip_name)

    bytes = resp['Body'].read()

    with open(full_path , 'wb') as out:
        out.write(bytes)

    print('Saved zip to {}'.format(full_path))


if __name__ == '__main__':
    parser = configuration.BossParser(description='Script for downloading lambda ' +
                                      'function code from S3. To supply arguments ' +
                                      'from a file, provide the filename prepended ' +
                                      'with an `@`.',
                                      fromfile_prefix_chars = '@')
    parser.add_bosslet()
    parser.add_argument('--save-path', '-p', 
                        default='.',
                        help='Where to save the lambda zip file.')

    args = parser.parse_args()

    download_lambda_zip(args.bosslet_config, args.save_path)
