"""
Global system constants shared by all DP3T designs.
"""

__copyright__ = """
    Copyright 2020 EPFL

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
__license__ = "Apache 2.0"

from datetime import timedelta

#: How long we should store keys and observations
RETENTION_PERIOD = timedelta(days=21)

#: The length of an epoch
EPOCH_LENGTH = timedelta(minutes=15)

#: Number of epochs in a day
NUM_EPOCHS_PER_DAY = timedelta(days=1) // EPOCH_LENGTH

#: Length of EphID in bytes
LENGTH_EPHID = 16

#: Seconds in a UNIX Epoch day
SECONDS_PER_DAY = timedelta(days=1) // timedelta(seconds=1)
