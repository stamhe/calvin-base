# -*- coding: utf-8 -*-

# Copyright (c) 2015 Ericsson AB
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

from calvin.actor.actor import Actor, ActionResult, manage, condition, stateguard


class Select(Actor):
    """
    Route 'data' token to 'case_true' or 'case_false' port depending on 'select'

    Select assumes false or true as input, values outside that
    range will default to 'case_false'.

    Inputs:
      select : Select output for token on 'data' port
      data   : Token to send to 'case_true' or 'case_false' port
    Outputs:
      case_false  : Token from input 'data' if select token is false
      case_true   : Token from input 'data' if select token is true
    """
    @manage(['select'])
    def init(self):
        self.select = None

    @stateguard(lambda self: self.select is None)
    @condition(['select'], [])
    def select_action(self, select):
        self.select = select is True
        return ActionResult()

    @stateguard(lambda self: self.select is False)
    @condition(['data'], ['case_false'])
    def false_action(self, data):
        self.select = None
        return ActionResult(production=(data, ))

    @stateguard(lambda self: self.select is True)
    @condition(['data'], ['case_true'])
    def true_action(self, data):
        self.select = None
        return ActionResult(production=(data, ))

    action_priority = (select_action, false_action, true_action)

    test_set = [
        {
            'in': {'select': [True, False, 0, 1], 'data':[1,2,3,4]},
            'out': {'case_false': [2,3,4], 'case_true':[1]},
        },
    ]
