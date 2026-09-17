#!/usr/bin/env python3
"""Fast, dependency-free checks for the phone-only Android distribution."""

from pathlib import Path
import re
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
ANDROID_NS = "{http://schemas.android.com/apk/res/android}"


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def check_manifest() -> None:
    manifest = ET.parse(ROOT / "android/app/src/main/AndroidManifest.xml").getroot()
    # The manifest has a plain activity child; Android attributes are the
    # namespaced values checked below.
    activities = manifest.findall("application/activity")
    assert len(activities) == 1, "the APK must expose one launcher activity"
    activity = activities[0]
    assert activity.get(ANDROID_NS + "name") == "android.app.NativeActivity"
    assert activity.get(ANDROID_NS + "exported") == "true"
    assert activity.get(ANDROID_NS + "screenOrientation") == "landscape"

    lib_names = manifest.findall("application/activity/meta-data")
    assert any(
        item.get(ANDROID_NS + "name") == "android.app.lib_name"
        and item.get(ANDROID_NS + "value") == "openrblx"
        for item in lib_names
    ), "NativeActivity must load libopenrblx.so"


def check_phone_only_native_target() -> None:
    cmake = read("android/CMakeLists.txt")
    makefile = read("Makefile")
    hefile = read("HeFile")

    assert 'message(FATAL_ERROR "The OpenRBLX native target is Android-only")' in cmake
    assert '"${OPENRBLX_ROOT}/player/player.c"' in cmake
    assert "/studio/studio.c" not in cmake
    assert re.search(r"^PROGRAMS=player\s*$", makefile, re.MULTILINE)
    assert "$(DISTDIR)/studio$(EXEC_EXTENSION)" not in makefile
    assert not re.search(r"^Program\s+studio\s*$", hefile, re.MULTILINE)
    assert "OPENRBLX_MOBILE" in cmake
    assert "OPENRBLX_NO_CURL" in cmake


def check_workflow() -> None:
    workflow = read(".github/workflows/android.yml")
    for required in (
        "submodules: recursive",
        "android-actions/setup-android@v3",
        "ndk;27.2.12479018",
        "cmake;3.22.1",
        ":app:assembleRelease",
        "apksigner",
        "actions/upload-artifact@v4",
    ):
        assert required in workflow, f"workflow is missing {required!r}"


def check_assets_are_reproducible() -> None:
    gradle = read("android/app/build.gradle")
    assert "syncGameAssets" in gradle
    assert 'include("staticdata/**")' in gradle
    assert 'include("res/test1.rbxl")' in gradle
    assert 'gameToLoad = "res/test1.rbxl"' in read("player/player.c")


def main() -> None:
    check_manifest()
    check_phone_only_native_target()
    check_workflow()
    check_assets_are_reproducible()
    print("mobile project checks: OK")


if __name__ == "__main__":
    main()
