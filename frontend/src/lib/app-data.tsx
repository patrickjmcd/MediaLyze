import {
  createContext,
  useContext,
  useEffectEvent,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";

import { api, type DashboardResponse, type LibrarySummary } from "./api";

type AppDataContextValue = {
  dashboard: DashboardResponse | null;
  dashboardLoaded: boolean;
  libraries: LibrarySummary[];
  librariesLoaded: boolean;
  loadDashboard: (force?: boolean) => Promise<DashboardResponse>;
  loadLibraries: (force?: boolean) => Promise<LibrarySummary[]>;
  setDashboard: (payload: DashboardResponse) => void;
  setLibraries: (payload: LibrarySummary[]) => void;
  upsertLibrary: (payload: LibrarySummary) => void;
  removeLibrary: (libraryId: number) => void;
};

const AppDataContext = createContext<AppDataContextValue | null>(null);

export function AppDataProvider({ children }: { children: ReactNode }) {
  const [dashboard, setDashboardState] = useState<DashboardResponse | null>(null);
  const [dashboardLoaded, setDashboardLoaded] = useState(false);
  const [libraries, setLibrariesState] = useState<LibrarySummary[]>([]);
  const [librariesLoaded, setLibrariesLoaded] = useState(false);
  const dashboardRequestRef = useRef<Promise<DashboardResponse> | null>(null);
  const librariesRequestRef = useRef<Promise<LibrarySummary[]> | null>(null);

  const setDashboard = useEffectEvent((payload: DashboardResponse) => {
    setDashboardState(payload);
    setDashboardLoaded(true);
  });

  const setLibraries = useEffectEvent((payload: LibrarySummary[]) => {
    setLibrariesState(payload);
    setLibrariesLoaded(true);
  });

  const upsertLibrary = useEffectEvent((payload: LibrarySummary) => {
    setLibrariesState((current) => {
      const existingIndex = current.findIndex((library) => library.id === payload.id);
      if (existingIndex === -1) {
        return [...current, payload].sort((left, right) => left.name.localeCompare(right.name));
      }

      const next = [...current];
      next[existingIndex] = payload;
      return next;
    });
    setLibrariesLoaded(true);
  });

  const removeLibrary = useEffectEvent((libraryId: number) => {
    setLibrariesState((current) => current.filter((library) => library.id !== libraryId));
    setLibrariesLoaded(true);
  });

  const loadDashboard = useEffectEvent(async (force = false) => {
    if (!force) {
      if (dashboardRequestRef.current) {
        return dashboardRequestRef.current;
      }
      if (dashboardLoaded && dashboard) {
        return dashboard;
      }
    }

    const request = api
      .dashboard()
      .then((payload) => {
        setDashboardState(payload);
        setDashboardLoaded(true);
        return payload;
      })
      .finally(() => {
        if (dashboardRequestRef.current === request) {
          dashboardRequestRef.current = null;
        }
      });

    dashboardRequestRef.current = request;
    return request;
  });

  const loadLibraries = useEffectEvent(async (force = false) => {
    if (!force) {
      if (librariesRequestRef.current) {
        return librariesRequestRef.current;
      }
      if (librariesLoaded) {
        return libraries;
      }
    }

    const request = api
      .libraries()
      .then((payload) => {
        setLibrariesState(payload);
        setLibrariesLoaded(true);
        return payload;
      })
      .finally(() => {
        if (librariesRequestRef.current === request) {
          librariesRequestRef.current = null;
        }
      });

    librariesRequestRef.current = request;
    return request;
  });

  const value = useMemo(
    () => ({
      dashboard,
      dashboardLoaded,
      libraries,
      librariesLoaded,
      loadDashboard,
      loadLibraries,
      setDashboard,
      setLibraries,
      upsertLibrary,
      removeLibrary,
    }),
    [
      dashboard,
      dashboardLoaded,
      libraries,
      librariesLoaded,
      loadDashboard,
      loadLibraries,
      setDashboard,
      setLibraries,
      upsertLibrary,
      removeLibrary,
    ],
  );

  return <AppDataContext.Provider value={value}>{children}</AppDataContext.Provider>;
}

export function useAppData() {
  const context = useContext(AppDataContext);
  if (!context) {
    throw new Error("useAppData must be used inside AppDataProvider");
  }
  return context;
}
