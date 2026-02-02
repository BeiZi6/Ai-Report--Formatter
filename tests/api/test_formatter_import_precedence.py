import subprocess
import sys


def test_api_import_prefers_project_formatter_package():
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import formatter; from apps.api.main import app; print(app)",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
