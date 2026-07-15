"""Tests for TMDB JSON parsing and tag construction."""

from __future__ import annotations

from movie_rec.data.loader import make_synthetic_sample
from movie_rec.features.text import (
    add_tags,
    build_tag,
    parse_cast,
    parse_director,
    parse_names,
)

_GENRES = '[{"id": 28, "name": "Action"}, {"id": 878, "name": "Science Fiction"}]'
_CREW = '[{"job": "Editor", "name": "E One"}, {"job": "Director", "name": "Christopher Nolan"}]'
_CAST = '[{"name": "A One"}, {"name": "B Two"}, {"name": "C Three"}, {"name": "D Four"}]'


def test_parse_names():
    assert parse_names(_GENRES) == ["Action", "Science Fiction"]


def test_parse_names_handles_bad_input():
    assert parse_names("") == []
    assert parse_names(None) == []
    assert parse_names("not json") == []


def test_parse_cast_top_n():
    assert parse_cast(_CAST, top_n=3) == ["A One", "B Two", "C Three"]


def test_parse_director():
    assert parse_director(_CREW) == "Christopher Nolan"
    assert parse_director('[{"job": "Editor", "name": "E One"}]') == ""


def test_build_tag_collapses_and_stems():
    row = {
        "overview": "Dreams within dreams",
        "genres": _GENRES,
        "keywords": '[{"name": "dream heist"}]',
        "cast": _CAST,
        "crew": _CREW,
    }
    tag = build_tag(row)
    # multi-word entities collapse to single tokens
    assert "sciencefiction" in tag
    assert "christophernolan" in tag
    assert "dreamheist" in tag
    # overview is stemmed: "dreams" -> "dream"
    assert "dream" in tag.split()
    assert "dreams" not in tag.split()


def test_add_tags_columns():
    df = add_tags(make_synthetic_sample())
    for col in ("genre_list", "keyword_list", "director", "tags"):
        assert col in df.columns
    assert df["tags"].str.len().gt(0).all()
