from typer.testing import CliRunner

from src.main import app, auto_register_commands

runner = CliRunner()


def test_all_sort_by_tags():
    auto_register_commands()
    with runner.isolated_filesystem():
        runner.invoke(app, ["add", "Pavlo", "1234567890"])
        runner.invoke(app, ["add", "Anna", "1111111111"])
        runner.invoke(app, ["tag-add", "Pavlo", "ml"])
        runner.invoke(app, ["tag-add", "Pavlo", "ai"])
        runner.invoke(app, ["tag-add", "Anna", "ai"])

        r = runner.invoke(app, ["all", "--sort-by", "tag_count"])
        assert r.exit_code == 0, r.stdout
        out = r.stdout
        assert out.index("Pavlo") < out.index("Anna")

        r = runner.invoke(app, ["all", "--sort-by", "tag_name"])
        assert r.exit_code == 0, r.stdout
