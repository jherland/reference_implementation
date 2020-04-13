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


class Simulation:
	''' Simulate apps/people interacting over a period of time.
	'''

	def __init__(self, start_date):
		self.today = start_date
		self.people = []

	def add_people(self, *people):
		self.people.extend(people)

	def next_day(self):
		''' Fast-forward the simulation and all people in it to the next day.
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
		now = datetime.combine(self.today, start)
		end = datetime.combine(self.today, end)
		while now < end:
			yield now
			now += LowCostDP3T.EPOCH_LENGTH

	def share_ephIDs(self, people, ephIDs, now):
		''' Broadcast each person's EphID to the other people in the group.

		Each item in the given list of EphIDs is assumed to originate from
		the corresponding person in the given list of people.
		'''
		assert len(people) == len(ephIDs)
		for p, own_ephID in zip(people, ephIDs):
			incoming = [e for e in ephIDs if e != own_ephID]
			p.ctmgr.receive_scans(incoming, now=now)

	def meeting(self, start, end, people):
		''' Simulate people meeting over a given time period.
		'''
		assert people
		for now in self.epochs(start, end):
			ephIDs = [p.keystore.get_current_ephID(now) for p in people]
			# Record two beacons in the same epoch, resulting in a contact
			self.share_ephIDs(people, ephIDs, now)
			now += LowCostDP3T.CONTACT_THRESHOLD + timedelta(seconds=1)
			self.share_ephIDs(people, ephIDs, now)
			# Process the received beacons
			for p in people:
				p.next_epoch()


def report_exposure(exposure_tuples):
	for ephID, day, duration in exposure_tuples:
		print("At risk, observed {} on day -{} for {}".format(ephID, day, duration))


def main():
	# Mock time starts midnight on April 01.
	sim = Simulation(date(2020, 4, 1))
	
	# We have three people: Alice, Bob, and Isidor
	alice = LowCostDP3T.MockApp()
	bob = LowCostDP3T.MockApp()
	isidor = LowCostDP3T.MockApp()
	sim.add_people(alice, bob, isidor)

	# Run tests for the specified number of days
	for day in range(2):
		print("Day: Alice, Bob, and Isidor do not have contact.")
		sim.next_day()

	for day in range(3):
		print("Day: Alice and Bob work in the same office, Isidor elsewhere.")
		sim.meeting(time(8, 0, 0), time(17, 0, 0), [alice, bob])
		# Tik Tok
		sim.next_day()


	print("Day: Bob and Isidor meet for dinner.")
	sim.meeting(time(17, 0, 0), time(20, 0, 0), [bob, isidor])

	print("Isidor is tested positive.")
	infectious_date = sim.today
	infections_SK = isidor.keystore.SKt[0]

	# Tik Tok
	sim.next_day()

	# Check infectiousness
	print("Check exposure of Alice and Bob.")
	print("Alice: (not positive)")
	report_exposure(alice.ctmgr.check_exposure(infections_SK, infectious_date, sim.today))

	print("Bob: (at risk)")
	report_exposure(bob.ctmgr.check_exposure(infections_SK, infectious_date, sim.today))


if __name__ == "__main__":
	main()
