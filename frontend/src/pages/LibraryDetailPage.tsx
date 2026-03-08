import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { AsyncPanel } from "../components/AsyncPanel";
import { DistributionList } from "../components/DistributionList";
import { StatCard } from "../components/StatCard";
import { api, type LibraryDetail, type MediaFileRow, type ScanJob } from "../lib/api";
import { formatBytes, formatDate, formatDuration } from "../lib/format";
import { useScanJobs } from "../lib/scan-jobs";

export function LibraryDetailPage() {
  const { libraryId = "" } = useParams();
  const [library, setLibrary] = useState<LibraryDetail | null>(null);
  const [files, setFiles] = useState<MediaFileRow[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [scanState, setScanState] = useState<string | null>(null);
  const [settingsState, setSettingsState] = useState<string | null>(null);
  const [scanHistory, setScanHistory] = useState<ScanJob[]>([]);
  const [settingsForm, setSettingsForm] = useState({
    scan_mode: "manual",
    interval_minutes: 60,
    debounce_seconds: 15,
  });
  const { activeJobs, hasActiveJobs, refresh } = useScanJobs();
  const activeJob = activeJobs.find((job) => String(job.library_id) === libraryId) ?? null;

  function loadPage() {
    Promise.all([api.library(libraryId), api.libraryFiles(libraryId), api.libraryScanJobs(libraryId)])
      .then(([libraryPayload, filesPayload, scanJobsPayload]) => {
        setLibrary(libraryPayload);
        setFiles(filesPayload);
        setScanHistory(scanJobsPayload);
        setSettingsForm({
          scan_mode: libraryPayload.scan_mode,
          interval_minutes: Number(libraryPayload.scan_config.interval_minutes ?? 60),
          debounce_seconds: Number(libraryPayload.scan_config.debounce_seconds ?? 15),
        });
        setError(null);
      })
      .catch((reason: Error) => setError(reason.message));
  }

  useEffect(() => {
    loadPage();
  }, [libraryId]);

  useEffect(() => {
    if (!hasActiveJobs) {
      return;
    }
    const timer = window.setInterval(loadPage, 3000);
    return () => window.clearInterval(timer);
  }, [hasActiveJobs, libraryId]);

  async function triggerScan(scanType: string) {
    try {
      const job = await api.scanLibrary(libraryId, scanType);
      setScanState(`Scan job #${job.id} queued as ${job.job_type}. Refresh after completion.`);
      await refresh();
      loadPage();
    } catch (reason) {
      setScanState((reason as Error).message);
    }
  }

  async function saveSettings(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    try {
      await api.updateLibrarySettings(libraryId, {
        scan_mode: settingsForm.scan_mode,
        scan_config:
          settingsForm.scan_mode === "scheduled"
            ? { interval_minutes: settingsForm.interval_minutes }
            : settingsForm.scan_mode === "watch"
              ? { debounce_seconds: settingsForm.debounce_seconds }
              : {},
      });
      setSettingsState("Settings saved.");
      loadPage();
    } catch (reason) {
      setSettingsState((reason as Error).message);
    }
  }

  return (
    <>
      <section className="panel stack">
        <div className="detail-back">
          <Link to="/libraries" className="badge">
            Back to libraries
          </Link>
          <div className="toolbar">
            <button type="button" className="secondary small" onClick={() => triggerScan("incremental")}>
              Incremental scan
            </button>
            <button type="button" className="small" onClick={() => triggerScan("full")}>
              Full scan
            </button>
          </div>
        </div>
        {scanState ? <div className="notice">{scanState}</div> : null}
        {activeJob ? (
          <div className="notice">
            <div className="distribution-copy">
              <strong>{activeJob.phase_label}</strong>
              <span>
                {activeJob.files_total > 0
                  ? `${activeJob.files_scanned}/${activeJob.files_total} files`
                  : "Preparing scan"}
              </span>
            </div>
            <div className="progress">
              <span style={{ width: `${activeJob.progress_percent}%` }} />
            </div>
          </div>
        ) : null}
        <p className="eyebrow">Library analysis</p>
        <h2>{library?.name ?? "Loading library…"}</h2>
        <p className="subtitle">{library?.path}</p>
        <div className="card-grid grid">
          <StatCard label="Files" value={String(library?.file_count ?? 0)} />
          <StatCard label="Storage" value={formatBytes(library?.total_size_bytes ?? 0)} tone="teal" />
          <StatCard
            label="Duration"
            value={formatDuration(library?.total_duration_seconds ?? 0)}
            tone="blue"
          />
          <StatCard label="Last scan" value={formatDate(library?.last_scan_at ?? null)} />
        </div>
      </section>

      <div className="media-grid">
        <AsyncPanel title="Scan settings" loading={!library && !error} error={error}>
          <form className="form-grid" onSubmit={saveSettings}>
            <div className="field">
              <label htmlFor="scan-mode">Mode</label>
              <select
                id="scan-mode"
                value={settingsForm.scan_mode}
                onChange={(event) =>
                  setSettingsForm((current) => ({ ...current, scan_mode: event.target.value }))
                }
              >
                <option value="manual">manual</option>
                <option value="scheduled">scheduled</option>
                <option value="watch">watch</option>
              </select>
            </div>
            {settingsForm.scan_mode === "scheduled" ? (
              <div className="field">
                <label htmlFor="interval-minutes">Interval in minutes</label>
                <input
                  id="interval-minutes"
                  type="number"
                  min={5}
                  value={settingsForm.interval_minutes}
                  onChange={(event) =>
                    setSettingsForm((current) => ({
                      ...current,
                      interval_minutes: Number(event.target.value),
                    }))
                  }
                />
              </div>
            ) : null}
            {settingsForm.scan_mode === "watch" ? (
              <div className="field">
                <label htmlFor="debounce-seconds">Debounce in seconds</label>
                <input
                  id="debounce-seconds"
                  type="number"
                  min={3}
                  value={settingsForm.debounce_seconds}
                  onChange={(event) =>
                    setSettingsForm((current) => ({
                      ...current,
                      debounce_seconds: Number(event.target.value),
                    }))
                  }
                />
              </div>
            ) : null}
            <div className="notice">
              <strong>Behavior</strong>
              <p className="subtitle settings-copy">
                `manual` only scans on demand. `scheduled` queues periodic incremental scans.
                `watch` listens for file changes and debounces automatic incremental scans.
              </p>
            </div>
            {settingsState ? <div className="alert success">{settingsState}</div> : null}
            <button type="submit">Save settings</button>
          </form>
        </AsyncPanel>
        <AsyncPanel title="Video codecs" loading={!library && !error} error={error}>
          <DistributionList items={library?.video_codec_distribution ?? []} />
        </AsyncPanel>
        <AsyncPanel title="Resolutions" loading={!library && !error} error={error}>
          <DistributionList items={library?.resolution_distribution ?? []} />
        </AsyncPanel>
        <AsyncPanel title="HDR coverage" loading={!library && !error} error={error}>
          <DistributionList items={library?.hdr_distribution ?? []} />
        </AsyncPanel>
        <AsyncPanel title="Audio languages" loading={!library && !error} error={error}>
          <DistributionList items={library?.audio_language_distribution ?? []} />
        </AsyncPanel>
      </div>

      <AsyncPanel title="Analyzed files" subtitle={`${files.length} indexed entries`} error={error}>
        <div className="media-table">
          <div className="media-table-head">
            <span>File</span>
            <span>Codec</span>
            <span>Resolution</span>
            <span>Duration</span>
            <span>Score</span>
          </div>
          {files.map((file) => (
            <Link className="media-table-row" key={file.id} to={`/files/${file.id}`}>
              <span>
                <strong>{file.filename}</strong>
                <small>{file.relative_path}</small>
              </span>
              <span>{file.video_codec ?? "n/a"}</span>
              <span>{file.resolution ?? "n/a"}</span>
              <span>{formatDuration(file.duration)}</span>
              <span>{file.quality_score}/10</span>
            </Link>
          ))}
        </div>
      </AsyncPanel>

      <AsyncPanel title="Recent scan jobs" subtitle="Latest queue and run history" error={error}>
        <div className="listing">
          {scanHistory.map((job) => (
            <div className="media-card compact-row-card" key={job.id}>
              <div className="stack">
                <strong>Job #{job.id}</strong>
                <span className="media-meta">
                  {job.job_type} · {job.phase_label}
                </span>
              </div>
              <div className="stack">
                <span>
                  {job.files_total > 0 ? `${job.files_scanned}/${job.files_total}` : "discovering"}
                </span>
                <div className="progress">
                  <span style={{ width: `${job.progress_percent}%` }} />
                </div>
              </div>
              <span className="badge">{job.status}</span>
            </div>
          ))}
        </div>
      </AsyncPanel>
    </>
  );
}
