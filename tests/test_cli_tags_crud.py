import pytest
from typer.testing import CliRunner

from src.container import container
from src.main import app, auto_register_commands

runner = CliRunner()


@pytest.fixture(autouse=True)
def _isolate_cli(tmp_path, monkeypatch):
    auto_register_commands()
    monkeypatch.chdir(tmp_path)
    container.config.storage.filename.override(str(tmp_path / "book.pkl"))
    yield
    container.config.storage.filename.reset_override()


def test_tag_crud():

    # 1. make sure contact exists
    r = runner.invoke(app, ["add", "Pavlo", "1234567890"])
    assert r.exit_code == 0

    # 2. Add tag
    r = runner.invoke(app, ["tag-add", "Pavlo", "ml"])
    assert r.exit_code == 0
    assert "added" in r.stdout.lower()

    # 3. Check tag list output
    r = runner.invoke(app, ["tag-list", "Pavlo"])
    assert "ml" in r.stdout

    # 4. Remove tag
    r = runner.invoke(app, ["tag-remove", "Pavlo", "ml"])
    assert r.exit_code == 0
    assert "removed" in r.stdout.lower()

    # 5. Check tag list output again
    r = runner.invoke(app, ["tag-list", "Pavlo"])
    assert "(no tags)" in r.stdout.lower()

    # 6. Check clear (should not fail)
    r = runner.invoke(app, ["tag-clear", "Pavlo"])
    assert r.exit_code == 0
