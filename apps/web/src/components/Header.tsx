import type React from "react";

type HeaderProps = {
  authUser: string | null;
  onSignOut: () => void;
  theme: {
    header: React.CSSProperties;
    title: React.CSSProperties;
    subtitle: React.CSSProperties;
    tabButton: (active: boolean) => React.CSSProperties;
  };
};

export function Header({ authUser, onSignOut, theme }: HeaderProps) {
  return (
    <header style={theme.header}>
      <div>
        <h1 style={theme.title}>Job Intelligence Agent</h1>
        <p style={theme.subtitle}>Signal-first discovery with transparent pipeline traces.</p>
      </div>
      {authUser && (
        <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
          <span style={{ fontFamily: "'Recursive', 'Work Sans', sans-serif", color: "#334155" }}>
            {authUser}
          </span>
          <button type="button" onClick={onSignOut} style={theme.tabButton(false)}>
            Sign Out
          </button>
        </div>
      )}
    </header>
  );
}
