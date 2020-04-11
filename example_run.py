#!/usr/bin/env python3
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

from datetime import date, datetime, time, timedelta

import LowCostDP3T


def epochs(
	start=datetime.combine(date.today(), time.min),
	end=datetime.combine(date.today(), time.max),
):
	''' Return datetime objects for each epoch between `start` and `end`.

	For example, assuming each epoch is 15 minutes long, calling epochs() with
	start = datetime.fromisoformat("2020-04-01 08:00") and
	end = datetime.fromisoformat("2020-04-01 10:00") will yield these objects:
		datetime(2020, 4, 1, 8, 0, 0)
		datetime(2020, 4, 1, 8, 15, 0)
		datetime(2020, 4, 1, 8, 30, 0)
		datetime(2020, 4, 1, 8, 45, 0)
		datetime(2020, 4, 1, 9, 0, 0)
		datetime(2020, 4, 1, 9, 15, 0)
		datetime(2020, 4, 1, 9, 30, 0)
		datetime(2020, 4, 1, 9, 45, 0)

	If `start` and/or `end` are not given they default to the start (0:00)
	and end (23:59) of today, respectively.
	'''
	epoch = timedelta(minutes=LowCostDP3T.EPOCH_LENGTH)
	while start < end:
		yield start
		start += epoch


def main():
	# Mock time starts midnight on April 01.
	epotime = datetime(2020, 4, 1)
	
	# We have three people: Alice, Bob, and Isidor
	alice = LowCostDP3T.MockApp()
	bob = LowCostDP3T.MockApp()
	isidor = LowCostDP3T.MockApp()

	# Run tests for the specified number of days
	for day in range(2):
		print("Day: Alice, Bob, and Isidor do not have contact.")
		epotime += timedelta(days=1)
		alice.next_day()
		bob.next_day()
		isidor.next_day()

	for day in range(3):
		print("Day: Alice and Bob work in the same office, Isidor elsewhere.")
		# For each epoch between 08:00 and 17:00
		for now in epochs(epotime.replace(hour=8), epotime.replace(hour=17)):
			alice_ephID = alice.keystore.get_current_ephID(now)
			bob_ephID = bob.keystore.get_current_ephID(now)
			# Record two beacons in the same epoch, resulting in a contact
			alice.ctmgr.receive_scans([bob_ephID], now = now)
			bob.ctmgr.receive_scans([alice_ephID], now = now)
			now = now + timedelta(seconds=LowCostDP3T.CONTACT_THRESHOLD+1)
			alice.ctmgr.receive_scans([bob_ephID], now = now)
			bob.ctmgr.receive_scans([alice_ephID], now = now)
			# Process the received beacons
			alice.next_epoch()
			bob.next_epoch()
		# Tik Tok
		epotime += timedelta(days=1)
		alice.next_day()
		bob.next_day()
		isidor.next_day()        

	print("Day: Bob and Isidor meet for dinner.")
	for now in epochs(epotime.replace(hour=17), epotime.replace(hour=20)):
		bob_ephID = bob.keystore.get_current_ephID(now)
		isidor_ephID = isidor.keystore.get_current_ephID(now)
		# Record two beacons in the same epoch, resulting in a contact
		bob.ctmgr.receive_scans([isidor_ephID], now = now)
		isidor.ctmgr.receive_scans([bob_ephID], now = now)
		now = now + timedelta(seconds=LowCostDP3T.CONTACT_THRESHOLD+1)
		bob.ctmgr.receive_scans([isidor_ephID], now = now)
		isidor.ctmgr.receive_scans([bob_ephID], now = now)
		# Process the received beacons
		alice.next_epoch()
		bob.next_epoch()
		isidor.next_epoch()

	print("Isidor is tested positive.")
	infectious_date = epotime
	infections_SK = isidor.keystore.SKt[0]

	# Tik Tok
	epotime += timedelta(days=1)
	alice.next_day()
	bob.next_day()
	isidor.next_day()

	# Check infectiousness
	print("Check exposure of Alice and Bob.")
	print("Alice: (not positive)")
	alice.ctmgr.check_infected(infections_SK, infectious_date.strftime("%Y-%m-%d"), epotime)
	print("Bob: (at risk)")
	bob.ctmgr.check_infected(infections_SK, infectious_date.strftime("%Y-%m-%d"), epotime)


if __name__ == "__main__":
	main()
