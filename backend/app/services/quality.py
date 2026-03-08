from backend.app.services.ffprobe_parser import ProbeResult


def calculate_quality_score(probe_result: ProbeResult) -> int:
    score = 3
    video = probe_result.video_streams[0] if probe_result.video_streams else None
    audio = max(probe_result.audio_streams, key=lambda stream: stream.channels or 0, default=None)

    if video:
        codec = (video.codec or "").lower()
        if codec in {"av1", "hevc", "h265"}:
            score += 2
        elif codec in {"h264", "avc"}:
            score += 1

        height = video.height or 0
        width = video.width or 0
        if width >= 3840 or height >= 2160:
            score += 2
        elif width >= 1920 or height >= 1080:
            score += 1

        if video.hdr_type:
            score += 1

        if probe_result.media_format.bit_rate and width and height:
            pixels = width * height
            bits_per_pixel_second = probe_result.media_format.bit_rate / max(pixels * max(video.frame_rate or 24, 1), 1)
            if bits_per_pixel_second > 0.22:
                score -= 2
            elif bits_per_pixel_second > 0.15:
                score -= 1

    if audio:
        codec = (audio.codec or "").lower()
        channels = audio.channels or 0

        if channels >= 8:
            score += 2
        elif channels >= 6:
            score += 1

        if codec in {"eac3", "dts", "truehd", "flac"}:
            score += 1

    return max(1, min(10, score))

