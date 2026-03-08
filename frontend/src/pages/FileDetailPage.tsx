import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { AsyncPanel } from "../components/AsyncPanel";
import { api, type MediaFileDetail } from "../lib/api";
import { formatBytes, formatDuration } from "../lib/format";

function JsonPreview({ value }: { value: unknown }) {
  return <pre className="json-preview">{JSON.stringify(value, null, 2)}</pre>;
}

export function FileDetailPage() {
  const { fileId = "" } = useParams();
  const [file, setFile] = useState<MediaFileDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .file(fileId)
      .then((payload) => {
        setFile(payload);
        setError(null);
      })
      .catch((reason: Error) => setError(reason.message));
  }, [fileId]);

  return (
    <>
      <section className="panel stack">
        <div className="detail-back">
          <Link to={`/libraries/${file?.library_id ?? ""}`} className="badge">
            Back to library
          </Link>
        </div>
        <p className="eyebrow">Media file detail</p>
        <h2>{file?.filename ?? "Loading file…"}</h2>
        <div className="meta-tags">
          <span className="badge">{file?.video_codec ?? "unknown codec"}</span>
          <span className="badge">{file?.resolution ?? "unknown resolution"}</span>
          <span className="badge">{file?.hdr_type ?? "SDR"}</span>
        </div>
        <div className="card-grid grid">
          <article className="media-card metric-card">
            <p className="eyebrow">Relative path</p>
            <h3>{file?.relative_path ?? "…"}</h3>
          </article>
          <article className="media-card metric-card metric-card-teal">
            <p className="eyebrow">Size</p>
            <h3>{formatBytes(file?.size_bytes ?? 0)}</h3>
          </article>
          <article className="media-card metric-card metric-card-blue">
            <p className="eyebrow">Duration</p>
            <h3>{formatDuration(file?.duration ?? 0)}</h3>
          </article>
          <article className="media-card metric-card">
            <p className="eyebrow">Quality</p>
            <h3>{file ? `${file.quality_score}/10` : "…"}</h3>
          </article>
        </div>
      </section>

      <div className="media-grid">
        <AsyncPanel title="Format" loading={!file && !error} error={error}>
          <JsonPreview value={file?.media_format ?? {}} />
        </AsyncPanel>
        <AsyncPanel title="Video streams" loading={!file && !error} error={error}>
          <JsonPreview value={file?.video_streams ?? []} />
        </AsyncPanel>
        <AsyncPanel title="Audio streams" loading={!file && !error} error={error}>
          <JsonPreview value={file?.audio_streams ?? []} />
        </AsyncPanel>
        <AsyncPanel title="Subtitles" loading={!file && !error} error={error}>
          <JsonPreview
            value={{
              internal: file?.subtitle_streams ?? [],
              external: file?.external_subtitles ?? [],
            }}
          />
        </AsyncPanel>
      </div>

      <AsyncPanel title="Raw ffprobe JSON" loading={!file && !error} error={error}>
        <JsonPreview value={file?.raw_ffprobe_json ?? {}} />
      </AsyncPanel>
    </>
  );
}
