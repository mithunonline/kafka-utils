# -*- coding: utf-8 -*-
# Copyright 2016 Yelp Inc.
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
import json
import logging

from .command import ClusterManagerCmd
from kafka_utils.util.validation import plan_to_assignment


class StatsCmd(ClusterManagerCmd):

    def __init__(self):
        super(StatsCmd, self).__init__()
        self.log = logging.getLogger(self.__class__.__name__)

    def build_subparser(self, subparsers):
        subparser = subparsers.add_parser(
            'stats',
            description='Show imbalance statistics of cluster topology',
            help='This command is used to display imbalance statistics of current '
            'cluster-topology or cluster-topology after given assignment is '
            'applied.',
        )
        subparser.add_argument(
            '--read-from-file',
            dest='plan_file_path',
            metavar='<reassignment-plan-file-path>',
            type=str,
            help='Read the partition assignment from json file. Example format:'
            ' {"version": 1, "partitions": [{"topic": "foo", "partition": 1, '
            '"replicas": [1,2,3]}]}',
        )
        return subparser

    def run_command(self, cluster_topology, _):
        if self.args.plan_file_path:
            print('Integrating given assignment-plan in current cluster-topology.')
            cluster_topology.update_cluster_topology(self.get_assignment())

    def get_assignment(self):
        """Parse the given json plan in dict format."""
        try:
            plan = json.loads(open(self.args.plan_file_path).read())
            return plan_to_assignment(plan)
        except IOError:
            self.log.exception(
                'Given json file {file} not found.'
                .format(file=self.args.plan_file_path),
            )
            raise
        except ValueError:
            self.log.exception(
                'Given json file {file} could not be decoded.'
                .format(file=self.args.plan_file_path),
            )
            raise
        except KeyError:
            self.log.exception(
                'Given json file {file} could not be parsed in desired format.'
                .format(file=self.args.plan_file_path),
            )
            raise
