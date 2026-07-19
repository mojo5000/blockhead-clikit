from cli_kit.signature import params_of


def test_params_of_reads_names_and_defaults():
    def action(force=None, verbose=False, name="app"):
        return None

    specs = params_of(action)
    names = [s.name for s in specs]
    assert names == ["force", "verbose", "name"]
    assert all(s.has_default for s in specs)
    by_name = {s.name: s for s in specs}
    assert by_name["verbose"].default is False
    assert by_name["name"].default == "app"


def test_params_of_marks_required_params():
    def action(target, force=None):
        return None

    specs = params_of(action)
    by_name = {s.name: s for s in specs}
    assert by_name["target"].has_default is False
    assert by_name["force"].has_default is True


def test_params_of_skips_self():
    class Thing:
        def method(self, x=1):
            return x

    specs = params_of(Thing().method)
    assert [s.name for s in specs] == ["x"]
