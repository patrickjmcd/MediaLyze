import type { ReactNode } from "react";

type AsyncPanelProps = {
  title: string;
  subtitle?: string;
  loading?: boolean;
  error?: string | null;
  bodyClassName?: string;
  children: ReactNode;
};

export function AsyncPanel({
  title,
  subtitle,
  loading,
  error,
  bodyClassName,
  children,
}: AsyncPanelProps) {
  return (
    <section className="panel async-panel">
      <div className="panel-header">
        <div>
          <h2>{title}</h2>
          {subtitle ? <p className="subtitle">{subtitle}</p> : null}
        </div>
      </div>
      <div className={`async-panel-body ${bodyClassName ?? ""}`.trim()}>
        {loading ? <div className="notice">Loading…</div> : null}
        {error ? <div className="alert">{error}</div> : null}
        {!loading && !error ? children : null}
      </div>
    </section>
  );
}
