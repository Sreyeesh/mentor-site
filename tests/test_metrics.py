"""Tests for the build-time metrics module.

subprocess is never invoked for real: _git is patched with fakes so the
tests are deterministic and run in containers without git.
"""

import subprocess
from datetime import datetime, timedelta, timezone

import metrics

NOW = datetime(2026, 7, 2, 12, 0, tzinfo=timezone.utc)


def _epoch(dt):
    return str(int(dt.timestamp()))


def fake_git_factory(responses):
    """Build a _git replacement returning canned output per subcommand."""
    def fake_git(args, cwd=None):
        return responses.get(args[0])
    return fake_git


def test_collect_metrics_parses_git_output(monkeypatch):
    log_lines = '\n'.join([
        _epoch(NOW - timedelta(days=1)),       # this week
        _epoch(NOW - timedelta(days=2)),       # this week
        _epoch(NOW - timedelta(weeks=3)),      # three weeks ago
    ])

    def fake_git(args, cwd=None):
        if args[0] == 'rev-list':
            return '321'
        if args == ['log', '-1', '--format=%cI']:
            return '2026-07-01T09:30:00+03:00'
        if args[0] == 'log':
            return log_lines
        raise AssertionError(f'unexpected git args: {args}')

    monkeypatch.setattr(metrics, '_git', fake_git)
    result = metrics.collect_metrics(now=NOW)

    assert result['available'] is True
    assert result['total_commits'] == 321
    assert result['last_commit'] == datetime.fromisoformat(
        '2026-07-01T09:30:00+03:00'
    )
    assert result['generated_at'] == NOW

    weekly = result['weekly_commits']
    assert len(weekly) == metrics.SPARKLINE_WEEKS
    assert weekly[-1] == 2          # newest bucket: the two recent commits
    assert weekly[-4] == 1          # the commit from three weeks ago
    assert sum(weekly) == 3


def test_collect_metrics_without_git_degrades_to_none(monkeypatch):
    monkeypatch.setattr(metrics, '_git', lambda args, cwd=None: None)
    result = metrics.collect_metrics(now=NOW)

    assert result == {
        'available': False,
        'total_commits': None,
        'last_commit': None,
        'weekly_commits': None,
        'generated_at': NOW,
    }


def test_weekly_counts_ignore_commits_outside_window(monkeypatch):
    stale = _epoch(NOW - timedelta(weeks=metrics.SPARKLINE_WEEKS + 1))
    monkeypatch.setattr(
        metrics, '_git', fake_git_factory({'log': stale})
    )
    counts = metrics._weekly_commit_counts(NOW)
    assert sum(counts) == 0


def test_bar_heights_scales_to_peak():
    assert metrics.bar_heights([0, 5, 10]) == [6, 50, 100]


def test_bar_heights_keeps_zero_weeks_visible():
    heights = metrics.bar_heights([0, 0, 1])
    assert heights == [6, 6, 100]


def test_bar_heights_handles_missing_data():
    assert metrics.bar_heights(None) is None
    assert metrics.bar_heights([]) is None


def test_git_helper_swallows_missing_binary(monkeypatch):
    def raise_missing(*args, **kwargs):
        raise FileNotFoundError('git not installed')

    monkeypatch.setattr(subprocess, 'run', raise_missing)
    assert metrics._git(['rev-list', '--count', 'HEAD']) is None


def test_git_helper_swallows_command_failure(monkeypatch):
    def raise_called_process_error(*args, **kwargs):
        raise subprocess.CalledProcessError(128, 'git')

    monkeypatch.setattr(subprocess, 'run', raise_called_process_error)
    assert metrics._git(['log', '-1']) is None
