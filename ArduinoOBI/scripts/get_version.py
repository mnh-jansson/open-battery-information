import subprocess
import re
Import("env")

def get_version_from_git():
    try:
        tag = subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"],
            cwd=env.subst("$PROJECT_DIR"),
            stderr=subprocess.DEVNULL,
        ).decode().strip()
        m = re.match(r"v?(\d+)\.(\d+)\.(\d+)", tag)
        if m:
            return int(m.group(1)), int(m.group(2)), int(m.group(3))
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return 0, 0, 0

major, minor, patch = get_version_from_git()

env.Append(BUILD_FLAGS=[
    f"-DARDUINO_OBI_VERSION_MAJOR={major}",
    f"-DARDUINO_OBI_VERSION_MINOR={minor}",
    f"-DARDUINO_OBI_VERSION_PATCH={patch}",
])
