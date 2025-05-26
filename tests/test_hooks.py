from hatch_timestamp_version import hooks


def test_hook() -> None:
    assert hooks.hatch_register_version_scheme()
