import { NavLink, Outlet } from "react-router-dom";
import { useTranslation } from "react-i18next";

import { useScanJobs } from "../lib/scan-jobs";

export function AppShell() {
  const { t } = useTranslation();
  const { activeJobs } = useScanJobs();

  return (
    <div className="layout media-app-shell">
      <div className="bg-shapes" />
      <header className="panel hero-panel">
        <div className="app-header media-header">
          <div>
            <h1>{t("app.title")}</h1>
          </div>
          <nav className="tabs has-pill media-nav" aria-label="Primary">
            <NavLink
              to="/"
              end
              className={({ isActive }) => `tab-button ${isActive ? "active" : ""}`.trim()}
            >
              {t("nav.dashboard")}
            </NavLink>
            <NavLink
              to="/libraries"
              className={({ isActive }) => `tab-button ${isActive ? "active" : ""}`.trim()}
            >
              {t("nav.libraries")}
            </NavLink>
          </nav>
        </div>
        {activeJobs.length > 0 ? (
          <div className="scan-banner">
            <div className="scan-banner-copy">
              <strong>Scan running in background</strong>
              <span>
                {activeJobs.length} active job{activeJobs.length > 1 ? "s" : ""}. Reloading or
                navigating away in the UI does not stop them.
              </span>
            </div>
            <div className="scan-banner-list">
              {activeJobs.map((job) => (
                <div className="scan-banner-job" key={job.id}>
                  <div className="distribution-copy">
                    <strong>{job.library_name ?? `Library #${job.library_id}`}</strong>
                    <span>{job.files_total > 0 ? `${job.files_scanned}/${job.files_total}` : job.phase_label}</span>
                  </div>
                  <div className="progress">
                    <span style={{ width: `${job.progress_percent}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : null}
      </header>
      <Outlet />
    </div>
  );
}
