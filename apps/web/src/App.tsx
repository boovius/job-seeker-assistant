import { useEffect, useState } from "react";
import {
  clearPipelineEvents,
  clearWorkflowQueue,
  getPreferences,
  getResume,
  getSourceConfig,
  getValues,
  listJobs,
  listQueue,
  listPipelineEvents,
  runPipeline,
  submitIdealJob,
  submitManualUrl,
  updatePreferences,
  updateResume,
  updateSourceConfig,
  updateValues
} from "./api";
import { supabase } from "./supabase";

import type { Job, PipelineEvent, Preferences, QueueItem } from "./components/types";
import { AuthPanel } from "./components/AuthPanel";
import { Header } from "./components/Header";
import { JobsTab } from "./components/JobsTab";
import { PipelineTab } from "./components/PipelineTab";
import { ProfileTab } from "./components/ProfileTab";
import { Tabs } from "./components/Tabs";

export function App() {
  const [url, setUrl] = useState("");
  const [notes, setNotes] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [idealUrl, setIdealUrl] = useState("");
  const [idealWhy, setIdealWhy] = useState("");
  const [idealStatus, setIdealStatus] = useState<string | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [jobsError, setJobsError] = useState<string | null>(null);
  const [queue, setQueue] = useState<QueueItem[]>([]);
  const [queueError, setQueueError] = useState<string | null>(null);
  const [loadingQueue, setLoadingQueue] = useState(false);
  const [queueClearStatus, setQueueClearStatus] = useState<string | null>(null);
  const [configText, setConfigText] = useState("");
  const [configStatus, setConfigStatus] = useState<string | null>(null);
  const [pipelineStatus, setPipelineStatus] = useState<string | null>(null);
  const [preferences, setPreferences] = useState<Preferences>({
    location: "",
    work_mode: "",
    salary: "",
    salary_period: "",
    sector: "",
    target_role: "",
    company_size: ""
  });
  const [preferencesStatus, setPreferencesStatus] = useState<string | null>(null);
  const [coreValues, setCoreValues] = useState<string>("");
  const [dreamJob, setDreamJob] = useState<string>("");
  const [valuesStatus, setValuesStatus] = useState<string | null>(null);
  const [resumeText, setResumeText] = useState<string>("");
  const [resumeStatus, setResumeStatus] = useState<string | null>(null);
  const [events, setEvents] = useState<PipelineEvent[]>([]);
  const [eventsStatus, setEventsStatus] = useState<string | null>(null);
  const [eventsClearStatus, setEventsClearStatus] = useState<string | null>(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [authStatus, setAuthStatus] = useState<string | null>(null);
  const [authUser, setAuthUser] = useState<string | null>(null);
  const [authHasSession, setAuthHasSession] = useState(false);
  const [activeTab, setActiveTab] = useState<"profile" | "pipeline" | "jobs">("profile");
  const [resetEmail, setResetEmail] = useState("");
  const [resetMode, setResetMode] = useState(false);
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setStatus("Submitting...");

    try {
      await submitManualUrl(url, notes || undefined);
      setStatus("Queued");
      setUrl("");
      setNotes("");
    } catch (err) {
      setStatus("Failed to submit");
    }
  }

  async function onSubmitIdeal(e: React.FormEvent) {
    e.preventDefault();
    setIdealStatus("Submitting...");
    try {
      await submitIdealJob(idealUrl, idealWhy);
      setIdealStatus("Queued");
      setIdealUrl("");
      setIdealWhy("");
    } catch (err) {
      setIdealStatus("Failed to submit");
    }
  }

  async function loadQueue(failedOnly = false) {
    setLoadingQueue(true);
    try {
      const res = await listQueue(failedOnly);
      setQueue(res.items);
      setQueueError(null);
    } catch (err) {
      setQueueError("Unable to load queue");
    } finally {
      setLoadingQueue(false);
    }
  }

  async function clearQueue() {
    setQueueClearStatus("Clearing...");
    try {
      const res = await clearWorkflowQueue();
      setQueue([]);
      setQueueClearStatus(`Cleared ${res.deleted} tasks`);
    } catch (err) {
      setQueueClearStatus("Failed to clear queue");
    }
  }

  async function loadConfig() {
    try {
      const res = await getSourceConfig();
      setConfigText(res.yaml);
      setConfigStatus(`Loaded config from ${res.source}`);
    } catch (err) {
      setConfigStatus("Failed to load config");
    }
  }

  async function saveConfig() {
    setConfigStatus("Saving...");
    try {
      await updateSourceConfig(configText);
      setConfigStatus("Saved");
    } catch (err) {
      setConfigStatus("Save failed");
    }
  }

  async function loadPreferences() {
    try {
      const res = await getPreferences();
      setPreferences({
        location: res.location ?? "",
        work_mode: res.work_mode ?? "",
        salary: "",
        salary_period: res.salary_period ?? "",
        sector: res.sector ?? "",
        target_role: res.target_role ?? "",
        company_size: res.company_size ?? ""
      });
      setPreferencesStatus(null);
    } catch (err) {
      setPreferencesStatus("Failed to load preferences");
    }
  }

  async function savePreferences() {
    setPreferencesStatus("Saving...");
    try {
      await updatePreferences(preferences);
      setPreferencesStatus("Saved");
    } catch (err) {
      setPreferencesStatus("Save failed");
    }
  }

  async function loadValues() {
    try {
      const res = await getValues();
      const valuesList = res.values ?? [];
      setCoreValues(valuesList.join("\n"));
      setDreamJob(res.dream_job_description ?? "");
      setValuesStatus(null);
    } catch (err) {
      setValuesStatus("Failed to load values");
    }
  }

  async function loadResume() {
    try {
      const res = await getResume();
      setResumeText(res.resume_text ?? "");
      setResumeStatus(null);
    } catch (err) {
      setResumeStatus("Failed to load resume");
    }
  }

  async function saveResume() {
    setResumeStatus("Saving...");
    try {
      await updateResume(resumeText);
      setResumeStatus("Saved");
    } catch (err) {
      setResumeStatus("Save failed");
    }
  }

  async function loadEvents() {
    try {
      const res = await listPipelineEvents(50);
      setEvents(res.items);
      setEventsStatus(null);
    } catch (err) {
      setEventsStatus("Failed to load events");
    }
  }

  async function clearEvents() {
    setEventsClearStatus("Clearing...");
    try {
      const res = await clearPipelineEvents();
      setEvents([]);
      setEventsClearStatus(`Cleared ${res.deleted} events`);
    } catch (err) {
      setEventsClearStatus("Failed to clear events");
    }
  }

  async function saveValues() {
    setValuesStatus("Saving...");
    const valuesList = coreValues
      .split("\n")
      .map((value) => value.trim())
      .filter(Boolean);
    try {
      await updateValues({ values: valuesList, dream_job_description: dreamJob });
      setValuesStatus("Saved");
    } catch (err) {
      setValuesStatus("Save failed");
    }
  }

  useEffect(() => {
    listJobs()
      .then((res) => setJobs(res.items))
      .catch(() => setJobsError("Unable to load jobs"));
  }, []);

  useEffect(() => {
    loadQueue(true);
  }, []);

  useEffect(() => {
    loadConfig();
  }, []);

  useEffect(() => {
    loadPreferences();
    loadValues();
    loadResume();
    loadEvents();
  }, []);

  async function runPipelineNow() {
    setPipelineStatus("Running pipeline...");
    try {
      const res = await runPipeline(5);
      const detail = res.message ?? `Queued ${res.tasks} sources`;
      setPipelineStatus(
        `${detail} (worker: ${res.run_worker ? "yes" : "no"}, cycles: ${res.max_cycles ?? 0})`
      );
      await loadQueue(true);
      const jobsRes = await listJobs();
      setJobs(jobsRes.items);
    } catch (err) {
    setPipelineStatus("Failed to run pipeline");
  }
}

  useEffect(() => {
    const { data: subscription } = supabase.auth.onAuthStateChange((event, session) => {
      if (event === "PASSWORD_RECOVERY") {
        setResetMode(true);
        setAuthUser(session?.user?.email ?? null);
        setAuthHasSession(Boolean(session));
      }
      if (event === "SIGNED_IN") {
        setAuthUser(session?.user?.email ?? null);
        setAuthHasSession(Boolean(session));
      }
      if (event === "SIGNED_OUT") {
        setAuthUser(null);
        setAuthHasSession(false);
      }
    });

    supabase.auth.getSession().then(({ data }) => {
      setAuthUser(data.session?.user?.email ?? null);
      setAuthHasSession(Boolean(data.session));
      if (window.location.hash.includes("type=recovery")) {
        setResetMode(true);
      }
    });

    return () => {
      subscription.subscription.unsubscribe();
    };
  }, []);

  async function signIn(e: React.FormEvent) {
    e.preventDefault();
    setAuthStatus("Signing in...");
    const { data, error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) {
      setAuthStatus(`Sign-in failed: ${error.message}`);
      return;
    }
    if (!data.session) {
      setAuthStatus("Signed in. Check email to confirm before API access.");
      setAuthUser(data.user?.email ?? null);
      setAuthHasSession(false);
      return;
    }
    setAuthStatus("Signed in.");
    setAuthUser(data.user?.email ?? null);
    setAuthHasSession(true);
    loadConfig();
    loadQueue(true);
    listJobs()
      .then((res) => setJobs(res.items))
      .catch(() => setJobsError("Unable to load jobs"));
  }

  async function signUp(e: React.FormEvent) {
    e.preventDefault();
    setAuthStatus("Creating account...");
    const { data, error } = await supabase.auth.signUp({ email, password });
    if (error) {
      setAuthStatus(`Sign-up failed: ${error.message}`);
      return;
    }
    if (data.user?.email) {
      setAuthStatus("Account created. Check your email to confirm.");
    } else {
      setAuthStatus("Account created. You may need to confirm via email.");
    }
  }

  async function resetPassword() {
    if (!resetEmail) {
      setAuthStatus("Enter an email to reset.");
      return;
    }
    setAuthStatus("Sending reset email...");
    const { error } = await supabase.auth.resetPasswordForEmail(resetEmail, {
      redirectTo: window.location.origin
    });
    if (error) {
      setAuthStatus(`Reset failed: ${error.message}`);
      return;
    }
    setAuthStatus("Password reset email sent.");
  }

  async function completePasswordReset(e: React.FormEvent) {
    e.preventDefault();
    const trimmedPassword = newPassword.trim();
    if (!trimmedPassword || trimmedPassword.length < 8) {
      setAuthStatus("Password must be at least 8 characters.");
      return;
    }
    if (trimmedPassword !== confirmPassword) {
      setAuthStatus("Passwords do not match.");
      return;
    }
    setAuthStatus("Updating password...");
    const { error } = await supabase.auth.updateUser({ password: trimmedPassword });
    if (error) {
      setAuthStatus(`Password update failed: ${error.message}`);
      return;
    }
    setAuthStatus("Password updated. Redirecting to sign-in...");
    setTimeout(async () => {
      await supabase.auth.signOut();
      setAuthUser(null);
      setAuthHasSession(false);
      setResetMode(false);
      setNewPassword("");
      setConfirmPassword("");
      if (window.location.hash) {
        window.history.replaceState(null, "", window.location.pathname);
      }
    }, 1200);
  }

  async function signOut() {
    await supabase.auth.signOut();
    setAuthUser(null);
    setAuthStatus("Signed out.");
  }

  const theme = {
    page: {
      minHeight: "100vh",
      background: "linear-gradient(180deg, #f7f3ee 0%, #f1f5f9 60%, #ffffff 100%)",
      color: "#1f2937",
      fontFamily: "'Alegreya', 'Source Serif 4', serif"
    },
    container: {
      maxWidth: 1100,
      margin: "0 auto",
      padding: "32px 20px 60px"
    },
    card: {
      background: "#ffffff",
      border: "1px solid #e5e7eb",
      borderRadius: 14,
      padding: 18,
      boxShadow: "0 12px 30px rgba(15, 23, 42, 0.06)"
    },
    header: {
      display: "flex",
      flexWrap: "wrap" as const,
      alignItems: "center",
      justifyContent: "space-between",
      gap: 12,
      marginBottom: 18
    },
    title: {
      fontSize: 34,
      letterSpacing: "-0.5px",
      margin: 0
    },
    subtitle: {
      fontFamily: "'Recursive', 'Work Sans', sans-serif",
      color: "#475569",
      margin: "6px 0 0"
    },
    tabBar: {
      display: "flex",
      gap: 10,
      flexWrap: "wrap" as const,
      marginBottom: 18
    },
    tabButton: (active: boolean) => ({
      border: active ? "1px solid #0f172a" : "1px solid #cbd5f5",
      background: active ? "#0f172a" : "#f8fafc",
      color: active ? "#f8fafc" : "#0f172a",
      padding: "10px 16px",
      borderRadius: 999,
      fontFamily: "'Recursive', 'Work Sans', sans-serif",
      letterSpacing: "0.2px",
      cursor: "pointer",
      transition: "all 0.2s ease"
    }),
    sectionTitle: {
      fontFamily: "'Recursive', 'Work Sans', sans-serif",
      fontSize: 20,
      margin: "0 0 12px"
    }
  };

  return (
    <div style={theme.page}>
      <div style={theme.container}>
        <Header authUser={authUser} onSignOut={signOut} theme={theme} />

        {!authHasSession ? (
          <AuthPanel
            authUser={authUser}
            authHasSession={authHasSession}
            authStatus={authStatus}
            email={email}
            password={password}
            resetEmail={resetEmail}
            resetMode={resetMode}
            newPassword={newPassword}
            confirmPassword={confirmPassword}
            onEmailChange={setEmail}
            onPasswordChange={setPassword}
            onResetEmailChange={setResetEmail}
            onNewPasswordChange={setNewPassword}
            onConfirmPasswordChange={setConfirmPassword}
            onSignIn={signIn}
            onSignUp={signUp}
            onSignOut={signOut}
            onResetPassword={resetPassword}
            onCompletePasswordReset={completePasswordReset}
            theme={theme}
          />
        ) : (
          <>
            <Tabs activeTab={activeTab} onTabChange={setActiveTab} theme={theme} />

            {activeTab === "profile" && (
              <ProfileTab
                idealUrl={idealUrl}
                idealWhy={idealWhy}
                idealStatus={idealStatus}
                onSubmitIdeal={onSubmitIdeal}
                setIdealUrl={setIdealUrl}
                setIdealWhy={setIdealWhy}
                preferences={preferences}
                setPreferences={setPreferences}
                preferencesStatus={preferencesStatus}
                savePreferences={savePreferences}
                loadPreferences={loadPreferences}
                coreValues={coreValues}
                dreamJob={dreamJob}
                valuesStatus={valuesStatus}
                setCoreValues={setCoreValues}
                setDreamJob={setDreamJob}
                saveValues={saveValues}
                loadValues={loadValues}
                resumeText={resumeText}
                resumeStatus={resumeStatus}
                setResumeText={setResumeText}
                saveResume={saveResume}
                loadResume={loadResume}
                theme={theme}
              />
            )}

            {activeTab === "pipeline" && (
              <PipelineTab
                pipelineStatus={pipelineStatus}
                runPipelineNow={runPipelineNow}
                events={events}
                eventsStatus={eventsStatus}
                eventsClearStatus={eventsClearStatus}
                loadEvents={loadEvents}
                clearEvents={clearEvents}
                queue={queue}
                queueError={queueError}
                queueClearStatus={queueClearStatus}
                loadingQueue={loadingQueue}
                loadQueue={loadQueue}
                clearQueue={clearQueue}
                configText={configText}
                configStatus={configStatus}
                setConfigText={setConfigText}
                saveConfig={saveConfig}
                loadConfig={loadConfig}
                theme={theme}
              />
          )}

            {activeTab === "jobs" && (
            <JobsTab
              jobs={jobs}
              jobsError={jobsError}
              url={url}
              notes={notes}
              status={status}
              onSubmit={onSubmit}
              setUrl={setUrl}
              setNotes={setNotes}
              theme={theme}
            />
          )}
        </>
      )}
        <style>
          {`
            .pipeline-grid {
              display: grid;
              grid-template-columns: repeat(2, minmax(0, 1fr));
              gap: 24px;
            }
            @media (max-width: 900px) {
              .pipeline-grid {
                grid-template-columns: 1fr;
              }
            }
          `}
        </style>
      </div>
    </div>
  );
}
