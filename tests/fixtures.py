# pylint: disable=missing-docstring,unused-argument
import datetime as dt
from unittest import mock

from gbp_testkit import fixtures as testkit
from unittest_fixtures import FixtureContext, Fixtures, fixture

build = testkit.build
builds = testkit.builds
environ = testkit.environ
publisher = testkit.publisher
tmpdir = testkit.tmpdir


@fixture()
def now(
    fixtures: Fixtures,
    now: dt.datetime | None = None,  # pylint: disable=redefined-outer-name
    at: str = "gbp_purge.purger.dt",
) -> FixtureContext[dt.datetime]:
    new = now or dt.datetime.now()

    with mock.patch(at, wraps=dt) as mock_dt:
        mock_dt.datetime.now.return_value = new
        yield new
