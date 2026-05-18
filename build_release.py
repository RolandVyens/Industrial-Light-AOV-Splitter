import pathlib
import tomllib
import zipfile


ROOT = pathlib.Path(__file__).resolve().parent
MANIFEST_PATH = ROOT / "blender_manifest.toml"
PACKAGE_DIR = "Industrial-Light-AOV-Splitter"
FILES_TO_INCLUDE = [
    "__init__.py",
    "auto_lightgroup.py",
    "blender_manifest.toml",
]


def read_version() -> str:
    manifest = tomllib.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return manifest["version"]


def build_zip() -> pathlib.Path:
    version = read_version()
    dist_dir = ROOT / "dist"
    dist_dir.mkdir(exist_ok=True)
    output_path = dist_dir / f"{PACKAGE_DIR} {version}.zip"

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Blender extension install expects forward-slash paths and a root entry.
        zf.writestr(f"{PACKAGE_DIR}/", "")
        for relative_path in FILES_TO_INCLUDE:
            source_path = ROOT / relative_path
            archive_path = f"{PACKAGE_DIR}/{relative_path}"
            zf.write(source_path, archive_path)

    return output_path


def main() -> None:
    output_path = build_zip()
    print(f"Created: {output_path}")


if __name__ == "__main__":
    main()
