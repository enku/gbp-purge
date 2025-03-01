"""tests for gbp_purge.signals"""

import datetime as dt
from unittest import TestCase

from gentoo_build_publisher.records import BuildRecord
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
        old_record = BuildRecord(
            machine=old_build.machine,
            build_id=old_build.build_id,
            submitted=time("2025-02-17 07:00:00+0000"),
        )
        publisher.pull(old_record)

        new_build = fixtures.new_build
        new_record = BuildRecord(
            machine=new_build.machine,
            build_id=new_build.build_id,
            submitted=time("2025-02-25 00:00:00+0000"),
        )
        publisher.pull(new_record)

        machine = old_build.machine
        builds = [str(record) for record in records.for_machine(machine)]
        self.assertEqual([str(new_build)], builds)
