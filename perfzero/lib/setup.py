# Copyright 2019 The TensorFlow Authors. All Rights Reserved.
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
# ==============================================================================
"""Checkout repository, download data and build docker image."""
from __future__ import print_function

import argparse
import json
import logging
import os
import time

import perfzero.utils as utils


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--dockerfile_path',
      type=str,
      default='docker/Dockerfile',
      help='Path to docker file')
  parser.add_argument(
      '--workspace',
      type=str,
      default='workspace')

  FLAGS, unparsed = parser.parse_known_args()

  logging.basicConfig(
      format='%(asctime)s %(levelname)s: %(message)s', level=logging.DEBUG)

  setup_execution_time = {}

  project_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
  workspace_dir = os.path.join(project_dir, FLAGS.workspace)

  # Download gcloud auth token and data
  # This step won't be necessary if GCE instance uses # <google-cloud-sdk-path>/bin/gsutil with
  # version 4.35 or higher which will pass gcloud credential to the docker instance.
  # See https://g3doc.corp.google.com/cloud/storage/g3doc/bigstore/bigstore-in-prod/bigstore-ops-playbook/gsutil-playbook.md?cl=head
  start_time = time.time()
  utils.download_from_gcs([{'gcs_url': 'gs://tf-performance/auth_tokens',
                            'local_path': os.path.join(workspace_dir, 'auth_tokens')}])
  setup_execution_time['download_token'] = time.time() - start_time

  start_time = time.time()
  dockerfile_path = os.path.join(project_dir, FLAGS.dockerfile_path)
  docker_tag = 'temp/tf-gpu'
  cmd = 'docker build --pull -t {} - < {}'.format(docker_tag, dockerfile_path)
  utils.run_commands([cmd])
  logging.info('Built docker image with tag %s', docker_tag)
  setup_execution_time['build_docker'] = time.time() - start_time

  logging.info('Setup time in seconds by operation:\n %s',
               json.dumps(setup_execution_time, indent=2))
