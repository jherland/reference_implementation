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


class World:
	def __init__(self, start_date):
		self.today = start_date
		self.people = []

	def add_people(self, *people):
		self.people.extend(people)

	def next_day(self):
		''' Add 24h to world clock and advance all people to the next day.
		'''
		self.today += timedelta(days=1)
		for p in self.people:
			p.next_day()

	def epochs(self, start=time.min, end=time.max):
		''' Return datetime objects for each epoch between `start` and `end`.

		For example, given that today's date is 2020-04-01 and each epoch is
		15 minutes, calling self.epochs(time(8, 0, 0), time(10, 0, 0)) will
		yield the following datetimes:
			datetime(2020, 4, 1, 8, 0, 0)
			datetime(2020, 4, 1, 8, 15, 0)
			datetime(2020, 4, 1, 8, 30, 0)
			datetime(2020, 4, 1, 8, 45, 0)
			datetime(2020, 4, 1, 9, 0, 0)
			datetime(2020, 4, 1, 9, 15, 0)
			datetime(2020, 4, 1, 9, 30, 0)
			datetime(2020, 4, 1, 9, 45, 0)

		If `start` and/or `end` are not given they default to the start (0:00)
		and end (23:59) of the day, respectively.
		'''
		epoch = timedelta(minutes=LowCostDP3T.EPOCH_LENGTH)
		now = datetime.combine(self.today, start)
		end = datetime.combine(self.today, end)
		while now < end:
			yield now
			now += epoch


def report_exposure(exposure_tuples):
	for ephID, day, duration in exposure_tuples:
		print("At risk, observed {} on day -{} for {}".format(ephID, day, duration))


def main():
	# Mock time starts midnight on April 01.
	world = World(date(2020, 4, 1))
	
	# We have three people: Alice, Bob, and Isidor
	alice = LowCostDP3T.MockApp()
	bob = LowCostDP3T.MockApp()
	isidor = LowCostDP3T.MockApp()
	world.add_people(alice, bob, isidor)

	# Run tests for the specified number of days
	for day in range(2):
		print("Day: Alice, Bob, and Isidor do not have contact.")
		world.next_day()

	for day in range(3):
		print("Day: Alice and Bob work in the same office, Isidor elsewhere.")
		for now in world.epochs(start=time(8, 0, 0), end=time(17, 0, 0)):
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
		world.next_day()


	print("Day: Bob and Isidor meet for dinner.")
	for now in world.epochs(start=time(17, 0, 0), end=time(20, 0, 0)):
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
	infectious_date = world.today
	infections_SK = isidor.keystore.SKt[0]

	# Tik Tok
	world.next_day()

	# Check infectiousness
	print("Check exposure of Alice and Bob.")
	print("Alice: (not positive)")
	report_exposure(alice.ctmgr.check_exposure(infections_SK, infectious_date, world.today))

	print("Bob: (at risk)")
	report_exposure(bob.ctmgr.check_exposure(infections_SK, infectious_date, world.today))


if __name__ == "__main__":
	main()
