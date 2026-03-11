import { createContext, useContext, useEffect, useEffectEvent, useMemo, useState, type ReactNode } from "react";

import { api, type ScanJob } from "./api";
import { getIdlePollInterval, usePageVisibility } from "./page-visibility";

type ScanJobsContextValue = {
  activeJobs: ScanJob[];
  hasActiveJobs: boolean;
  refresh: () => Promise<void>;
  stopAll: () => Promise<void>;
};

const ScanJobsContext = createContext<ScanJobsContextValue | null>(null);

export function ScanJobsProvider({ children }: { children: ReactNode }) {
  const [activeJobs, setActiveJobs] = useState<ScanJob[]>([]);
  const isPageVisible = usePageVisibility();
  const pollInterval = isPageVisible ? (activeJobs.length > 0 ? 3000 : getIdlePollInterval()) : null;

  const refresh = useEffectEvent(async () => {
    try {
      const jobs = await api.activeScanJobs();
      setActiveJobs(jobs);
    } catch {
      // Keep the last known active jobs on transient polling errors.
    }
  });

  const stopAll = useEffectEvent(async () => {
    try {
      await api.cancelActiveScanJobs();
      setActiveJobs([]);
    } catch {
      // Keep the last known state on transient errors.
    }
  });

  useEffect(() => {
    void refresh();
    if (pollInterval === null) {
      return undefined;
    }

    const timer = window.setInterval(() => {
      void refresh();
    }, pollInterval);

    return () => {
      window.clearInterval(timer);
    };
  }, [pollInterval, refresh]);

  const value = useMemo(
    () => ({
      activeJobs,
      hasActiveJobs: activeJobs.length > 0,
      refresh,
      stopAll,
    }),
    [activeJobs],
  );

  return <ScanJobsContext.Provider value={value}>{children}</ScanJobsContext.Provider>;
}

export function useScanJobs() {
  const context = useContext(ScanJobsContext);
  if (!context) {
    throw new Error("useScanJobs must be used inside ScanJobsProvider");
  }
  return context;
}
