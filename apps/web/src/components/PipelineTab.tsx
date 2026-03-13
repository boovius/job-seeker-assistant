import type React from "react";

import type { PipelineEvent, QueueItem } from "./types";

type PipelineTabProps = {
  pipelineStatus: string | null;
  runPipelineNow: () => void;
  events: PipelineEvent[];
  eventsStatus: string | null;
  eventsClearStatus: string | null;
  loadEvents: () => void;
  clearEvents: () => void;
  queue: QueueItem[];
  queueError: string | null;
  queueClearStatus: string | null;
  loadingQueue: boolean;
  loadQueue: (failedOnly?: boolean) => void;
  clearQueue: () => void;
  configText: string;
  configStatus: string | null;
  setConfigText: (value: string) => void;
  saveConfig: () => void;
  loadConfig: () => void;
  theme: {
    card: React.CSSProperties;
    sectionTitle: React.CSSProperties;
  };
};

export function PipelineTab({
  pipelineStatus,
  runPipelineNow,
  events,
  eventsStatus,
  eventsClearStatus,
  loadEvents,
  clearEvents,
  queue,
  queueError,
  queueClearStatus,
  loadingQueue,
  loadQueue,
  clearQueue,
  configText,
  configStatus,
  setConfigText,
  saveConfig,
  loadConfig,
  theme
}: PipelineTabProps) {
  return (
    <section style={theme.card}>
      <h2 style={theme.sectionTitle}>Controls</h2>
      <div style={{ display: "flex", gap: 8, marginBottom: 12, alignItems: "center" }}>
        <button type="button" onClick={runPipelineNow}>
          Run Pipeline
        </button>
        {pipelineStatus && <span>{pipelineStatus}</span>}
      </div>

      <h3>Source Config</h3>
      <p style={{ color: "#555" }}>Edit YAML to change keyword profiles and enabled sources.</p>
      <textarea
        value={configText}
        onChange={(e) => setConfigText(e.target.value)}
        style={{ width: "100%", minHeight: 220, padding: 10, fontFamily: "monospace" }}
      />
      <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
        <button type="button" onClick={saveConfig}>
          Save Config
        </button>
        <button type="button" onClick={loadConfig}>
          Reload Config
        </button>
        {configStatus && <span>{configStatus}</span>}
      </div>

      <hr style={{ margin: "32px 0" }} />

      <div className="pipeline-grid">
        <div>
          <h3 style={{ marginTop: 0 }}>Pipeline Events</h3>
          <div style={{ display: "flex", gap: 8, marginBottom: 10, alignItems: "center" }}>
            <button type="button" onClick={loadEvents}>
              Refresh Events
            </button>
            <button type="button" onClick={clearEvents}>
              Clear Events
            </button>
            {eventsStatus && <span>{eventsStatus}</span>}
            {eventsClearStatus && <span>{eventsClearStatus}</span>}
          </div>
          {events.length === 0 && <p>No events yet.</p>}
          <ul>
            {events.map((event) => (
              <li key={event.id}>
                <div>
                  <strong>{event.event_type}</strong>
                  {event.message ? ` — ${event.message}` : ""}
                </div>
                <div style={{ color: "#555", fontSize: 14 }}>
                  {event.created_at ? `At ${new Date(event.created_at).toLocaleString()}` : "Time unknown"}
                  {event.task_id ? ` · Task ${event.task_id}` : ""}
                </div>
                {event.payload && (
                  <details style={{ marginTop: 6 }}>
                    <summary>Payload</summary>
                    <pre style={{ whiteSpace: "pre-wrap", fontSize: 12 }}>
                      {JSON.stringify(event.payload, null, 2)}
                    </pre>
                  </details>
                )}
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h3 style={{ marginTop: 0 }}>Queue Status</h3>
          <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
            <button type="button" onClick={() => loadQueue(false)} disabled={loadingQueue}>
              {loadingQueue ? "Loading..." : "Refresh All"}
            </button>
            <button type="button" onClick={() => loadQueue(true)} disabled={loadingQueue}>
              {loadingQueue ? "Loading..." : "Refresh Failed"}
            </button>
            <button type="button" onClick={clearQueue} disabled={loadingQueue}>
              Clear Queue
            </button>
          </div>
          {queueClearStatus && <p>{queueClearStatus}</p>}

          {queueError && <p>{queueError}</p>}
          {!queueError && queue.length === 0 && <p>No queue items.</p>}
          <ul>
            {queue.map((item) => (
              <li key={item.id}>
                <strong>{item.task_type}</strong> — {item.status} (attempts: {item.attempts})
                {item.last_error ? ` — ${item.last_error}` : ""}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}
