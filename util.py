"""Misc. utilities."""
import shutil
import subprocess
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, Self

from pydantic import BaseModel, ValidationInfo, field_validator


class FFprobeStream(BaseModel):
    # Based on: https://github.com/FFmpeg/FFmpeg/blob/master/doc/ffprobe.xsd
    # Anything without `use="required"` has been made nullable

    index: int
    codec_name: str | None = None
    codec_long_name: str | None = None
    profile: str | None = None
    level: int | None = None
    codec_type: str | None = None
    codec_tag: str
    codec_tag_string: str
    extradata: str | None = None
    extradata_size: int | None = None
    extradata_hash: str | None = None
    mime_codec_string: str | None = None

    # Video
    width: int | None = None
    height: int | None = None
    coded_width: int | None = None
    coded_height: int | None = None
    closed_captions: bool | None = None
    film_grain: bool | None = None
    has_b_frames: int | None = None
    sample_aspect_ratio: str | None = None
    display_aspect_ratio: str | None = None
    pix_fmt: str | None = None
    color_range: str | None = None
    color_space: str | None = None
    color_transfer: str | None = None
    color_primaries: str | None = None
    chroma_location: str | None = None
    field_order: str | None = None
    refs: int | None = None

    # Audio
    sample_fmt: str | None = None
    sample_rate: int | None = None
    channels: int | None = None
    channel_layout: str | None = None
    bits_per_sample: int | None = None
    initial_padding: int | None = None
    seek_preroll: int | None = None
    id: str | None = None
    r_frame_rate: str
    avg_frame_rate: str
    time_base: str
    start_pts: int | None = None
    start_time: float | None = None
    duration_ts: int | None = None
    duration: float | None = None
    bit_rate: int | None = None
    max_bit_rate: int | None = None
    bits_per_raw_sample: int | None = None
    nb_frames: int | None = None
    nb_read_frames: int | None = None
    nb_read_packets: int | None = None

    @field_validator('*', mode='before')
    @classmethod
    def void_na(cls, value: Any, _info: ValidationInfo) -> Any:  # noqa: ANN401
        return None if value == 'N/A' else value

    @classmethod
    def from_output(cls, raw: str) -> list[Self]:
        """Returns a list of streams parsed from the default output of ffprobe."""
        streams: list[dict[str, str]] = []

        stream: dict[str, str] | None = None

        for ln in raw.splitlines():
            if not ln.strip():
                continue

            if ln == '[STREAM]':
                streams.append(stream := {})
                continue

            if ln == '[/STREAM]':
                stream = None
                continue

            if stream is None:
                continue

            k, v = ln.split('=', maxsplit=1)
            stream[k] = v

        return [cls.model_validate(d) for d in streams]

    @classmethod
    def from_file(cls, fp: str | Path) -> list[Self]:
        """Spawns an ffprobe process and returns a list of streams from a media file.

        :raises subprocess.CalledProcessError:
            ffprobe exited with a non-zero status.
        :raises FileNotFoundError:
            `fp` does not exist, or `ffprobe` was not found on the system's PATH.
        """
        if not (ffprobe_bin := shutil.which('ffprobe')):
            raise FileNotFoundError("ffprobe is not on the system's PATH")

        fp = Path(fp)
        if not fp.is_file():
            raise FileNotFoundError(fp)

        proc = subprocess.run(  # noqa: S603
            (
                ffprobe_bin,
                '-v', 'error',
                '-show_streams',
                str(fp),
            ),
            capture_output=True,
            check=True,
        )

        return cls.from_output(proc.stdout.decode('utf-8'))

def asserts(condition: bool, err: str | Exception | None = None) -> None:  # noqa: FBT001
    """Asserts that ``condition`` is ``True``, raising according to ``err`` otherwise.

    :param err: If ``None``, raises :class:`AssertionError` with the message "expected True". If given a string, raises
        :class:`AssertionError` with that string as its argument. If given an exception, raises the exception.
    """
    if not condition:
        if isinstance(err, Exception):
            raise err

        raise AssertionError(err if err is not None else 'expected True')

def expect[T](value: T | None, err: str | Exception | None = None) -> T:
    """Returns ``value`` if not ``None``, otherwise raises according to ``err``.

    :param err: If ``None``, raises :class:`ValueError` with the message "None". If given a string, raises
        :class:`ValueError` with that string as the message. If given an exception, raises the exception.
    """
    if value is None:
        if (err is None) or isinstance(err, str):
            raise ValueError(err)
        if isinstance(err, Exception):
            raise err
        raise TypeError(f'Unexpected type for parameter err: {err!r}')

    return value

def get_as[K, V, T](m: Mapping[K, V], key: K, fn: Callable[[V], T]) -> T | None:
    """Call ``m.get(key)`` and apply ``fn`` to its result if not ``None``."""
    return fn(v) if (v := m.get(key)) is not None else None
