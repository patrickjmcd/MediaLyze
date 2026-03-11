import { useEffect, useState } from "react";

type NavigatorWithConnection = Navigator & {
  connection?: {
    saveData?: boolean;
  };
};

function getInitialVisibility() {
  if (typeof document === "undefined") {
    return true;
  }
  return document.visibilityState !== "hidden";
}

export function usePageVisibility() {
  const [isVisible, setIsVisible] = useState(getInitialVisibility);

  useEffect(() => {
    if (typeof document === "undefined") {
      return undefined;
    }

    function handleVisibilityChange() {
      setIsVisible(document.visibilityState !== "hidden");
    }

    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, []);

  return isVisible;
}

export function getIdlePollInterval() {
  if (typeof navigator === "undefined") {
    return 30000;
  }

  const connection = (navigator as NavigatorWithConnection).connection;
  if (connection?.saveData) {
    return 60000;
  }
  if (navigator.hardwareConcurrency > 0 && navigator.hardwareConcurrency <= 4) {
    return 45000;
  }
  return 30000;
}
