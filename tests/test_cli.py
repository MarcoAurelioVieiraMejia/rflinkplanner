from rflinkplanner.cli import main


def test_cli_fspl(capsys):
    assert main(["fspl", "--distance-km", "1", "--freq-mhz", "900"]) == 0
    out = capsys.readouterr().out
    assert "path loss" in out.lower()


def test_cli_linkbudget(capsys):
    code = main(
        [
            "linkbudget",
            "--tx-power-dbm", "20",
            "--tx-gain-dbi", "24",
            "--rx-gain-dbi", "24",
            "--path-loss-db", "130",
            "--rx-sensitivity-dbm", "-85",
        ]
    )
    assert code == 0
    out = capsys.readouterr().out
    assert "Fade margin" in out


def test_cli_reports_error_on_invalid_input(capsys):
    code = main(["fspl", "--distance-km", "-1", "--freq-mhz", "900"])
    assert code == 1
    err = capsys.readouterr().err
    assert "Error" in err
