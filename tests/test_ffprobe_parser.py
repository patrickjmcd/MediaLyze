from backend.app.services.ffprobe_parser import normalize_ffprobe_payload


def test_normalize_ffprobe_payload_extracts_streams() -> None:
    payload = {
        "format": {
            "format_name": "matroska,webm",
            "duration": "5423.21",
            "bit_rate": "14000000",
            "probe_score": 100,
        },
        "streams": [
            {
                "index": 0,
                "codec_type": "video",
                "codec_name": "hevc",
                "profile": "Main 10",
                "width": 3840,
                "height": 2160,
                "pix_fmt": "yuv420p10le",
                "color_transfer": "smpte2084",
                "avg_frame_rate": "24000/1001",
                "bit_rate": "12000000",
            },
            {
                "index": 1,
                "codec_type": "audio",
                "codec_name": "eac3",
                "channels": 6,
                "channel_layout": "5.1(side)",
                "sample_rate": "48000",
                "bit_rate": "768000",
                "tags": {"language": "eng"},
                "disposition": {"default": 1, "forced": 0},
            },
            {
                "index": 2,
                "codec_type": "subtitle",
                "codec_name": "subrip",
                "tags": {"language": "deu"},
                "disposition": {"default": 0, "forced": 1},
            },
        ],
    }

    normalized = normalize_ffprobe_payload(payload)

    assert normalized.media_format.container_format == "matroska,webm"
    assert normalized.media_format.duration == 5423.21
    assert normalized.video_streams[0].hdr_type == "HDR10"
    assert normalized.video_streams[0].frame_rate == 24000 / 1001
    assert normalized.audio_streams[0].language == "eng"
    assert normalized.subtitle_streams[0].subtitle_type == "text"

