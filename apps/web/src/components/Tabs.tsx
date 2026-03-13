import type React from "react";

type TabKey = "profile" | "pipeline" | "jobs";

type TabsProps = {
  activeTab: TabKey;
  onTabChange: (tab: TabKey) => void;
  theme: {
    tabBar: React.CSSProperties;
    tabButton: (active: boolean) => React.CSSProperties;
  };
};

export function Tabs({ activeTab, onTabChange, theme }: TabsProps) {
  return (
    <nav style={theme.tabBar}>
      <button type="button" onClick={() => onTabChange("profile")} style={theme.tabButton(activeTab === "profile")}>
        Profile
      </button>
      <button type="button" onClick={() => onTabChange("pipeline")} style={theme.tabButton(activeTab === "pipeline")}>
        Controls
      </button>
      <button type="button" onClick={() => onTabChange("jobs")} style={theme.tabButton(activeTab === "jobs")}>
        Jobs
      </button>
    </nav>
  );
}
