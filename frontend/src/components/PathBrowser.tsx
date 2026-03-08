import { useEffect, useState } from "react";

import { api, type BrowseResponse } from "../lib/api";

type PathBrowserProps = {
  value: string;
  onChange: (value: string) => void;
};

export function PathBrowser({ value, onChange }: PathBrowserProps) {
  const [browser, setBrowser] = useState<BrowseResponse | null>(null);
  const [currentPath, setCurrentPath] = useState<string>(value || ".");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setCurrentPath(value || ".");
  }, [value]);

  useEffect(() => {
    let cancelled = false;
    api
      .browse(currentPath)
      .then((payload) => {
        if (!cancelled) {
          setBrowser(payload);
          setError(null);
        }
      })
      .catch((reason: Error) => {
        if (!cancelled) {
          setError(reason.message);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [currentPath]);

  return (
    <div className="stack">
      <div className="meta-row">
        <span className="meta-label">Selected</span>
        <div className="badge">{value || "."}</div>
      </div>
      {error ? <div className="alert">{error}</div> : null}
      <div className="path-browser">
        <div className="toolbar">
          <strong>{browser?.current_path ?? currentPath}</strong>
          {browser?.parent_path ? (
            <button
              type="button"
              className="secondary small"
              onClick={() => setCurrentPath(browser.parent_path ?? ".")}
            >
              Up
            </button>
          ) : null}
        </div>
        <div className="listing path-list">
          {browser?.entries.filter((entry) => entry.is_dir).map((entry) => (
            <button
              key={entry.path}
              type="button"
              className={`ghost path-entry ${value === entry.path ? "active" : ""}`.trim()}
              onClick={() => {
                setCurrentPath(entry.path);
                onChange(entry.path);
              }}
            >
              <span>{entry.name}</span>
              <span className="subtitle">{entry.path}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

