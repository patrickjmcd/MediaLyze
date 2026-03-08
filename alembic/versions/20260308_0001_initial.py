"""initial schema

Revision ID: 20260308_0001
Revises:
Create Date: 2026-03-08
"""

from alembic import op
import sqlalchemy as sa


revision = "20260308_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    library_type = sa.Enum("movies", "series", "mixed", "other", name="librarytype", native_enum=False)
    scan_mode = sa.Enum("manual", "scheduled", "watch", name="scanmode", native_enum=False)
    scan_status = sa.Enum("pending", "analyzing", "ready", "failed", name="scanstatus", native_enum=False)
    job_status = sa.Enum("queued", "running", "completed", "failed", name="jobstatus", native_enum=False)

    op.create_table(
        "libraries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False, unique=True),
        sa.Column("path", sa.String(length=2048), nullable=False, unique=True),
        sa.Column("type", library_type, nullable=False),
        sa.Column("last_scan_at", sa.DateTime(), nullable=True),
        sa.Column("scan_mode", scan_mode, nullable=False),
        sa.Column("scan_config", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_table(
        "media_files",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("library_id", sa.Integer(), sa.ForeignKey("libraries.id", ondelete="CASCADE"), nullable=False),
        sa.Column("relative_path", sa.String(length=2048), nullable=False),
        sa.Column("filename", sa.String(length=512), nullable=False),
        sa.Column("extension", sa.String(length=32), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("mtime", sa.Float(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(), nullable=False),
        sa.Column("last_analyzed_at", sa.DateTime(), nullable=True),
        sa.Column("scan_status", scan_status, nullable=False),
        sa.Column("quality_score", sa.Integer(), nullable=False),
        sa.Column("raw_ffprobe_json", sa.JSON(), nullable=True),
    )
    op.create_index("ix_media_files_library_relative_path", "media_files", ["library_id", "relative_path"], unique=True)
    op.create_index("ix_media_files_quality_score", "media_files", ["quality_score"])
    op.create_index("ix_media_files_scan_status", "media_files", ["scan_status"])

    op.create_table(
        "media_formats",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("media_file_id", sa.Integer(), sa.ForeignKey("media_files.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("container_format", sa.String(length=255)),
        sa.Column("duration", sa.Float()),
        sa.Column("bit_rate", sa.Integer()),
        sa.Column("probe_score", sa.Integer()),
    )

    op.create_table(
        "video_streams",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("media_file_id", sa.Integer(), sa.ForeignKey("media_files.id", ondelete="CASCADE"), nullable=False),
        sa.Column("stream_index", sa.Integer(), nullable=False),
        sa.Column("codec", sa.String(length=64)),
        sa.Column("profile", sa.String(length=128)),
        sa.Column("width", sa.Integer()),
        sa.Column("height", sa.Integer()),
        sa.Column("pix_fmt", sa.String(length=64)),
        sa.Column("color_space", sa.String(length=64)),
        sa.Column("color_transfer", sa.String(length=64)),
        sa.Column("color_primaries", sa.String(length=64)),
        sa.Column("frame_rate", sa.Float()),
        sa.Column("bit_rate", sa.Integer()),
        sa.Column("hdr_type", sa.String(length=64)),
    )
    op.create_index("ix_video_streams_codec", "video_streams", ["codec"])
    op.create_index("ix_video_streams_hdr_type", "video_streams", ["hdr_type"])
    op.create_index("ix_video_streams_resolution", "video_streams", ["width", "height"])

    op.create_table(
        "audio_streams",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("media_file_id", sa.Integer(), sa.ForeignKey("media_files.id", ondelete="CASCADE"), nullable=False),
        sa.Column("stream_index", sa.Integer(), nullable=False),
        sa.Column("codec", sa.String(length=64)),
        sa.Column("channels", sa.Integer()),
        sa.Column("channel_layout", sa.String(length=64)),
        sa.Column("sample_rate", sa.Integer()),
        sa.Column("bit_rate", sa.Integer()),
        sa.Column("language", sa.String(length=16)),
        sa.Column("default_flag", sa.Boolean(), nullable=False),
        sa.Column("forced_flag", sa.Boolean(), nullable=False),
    )
    op.create_index("ix_audio_streams_codec", "audio_streams", ["codec"])
    op.create_index("ix_audio_streams_language", "audio_streams", ["language"])
    op.create_index("ix_audio_streams_layout", "audio_streams", ["channel_layout"])

    op.create_table(
        "subtitle_streams",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("media_file_id", sa.Integer(), sa.ForeignKey("media_files.id", ondelete="CASCADE"), nullable=False),
        sa.Column("stream_index", sa.Integer(), nullable=False),
        sa.Column("codec", sa.String(length=64)),
        sa.Column("language", sa.String(length=16)),
        sa.Column("default_flag", sa.Boolean(), nullable=False),
        sa.Column("forced_flag", sa.Boolean(), nullable=False),
        sa.Column("subtitle_type", sa.String(length=32)),
    )
    op.create_index("ix_subtitle_streams_codec", "subtitle_streams", ["codec"])
    op.create_index("ix_subtitle_streams_language", "subtitle_streams", ["language"])

    op.create_table(
        "external_subtitles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("media_file_id", sa.Integer(), sa.ForeignKey("media_files.id", ondelete="CASCADE"), nullable=False),
        sa.Column("path", sa.String(length=2048), nullable=False),
        sa.Column("language", sa.String(length=16)),
        sa.Column("format", sa.String(length=32)),
    )
    op.create_index("ix_external_subtitles_language", "external_subtitles", ["language"])

    op.create_table(
        "scan_jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("library_id", sa.Integer(), sa.ForeignKey("libraries.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", job_status, nullable=False),
        sa.Column("job_type", sa.String(length=32), nullable=False),
        sa.Column("files_total", sa.Integer(), nullable=False),
        sa.Column("files_scanned", sa.Integer(), nullable=False),
        sa.Column("errors", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime()),
        sa.Column("finished_at", sa.DateTime()),
    )
    op.create_index("ix_scan_jobs_status", "scan_jobs", ["status"])


def downgrade() -> None:
    op.drop_index("ix_scan_jobs_status", table_name="scan_jobs")
    op.drop_table("scan_jobs")
    op.drop_index("ix_external_subtitles_language", table_name="external_subtitles")
    op.drop_table("external_subtitles")
    op.drop_index("ix_subtitle_streams_language", table_name="subtitle_streams")
    op.drop_index("ix_subtitle_streams_codec", table_name="subtitle_streams")
    op.drop_table("subtitle_streams")
    op.drop_index("ix_audio_streams_layout", table_name="audio_streams")
    op.drop_index("ix_audio_streams_language", table_name="audio_streams")
    op.drop_index("ix_audio_streams_codec", table_name="audio_streams")
    op.drop_table("audio_streams")
    op.drop_index("ix_video_streams_resolution", table_name="video_streams")
    op.drop_index("ix_video_streams_hdr_type", table_name="video_streams")
    op.drop_index("ix_video_streams_codec", table_name="video_streams")
    op.drop_table("video_streams")
    op.drop_table("media_formats")
    op.drop_index("ix_media_files_scan_status", table_name="media_files")
    op.drop_index("ix_media_files_quality_score", table_name="media_files")
    op.drop_index("ix_media_files_library_relative_path", table_name="media_files")
    op.drop_table("media_files")
    op.drop_table("libraries")

