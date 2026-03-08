from backend.app.services.ffprobe_parser import (
    NormalizedAudioStream,
    NormalizedFormat,
    NormalizedVideoStream,
    ProbeResult,
)
from backend.app.services.quality import calculate_quality_score


def test_quality_score_rewards_modern_high_quality_media() -> None:
    probe = ProbeResult(
        raw={},
        media_format=NormalizedFormat(
            container_format="matroska",
            duration=7200,
            bit_rate=14000000,
            probe_score=100,
        ),
        video_streams=[
            NormalizedVideoStream(
                stream_index=0,
                codec="hevc",
                profile="Main 10",
                width=3840,
                height=2160,
                pix_fmt="yuv420p10le",
                color_space=None,
                color_transfer="smpte2084",
                color_primaries=None,
                frame_rate=23.976,
                bit_rate=12000000,
                hdr_type="HDR10",
            )
        ],
        audio_streams=[
            NormalizedAudioStream(
                stream_index=1,
                codec="truehd",
                channels=8,
                channel_layout="7.1",
                sample_rate=48000,
                bit_rate=3000000,
                language="eng",
                default_flag=True,
                forced_flag=False,
            )
        ],
    )

    assert calculate_quality_score(probe) >= 8


def test_quality_score_penalizes_inefficient_video() -> None:
    probe = ProbeResult(
        raw={},
        media_format=NormalizedFormat(
            container_format="matroska",
            duration=7200,
            bit_rate=45000000,
            probe_score=100,
        ),
        video_streams=[
            NormalizedVideoStream(
                stream_index=0,
                codec="h264",
                profile="High",
                width=1920,
                height=1080,
                pix_fmt="yuv420p",
                color_space=None,
                color_transfer=None,
                color_primaries=None,
                frame_rate=24.0,
                bit_rate=43000000,
                hdr_type=None,
            )
        ],
    )

    assert calculate_quality_score(probe) <= 4

