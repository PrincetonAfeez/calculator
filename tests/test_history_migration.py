from app import migrate_history_line


def test_migrate_old_binary_format():
    old_line = "[2026-03-25 22:55:23] 88.0 pow 2.0 = 7744.0"
    assert (
        migrate_history_line(old_line)
        == "[2026-03-25 22:55:23] pow 88.0 2.0 = 7744.0"
    )


def test_migrate_old_sqrt_format_removes_fake_second_arg():
    old_line = "[2026-03-25 22:55:05] 88.0 sqrt 0 = 9.38083151964686"
    assert (
        migrate_history_line(old_line)
        == "[2026-03-25 22:55:05] sqrt 88.0 = 9.38083151964686"
    )


def test_keep_new_or_unknown_format_unchanged():
    line = "[2026-03-25 23:09:12] pct 20.0 150.0 = 30.0"
    assert migrate_history_line(line) == line
