"""Build-time repository metrics for the construction dashboard.

The public site is frozen to static HTML, so these values are captured
once — when the page is rendered/frozen — and baked into the output.
That is deliberate: a static site's "telemetry" is whatever was true at
build time.

Every value degrades to None when git or the .git directory is missing
(the production Docker image has neither); the dashboard renders those
as "n/a" rather than inventing numbers.
"""

import subprocess
from datetime import datetime, timedelta, timezone

SPARKLINE_WEEKS = 12
_GIT_TIMEOUT_SECONDS = 10


def _git(args, cwd=None):
    """Run a git command; return stripped stdout, or None on any failure."""
    try:
        result = subprocess.run(
            ['git', *args],
            capture_output=True,
            text=True,
            check=True,
            timeout=_GIT_TIMEOUT_SECONDS,
            cwd=cwd,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        # OSError: git binary missing. CalledProcessError: not a repo /
        # bad ref. TimeoutExpired: pathological repo. All mean "no data".
        return None
    return result.stdout.strip()


def _weekly_commit_counts(now, repo_dir=None, weeks=SPARKLINE_WEEKS):
    """Commit counts per week, oldest first, over the last `weeks` weeks."""
    since = now - timedelta(weeks=weeks)
    raw = _git(
        ['log', f'--since={since.isoformat()}', '--format=%ct'],
        cwd=repo_dir,
    )
    if raw is None:
        return None

    counts = [0] * weeks
    for line in raw.splitlines():
        commit_time = datetime.fromtimestamp(int(line), tz=timezone.utc)
        weeks_ago = (now - commit_time) // timedelta(weeks=1)
        if 0 <= weeks_ago < weeks:
            counts[weeks - 1 - weeks_ago] += 1
    return counts


def bar_heights(counts, floor=6):
    """Scale commit counts to 0-100 bar heights for the CSS chart.

    `floor` keeps zero-commit weeks faintly visible so the chart reads
    as "quiet week", not "missing data".
    """
    if not counts:
        return None
    peak = max(counts) or 1
    return [
        max(round(count / peak * 100), floor) if count else floor
        for count in counts
    ]


def collect_metrics(repo_dir=None, now=None):
    """Assemble the dashboard metrics dict.

    `repo_dir` and `now` exist so tests can inject a fixed repo path and
    a frozen clock instead of depending on the real environment.
    """
    now = now or datetime.now(timezone.utc)

    total = _git(['rev-list', '--count', 'HEAD'], cwd=repo_dir)
    last_commit_iso = _git(['log', '-1', '--format=%cI'], cwd=repo_dir)

    return {
        'available': total is not None,
        'total_commits': int(total) if total is not None else None,
        'last_commit': (
            datetime.fromisoformat(last_commit_iso)
            if last_commit_iso else None
        ),
        'weekly_commits': _weekly_commit_counts(now, repo_dir=repo_dir),
        'generated_at': now,
    }
