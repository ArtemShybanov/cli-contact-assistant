from typer.testing import CliRunner

from src.main import app, auto_register_commands

runner = CliRunner()


def test_find_by_tags_and_or(tmp_path, monkeypatch):

    auto_register_commands()

    with runner.isolated_filesystem():

        # create contacts
        runner.invoke(app, ["add", "Pavlo", "1234567890"])
        runner.invoke(app, ["add", "Anna", "1111111111"])

        # add tags
        runner.invoke(app, ["tag-add", "Pavlo", "ml"])
        runner.invoke(app, ["tag-add", "Pavlo", "ai"])
        runner.invoke(app, ["tag-add", "Anna", "ai"])

        # AND: both tags → only Pavlo
        r = runner.invoke(app, ["find-by-tags", "ai,ml"])
        out = r.stdout.lower()
        assert "pavlo" in out
        assert "anna" not in out

        # OR: at least one tag → both
        r = runner.invoke(app, ["find-by-tags-any", "ai,ml"])
        out = r.stdout.lower()
        assert "pavlo" in out
        assert "anna" in out
