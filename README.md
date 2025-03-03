# gbp-purge

A [Gentoo Build Publisher](https://github.com/enku/gentoo-build-publisher)
plugin to purge old builds.

## Description

This is a plugin to purge old builds of one's Gentoo Build Publisher instance.
It was spun off from core some of the core functionality in Gentoo Build
Publisher. The main reason for spinning out from GBP is that the strategy for
determining which builds to purge are specific and subjective, the purge
process was optional to begin with and, well, the satisfaction of writing
another plugin.

## Usage

Simply install it into the same environment as your Gentoo Build Publisher,
restart the services and that's it.  So if you've installed GBP via the
[Install
Guide](https://github.com/enku/gentoo-build-publisher/blob/master/docs/how-to-install.md)
it would look like this:

```
cd /home/gbp
sudo -u gbp -H ./bin/pip install git+https://github.com/enku/gbp-purge.git
systemctl restart gentoo-build-publisher-wsgi gentoo-build-publisher-worker
```

## How it works?

The system starts off by listening for "pull" events from Gentoo Build
Publisher. Whenever a build is pulled, a worker task is created to purge
builds belonging to the same machine as the build that was pulled.

In my ([rq](https://python-rq.org/)) logs it looks something like this:

```
21:01:25 gbp: gentoo_build_publisher.worker.tasks.pull_build('postgres.272', note=None, tags=None) (e1dec681-b392-4314-b7b7-7bff953f3acc)
21:01:40 Successfully completed gentoo_build_publisher.worker.tasks.pull_build('postgres.272', note=None, tags=None) job in 0:00:14.576645s on worker 57fa006e686f418787083030431476b4
21:01:40 gbp: Job OK (e1dec681-b392-4314-b7b7-7bff953f3acc)
21:01:40 gbp: gbp_fl.worker.tasks.index_packages('postgres', '272') (7dcf1f1b-91e6-4c71-8d0f-a5659cf9c634)
21:01:52 Successfully completed gbp_fl.worker.tasks.index_packages('postgres', '272') job in 0:00:11.676547s on worker 57fa006e686f418787083030431476b4
21:01:52 gbp: Job OK (7dcf1f1b-91e6-4c71-8d0f-a5659cf9c634)
21:01:52 gbp: gbp_purge.worker.tasks.purge_machine('postgres') (d3349ad8-2e5e-4ed2-9b3b-56d5aebf09aa)
21:01:54 Successfully completed gbp_purge.worker.tasks.purge_machine('postgres') job in 0:00:02.709775s on worker 57fa006e686f418787083030431476b4
21:01:54 gbp: Job OK (d3349ad8-2e5e-4ed2-9b3b-56d5aebf09aa)
21:01:54 gbp: gbp_fl.worker.tasks.delete_from_build('postgres', '270') (48abe652-1993-456a-a1aa-609faeb5d5c1)
21:01:54 Successfully completed gbp_fl.worker.tasks.delete_from_build('postgres', '270') job in 0:00:00.123885s on worker 57fa006e686f418787083030431476b4
21:01:54 gbp: Job OK (48abe652-1993-456a-a1aa-609faeb5d5c1)
```

### Purge strategy

gbp-purge will get the list of builds for the machine, look at the time they
were submitted (pulled) by GBP and keep:

- All from yesterday or later
- One for each day of the past week
- One for each week of the past month
- One for each month of the past year
- One per year
- The published build, if there is one
- All tagged builds
- All builds with the "keep" flag.

All other builds for that machine will be deleted. In all of the "one for
each" scenarios if there are more than one then it prefers the most recent.
For example in the "one for each day of the past week" scenario, if there is a
Thursday build and a Friday build it will keep the Friday build.

This is the same method I use for my [backup](https://github.com/enku/backup)
script.

Depending how many machines you have, how often they are build and how often
builds build new packages this will resemble something like a long tail over
time. For example, presently on my GBP instance the number of builds kept over
time looks like this

![screenshot](https://raw.githubusercontent.com/enku/screenshots/refs/heads/master/gbp-purge/builds-over-time.png)

Perhaps in the future I will add the capability of choosing different purge
strategies and add configuration to decide which strategy to use.
