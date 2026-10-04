import { useEffect, useState } from "react";
import api from "../api/client";
import Layout from "../components/Layout";
export default function Reports() {
  const [devices, setDevices] = useState([]);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [devRes, evtRes] = await Promise.all([
          api.get("/api/devices"),
          api.get("/api/events?limit=500"),
        ]);
        setDevices(devRes.data.data);
        setEvents(evtRes.data.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);
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
  const exportDevices = () => {
    const rows = devices.map((d) => ({
      device_id: d.device_id,
      device_name: d.device_name,
      hostname: d.hostname,
      ip_address: d.ip_address,
      mac_address: d.mac_address,
      operating_system: d.operating_system,
      status: d.status,
      last_active_time: d.last_active_time,
    }));
    downloadCSV(rows, "devices.csv");
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
    downloadCSV(rows, "events.csv");
  };
  const onlineCount = devices.filter((d) => d.status === "ONLINE").length;
  const offlineCount = devices.filter((d) => d.status === "OFFLINE").length;
  const highAlerts = events.filter((e) => e.severity === "HIGH" || e.severity === "CRITICAL").length;
  return (
    <Layout>
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Reports</h2>
      {loading ? (
        <div className="text-center text-gray-500">Loading...</div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <MetricCard label="Total Devices" value={devices.length} />
            <MetricCard label="Online Now" value={onlineCount} />
            <MetricCard label="Offline Now" value={offlineCount} />
            <MetricCard label="High Severity Events" value={highAlerts} />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <ExportCard
              title="Device Report"
              description="All devices with status and last-seen time."
              onExport={exportDevices}
              count={devices.length}
            />
            <ExportCard
              title="Events Report"
              description="All events with severity and timestamps."
              onExport={exportEvents}
              count={events.length}
            />
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
function ExportCard({ title, description, onExport, count }) {
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
