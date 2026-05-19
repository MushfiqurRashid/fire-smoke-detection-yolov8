"""
Dataset helper for the D-Fire project layout.

This script does not download proprietary dataset assets automatically. Instead,
it validates the local dataset structure and can generate the expected YOLO
dataset YAML inside the data directory.
"""

from __future__ import annotations

from pathlib import Path
import argparse
import textwrap


DATA_YAML = textwrap.dedent(
    """\
    path: ..
    train: data/train/images
    val: data/val/images
    test: data/test/images

    names:
      - smoke
      - fire

    nc: 2
    """
)


def validate_dataset_layout(data_dir: Path) -> list[str]:
    """Return missing required dataset paths."""
    required = [
        data_dir / "train" / "images",
        data_dir / "train" / "labels",
        data_dir / "val" / "images",
        data_dir / "val" / "labels",
        data_dir / "test" / "images",
        data_dir / "test" / "labels",
    ]
    return [str(path) for path in required if not path.exists()]


def write_dataset_yaml(data_dir: Path) -> Path:
    """Write the expected YOLO dataset YAML into the data directory."""
    yaml_path = data_dir / "data.yaml"
    yaml_path.write_text(DATA_YAML, encoding="utf-8")
    return yaml_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate the D-Fire dataset layout and generate data/data.yaml."
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data"),
        help="Path to the dataset directory.",
    )
    parser.add_argument(
        "--write-yaml",
        action="store_true",
        help="Write data/data.yaml if the dataset structure is present.",
    )
    args = parser.parse_args()

    data_dir = args.data_dir
    missing = validate_dataset_layout(data_dir)

    if missing:
        print("Dataset layout is incomplete. Missing paths:")
        for path in missing:
            print(f" - {path}")
        raise SystemExit(1)

    print(f"Dataset layout looks good at {data_dir.resolve()}.")

    if args.write_yaml:
        yaml_path = write_dataset_yaml(data_dir)
        print(f"Wrote dataset YAML to {yaml_path.resolve()}.")


if __name__ == "__main__":
    main()
