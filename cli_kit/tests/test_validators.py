from cli_kit.prompts import validators as v


def test_nonempty():
    assert v.nonempty("hi") is True
    assert isinstance(v.nonempty("  "), str)


def test_port_range():
    assert v.port_range("8000") is True
    assert isinstance(v.port_range("0"), str)
    assert isinstance(v.port_range("70000"), str)
    assert isinstance(v.port_range("abc"), str)


def test_regex_factory():
    slug = v.regex(r"^[a-z-]+$", "lowercase and hyphens only")
    assert slug("my-app") is True
    assert slug("My App") == "lowercase and hyphens only"


def test_one_of():
    env = v.one_of(["dev", "prod"])
    assert env("dev") is True
    assert isinstance(env("staging"), str)


def test_chain_first_failure_wins():
    combined = v.chain(v.nonempty, v.port_range)
    assert combined("8000") is True
    assert isinstance(combined(""), str)  # fails nonempty
    assert isinstance(combined("abc"), str)  # passes nonempty, fails port_range
