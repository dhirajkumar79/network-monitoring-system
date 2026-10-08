import { useEffect, useState, useCallback } from "react";
import api from "../api/client";
import Layout from "../components/Layout";

function isoDaysAgo(days) {
  const d = new Date();
  d.setDate(d.getDate() - days);
  return d.toISOString().slice(0, 10);
}

export default function Reports() {
  const [range, setRange] = useState("7");
  const [summary, setSummary] = useState(null);
  const [availability, setAvailability] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      const from = isoDaysAgo(parseInt(range));
      const params = { from };

      const [sumRes, avRes, sessRes, evtRes] = await Promise.all([
        api.get("/api/reports/summary", { params }),
        api.get("/api/reports/device-availability", { params }),
        api.get("/api/reports/session-durations", { params }),
        api.get("/api/events", { params: { limit: 500, since: from } }),
      ]);

      setSummary(sumRes.data.data);
      setAvailability(avRes.data.data);
      setSessions(sessRes.data.data);
      setEvents(evtRes.data.data);
    } catch (err) {
      console.error("Report fetch error:", err);
    } finally {
      setLoading(false);
    }
  }, [range]);

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  const downloadCSV = (rows, filename) => {
    if (!rows.length) return;
    const headers = Object.keys(rows[0]);
    const csv = [
      headers.join(","),
      ...rows.map((row) =>
        headers
          .map((h) => {
            const v = row[h] ?? "";
            return `"${String(v).replace(/"/g, '""')}"`;
          })
          .join(",")
      ),
    ].join("\n");

    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const exportAvailability = () => {
    downloadCSV(availability, `device_availability_${range}d.csv`);
  };
  const exportSessions = () => {
    downloadCSV(sessions, `sessions_${range}d.csv`);
  };
  const exportEvents = () => {
    const rows = events.map((e) => ({
      event_id: e.event_id,
      device_id: e.device_id,
      event_type: e.event_type,
      severity: e.severity,
      description: e.description,
      timestamp: e.timestamp,
    }));
    downloadCSV(rows, `events_${range}d.csv`);
  };

  return (
    <Layout>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Reports</h2>
        <div className="flex items-center gap-3">
          <label className="text-sm text-gray-600">Range:</label>
          <select
            value={range}
            onChange={(e) => setRange(e.target.value)}
            className="border border-gray-300 rounded px-3 py-1 text-sm"
          >
            <option value="1">Last 24 hours</option>
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 90 days</option>
          </select>
          <button
            onClick={fetchAll}
            className="text-sm bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded"
          >
            Refresh
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-center text-gray-500">Loading...</div>
      ) : (
        <>
          {summary && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              <MetricCard label="Total Devices" value={summary.total_devices} />
              <MetricCard label="Online Now" value={summary.online_now} />
              <MetricCard label="Sessions in Range" value={summary.sessions_in_range} />
              <MetricCard label="High Alerts" value={summary.high_alerts_in_range} />
              <MetricCard
                label="Avg CPU %"
                value={summary.avg_cpu.toFixed(1)}
              />
              <MetricCard
                label="Avg Memory %"
                value={summary.avg_memory.toFixed(1)}
              />
              <MetricCard
                label="Avg Latency (ms)"
                value={summary.avg_latency.toFixed(0)}
              />
              <MetricCard label="Events in Range" value={summary.events_in_range} />
            </div>
          )}

          {/* Export cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <ExportCard
              title="Device Availability"
              description="Per-device metric points and avg CPU in range."
              count={availability.length}
              onExport={exportAvailability}
            />
            <ExportCard
              title="Remote Sessions"
              description="Sessions with duration in seconds."
              count={sessions.length}
              onExport={exportSessions}
            />
            <ExportCard
              title="Events & Alerts"
              description="All events in range with severity."
              count={events.length}
              onExport={exportEvents}
            />
          </div>

          {/* Device availability table */}
          <div className="bg-white rounded-lg shadow mb-8">
            <div className="px-6 py-4 border-b">
              <h3 className="font-semibold text-gray-800">Device Availability</h3>
            </div>
            <table className="w-full text-left">
              <thead className="bg-gray-50 text-xs uppercase text-gray-500">
                <tr>
                  <th className="px-6 py-3">Device</th>
                  <th className="px-6 py-3">Hostname</th>
                  <th className="px-6 py-3">Status</th>
                  <th className="px-6 py-3">Metrics</th>
                  <th className="px-6 py-3">Avg CPU %</th>
                  <th className="px-6 py-3">Last Active</th>
                </tr>
              </thead>
              <tbody>
                {availability.map((d) => (
                  <tr key={d.device_id} className="border-t hover:bg-gray-50">
                    <td className="px-6 py-3 text-sm">{d.device_name}</td>
                    <td className="px-6 py-3 text-sm text-gray-600">
                      {d.hostname}
                    </td>
                    <td className="px-6 py-3 text-sm">{d.current_status}</td>
                    <td className="px-6 py-3 text-sm">{d.metric_points}</td>
                    <td className="px-6 py-3 text-sm">{d.avg_cpu}</td>
                    <td className="px-6 py-3 text-xs text-gray-600">
                      {d.last_active_time
                        ? new Date(d.last_active_time).toLocaleString()
                        : "-"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Sessions table */}
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b">
              <h3 className="font-semibold text-gray-800">
                Session Durations
              </h3>
            </div>
            <table className="w-full text-left">
              <thead className="bg-gray-50 text-xs uppercase text-gray-500">
                <tr>
                  <th className="px-6 py-3">ID</th>
                  <th className="px-6 py-3">Device</th>
                  <th className="px-6 py-3">Type</th>
                  <th className="px-6 py-3">Status</th>
                  <th className="px-6 py-3">Start</th>
                  <th className="px-6 py-3">End</th>
                  <th className="px-6 py-3">Duration</th>
                </tr>
              </thead>
              <tbody>
                {sessions.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="px-6 py-4 text-center text-gray-500">
                      No sessions in range
                    </td>
                  </tr>
                ) : (
                  sessions.map((s) => (
                    <tr key={s.session_id} className="border-t hover:bg-gray-50">
                      <td className="px-6 py-3 text-sm">{s.session_id}</td>
                      <td className="px-6 py-3 text-sm">{s.device_id}</td>
                      <td className="px-6 py-3 text-sm">{s.session_type}</td>
                      <td className="px-6 py-3 text-sm">{s.connection_status}</td>
                      <td className="px-6 py-3 text-xs text-gray-600">
                        {new Date(s.start_time).toLocaleString()}
                      </td>
                      <td className="px-6 py-3 text-xs text-gray-600">
                        {s.end_time ? new Date(s.end_time).toLocaleString() : "-"}
                      </td>
                      <td className="px-6 py-3 text-sm">
                        {s.duration_seconds !== null
                          ? `${s.duration_seconds}s`
                          : "-"}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </>
      )}
    </Layout>
  );
}

function MetricCard({ label, value }) {
  return (
    <div className="bg-white rounded-lg shadow p-5">
      <div className="text-sm text-gray-500 mb-1">{label}</div>
      <div className="text-3xl font-bold text-gray-800">{value}</div>
    </div>
  );
}

function ExportCard({ title, description, count, onExport }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-1">{title}</h3>
      <p className="text-sm text-gray-500 mb-4">{description}</p>
      <div className="text-sm text-gray-600 mb-4">Rows available: {count}</div>
      <button
        onClick={onExport}
        disabled={!count}
        className="bg-blue-600 hover:bg-blue-700 text-white text-sm px-4 py-2 rounded disabled:opacity-50"
      >
        Download CSV
      </button>
    </div>
  );
}