"""tests for gbp_purge.signals"""

import datetime as dt
from unittest import TestCase

from unittest_fixtures import Fixtures, given, where

# pylint: disable=missing-docstring
time = dt.datetime.fromisoformat


@given("environ", "now", "publisher", old_build="build", new_build="build")
@where(
    now=time("2025-02-25 07:00:00"), environ={"BUILD_PUBLISHER_WORKER_BACKEND": "sync"}
)
class SignalsTests(TestCase):
    def test(self, fixtures: Fixtures) -> None:
        publisher = fixtures.publisher
        records = publisher.repo.build_records

        old_build = fixtures.old_build
        publisher.pull(old_build)
        old_record = records.get(old_build)
        old_record = records.save(
            old_record, submitted=time("2025-02-17 07:00:00+0000")
        )

        new_build = fixtures.new_build
        publisher.pull(new_build)
        new_record = records.get(new_build)

        machine = old_build.machine
        self.assertEqual([new_record], records.for_machine(machine))
