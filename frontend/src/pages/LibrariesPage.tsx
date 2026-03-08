import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { AsyncPanel } from "../components/AsyncPanel";
import { PathBrowser } from "../components/PathBrowser";
import { api, type LibrarySummary } from "../lib/api";
import { formatBytes, formatDate, formatDuration } from "../lib/format";
import { useScanJobs } from "../lib/scan-jobs";

const EMPTY_FORM = {
  name: "",
  path: ".",
  type: "mixed",
  scan_mode: "manual",
};

export function LibrariesPage() {
  const { t } = useTranslation();
  const [libraries, setLibraries] = useState<LibrarySummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState(EMPTY_FORM);
  const { activeJobs, hasActiveJobs } = useScanJobs();

  const loadLibraries = () => {
    api
      .libraries()
      .then((payload) => {
        setLibraries(payload);
        setError(null);
      })
      .catch((reason: Error) => setError(reason.message));
  };

  useEffect(() => {
    loadLibraries();
  }, []);

  useEffect(() => {
    if (!hasActiveJobs) {
      return;
    }
    const timer = window.setInterval(loadLibraries, 3000);
    return () => window.clearInterval(timer);
  }, [hasActiveJobs]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    try {
      await api.createLibrary(form);
      setForm(EMPTY_FORM);
      setSubmitError(null);
      loadLibraries();
    } catch (reason) {
      setSubmitError((reason as Error).message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <>
      <section className="panel stack">
        <p className="eyebrow">{t("libraries.eyebrow")}</p>
        <h2>{t("libraries.title")}</h2>
        <p className="subtitle">{t("libraries.subtitle")}</p>
      </section>

      <div className="media-grid">
        <AsyncPanel
          title="Create library"
          subtitle="Path selection is restricted to directories below MEDIA_ROOT."
          error={submitError}
        >
          <form className="form-grid" onSubmit={handleSubmit}>
            <div className="field">
              <label htmlFor="library-name">Name</label>
              <input
                id="library-name"
                value={form.name}
                onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))}
                placeholder="Movies archive"
                required
              />
            </div>
            <div className="field">
              <label htmlFor="library-type">Library type</label>
              <select
                id="library-type"
                value={form.type}
                onChange={(event) => setForm((current) => ({ ...current, type: event.target.value }))}
              >
                <option value="movies">movies</option>
                <option value="series">series</option>
                <option value="mixed">mixed</option>
                <option value="other">other</option>
              </select>
            </div>
            <PathBrowser
              value={form.path}
              onChange={(path) => setForm((current) => ({ ...current, path }))}
            />
            <button type="submit" disabled={submitting}>
              {submitting ? "Creating…" : "Create library"}
            </button>
          </form>
        </AsyncPanel>

        <AsyncPanel title="Configured libraries" loading={!libraries.length && !error} error={error}>
          <div className="listing">
            {libraries.map((library) => (
              <Link className="media-card library-card" key={library.id} to={`/libraries/${library.id}`}>
                <div className="item-meta">
                  <div className="meta-tags">
                    <span className="badge">{library.type}</span>
                    <span className="badge">{library.scan_mode}</span>
                    {activeJobs
                      .filter((job) => job.library_id === library.id)
                      .map((job) => (
                        <span className="badge scan-badge" key={job.id}>
                          {job.phase_label} {job.files_total > 0 ? `${job.progress_percent}%` : ""}
                        </span>
                      ))}
                  </div>
                  <h3>{library.name}</h3>
                  <p className="media-meta">{library.path}</p>
                </div>
                <div className="library-stats">
                  <span>{library.file_count} files</span>
                  <span>{formatBytes(library.total_size_bytes)}</span>
                  <span>{formatDuration(library.total_duration_seconds)}</span>
                  <span>Last scan: {formatDate(library.last_scan_at)}</span>
                </div>
                {activeJobs.find((job) => job.library_id === library.id) ? (
                  <div className="progress">
                    <span
                      style={{
                        width: `${activeJobs.find((job) => job.library_id === library.id)?.progress_percent ?? 0}%`,
                      }}
                    />
                  </div>
                ) : null}
              </Link>
            ))}
          </div>
        </AsyncPanel>
      </div>
    </>
  );
}
