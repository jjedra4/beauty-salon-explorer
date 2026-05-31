"""Tests for raw-record filesystem persistence."""

from pathlib import Path

from pipeline.collectors.base import RawSalon
from pipeline.storage import read_raw_salons, write_raw_salons


def test_write_then_read_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "salons.json"
    records = [
        RawSalon(
            source="google_places",
            source_id="A",
            name="Alpha",
            address="ul. Testowa 1",
            rating=4.5,
            reviews=["nice"],
            types=["hair_salon"],
            district_hint="Mokotów",
        ),
        RawSalon(source="google_places", source_id="B", name="Beta"),
    ]

    written = write_raw_salons(records, path)
    assert written == 2

    loaded = read_raw_salons(path)
    assert [r.source_id for r in loaded] == ["A", "B"]
    assert loaded[0].name == "Alpha"
    assert loaded[0].reviews == ["nice"]
    assert loaded[0].district_hint == "Mokotów"
