import type React from "react";

type AuthPanelProps = {
  authUser: string | null;
  authHasSession: boolean;
  authStatus: string | null;
  email: string;
  password: string;
  resetEmail: string;
  resetMode: boolean;
  newPassword: string;
  confirmPassword: string;
  onEmailChange: (value: string) => void;
  onPasswordChange: (value: string) => void;
  onResetEmailChange: (value: string) => void;
  onNewPasswordChange: (value: string) => void;
  onConfirmPasswordChange: (value: string) => void;
  onSignIn: (event: React.FormEvent) => void;
  onSignUp: () => void;
  onSignOut: () => void;
  onResetPassword: () => void;
  onCompletePasswordReset: (event: React.FormEvent) => void;
  theme: {
    card: React.CSSProperties;
    sectionTitle: React.CSSProperties;
  };
};

export function AuthPanel({
  authUser,
  authHasSession,
  authStatus,
  email,
  password,
  resetEmail,
  resetMode,
  newPassword,
  confirmPassword,
  onEmailChange,
  onPasswordChange,
  onResetEmailChange,
  onNewPasswordChange,
  onConfirmPasswordChange,
  onSignIn,
  onSignUp,
  onSignOut,
  onResetPassword,
  onCompletePasswordReset,
  theme
}: AuthPanelProps) {
  return (
    <section style={theme.card}>
      <h2 style={theme.sectionTitle}>Sign In</h2>
      {authUser ? (
        <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
          <span>
            Signed in as {authUser} {authHasSession ? "(session active)" : "(no session)"}
          </span>
          <button type="button" onClick={onSignOut}>
            Sign Out
          </button>
        </div>
      ) : (
        <form onSubmit={onSignIn} style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <input
            type="email"
            value={email}
            onChange={(e) => onEmailChange(e.target.value)}
            placeholder="Email"
            required
            style={{ flex: "1 1 200px", padding: 8 }}
          />
          <input
            type="password"
            value={password}
            onChange={(e) => onPasswordChange(e.target.value)}
            placeholder="Password"
            required
            style={{ flex: "1 1 200px", padding: 8 }}
          />
          <button type="submit">Sign In</button>
          <button type="button" onClick={onSignUp}>
            Sign Up
          </button>
        </form>
      )}
      {authStatus && <p style={{ marginTop: 8 }}>{authStatus}</p>}
      {!authUser && (
        <div style={{ marginTop: 12, display: "flex", gap: 8, flexWrap: "wrap" }}>
          <input
            type="email"
            value={resetEmail}
            onChange={(e) => onResetEmailChange(e.target.value)}
            placeholder="Email for reset"
            style={{ flex: "1 1 200px", padding: 8 }}
          />
          <button type="button" onClick={onResetPassword}>
            Send Reset Link
          </button>
        </div>
      )}
      {resetMode && (
        <form onSubmit={onCompletePasswordReset} style={{ marginTop: 16 }}>
          <h3>Set New Password</h3>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <input
              type="password"
              value={newPassword}
              onChange={(e) => onNewPasswordChange(e.target.value)}
              placeholder="New password"
              required
              style={{ flex: "1 1 200px", padding: 8 }}
            />
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => onConfirmPasswordChange(e.target.value)}
              placeholder="Confirm password"
              required
              style={{ flex: "1 1 200px", padding: 8 }}
            />
            <button type="submit">Update Password</button>
          </div>
          <p style={{ marginTop: 8, color: "#555" }}>Minimum 8 characters.</p>
        </form>
      )}
    </section>
  );
}
