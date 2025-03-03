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

In my ([rq](https://python-rq.org/)) logs it looks something like this
(summarized):

```
06:51:42 gbp: gentoo_build_publisher.worker.tasks.pull_build('arm64-base.822', note=None, tags=None) (5ae68cf6-3eb0-4e40-b6ee-f99ba049fe2d)
06:51:55 Successfully completed gentoo_build_publisher.worker.tasks.pull_build('arm64-base.822', note=None, tags=None) job in 0:00:13.068159s on worker fd2c3f812a604660974e6ccaaa093b3f
06:51:55 gbp: gbp_purge.worker.tasks.purge_machine('arm64-base') (a157b907-7070-40b4-91b8-785e70056139)
06:52:05 Successfully completed gbp_purge.worker.tasks.purge_machine('arm64-base') job in 0:00:10.031353s on worker fd2c3f812a604660974e6ccaaa093b3f
06:52:05 gbp: gbp_fl.worker.tasks.index_build('arm64-base', '822') (22581b06-3a37-49cd-bd39-4484ace4428e)
06:52:18 Successfully completed gbp_fl.worker.tasks.index_build('arm64-base', '822') job in 0:00:12.643137s on worker fd2c3f812a604660974e6ccaaa093b3f
06:52:18 gbp: gbp_fl.worker.tasks.deindex_build('arm64-base', '523') (b304d865-57a6-47cd-a1bf-d6a639328468)
06:52:18 Successfully completed gbp_fl.worker.tasks.deindex_build('arm64-base', '523') job in 0:00:00.085653s on worker fd2c3f812a604660974e6ccaaa093b3f
06:52:18 gbp: gbp_fl.worker.tasks.deindex_build('arm64-base', '814') (b04331b4-21c3-4219-b420-b819287a11bc)
06:52:18 Successfully completed gbp_fl.worker.tasks.deindex_build('arm64-base', '814') job in 0:00:00.058608s on worker fd2c3f812a604660974e6ccaaa093b3f
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
