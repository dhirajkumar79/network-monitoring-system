import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import api from "../api/client";
import Layout from "../components/Layout";
export default function DeviceDetail() {
  const { id } = useParams();
  const [device, setDevice] = useState(null);
  const [metrics, setMetrics] = useState([]);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  useEffect(() => {
    const fetchAll = async () => {
      try {
        const [devRes, metRes, evtRes] = await Promise.all([
          api.get(`/api/devices/${id}`),
          api.get(`/api/devices/${id}/metrics?limit=100`),
          api.get(`/api/devices/${id}/events?limit=20`),
        ]);
        setDevice(devRes.data.data);
        // metrics come newest-first from server; reverse for chart
        setMetrics([...metRes.data.data].reverse());
        setEvents(evtRes.data.data);
      } catch (err) {
        setError(err.response?.data?.message || "Failed to load device");
      } finally {
        setLoading(false);
      }
    };
    fetchAll();
  }, [id]);
  if (loading) {
    return (
      <Layout>
        <div className="text-center text-gray-500">Loading...</div>
      </Layout>
    );
  }
  if (error || !device) {
    return (
      <Layout>
        <div className="bg-red-100 text-red-700 p-4 rounded">
          {error || "Device not found"}
        </div>
        <Link to="/devices" className="text-blue-600 hover:underline mt-4 inline-block">
          ← Back to devices
        </Link>
      </Layout>
    );
  }
  const chartData = metrics.map((m) => ({
    time: new Date(m.timestamp).toLocaleTimeString(),
    cpu: m.cpu_usage,
    mem: m.memory_usage,
    latency: m.latency_ms,
  }));
  return (
    <Layout>
      <Link to="/devices" className="text-sm text-blue-600 hover:underline">
        ← Back to devices
      </Link>
      <div className="flex justify-between items-start mt-4 mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">{device.device_name}</h2>
          <p className="text-sm text-gray-500">{device.hostname}</p>
        </div>
        <StatusBadge status={device.status} />
      </div>
      {/* Info cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <InfoCard label="IP Address" value={device.ip_address || "-"} />
        <InfoCard label="MAC Address" value={device.mac_address || "-"} />
        <InfoCard label="Operating System" value={device.operating_system || "-"} />
        <InfoCard label="Location" value={device.location || "-"} />
      </div>
      {/* Charts */}
      {chartData.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-6 text-center text-gray-500 mb-8">
          No metrics yet for this device.
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <ChartCard title="CPU & Memory Usage (%)">
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" tick={{ fontSize: 10 }} />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Line type="monotone" dataKey="cpu" stroke="#3b82f6" name="CPU %" dot={false} />
                <Line type="monotone" dataKey="mem" stroke="#10b981" name="Memory %" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>
          <ChartCard title="Latency (ms)">
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" tick={{ fontSize: 10 }} />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="latency" stroke="#f59e0b" name="Latency ms" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>
      )}
      {/* Events */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b">
          <h3 className="font-semibold text-gray-800">Recent Events</h3>
        </div>
        <ul className="divide-y">
          {events.length === 0 ? (
            <li className="px-6 py-4 text-center text-gray-500">No events</li>
          ) : (
            events.map((e) => (
              <li key={e.event_id} className="px-6 py-3 text-sm">
                <span className="font-medium">{e.event_type}</span>
                <span className="ml-2 text-xs text-gray-500">[{e.severity}]</span>
                <div className="text-gray-600">{e.description}</div>
                <div className="text-xs text-gray-400 mt-1">
                  {new Date(e.timestamp).toLocaleString()}
                </div>
              </li>
            ))
          )}
        </ul>
      </div>
    </Layout>
  );
}
function InfoCard({ label, value }) {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="text-xs text-gray-500 uppercase mb-1">{label}</div>
      <div className="text-sm font-medium text-gray-800 truncate">{value}</div>
    </div>
  );
}
function ChartCard({ title, children }) {
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h3 className="text-sm font-semibold text-gray-700 mb-3">{title}</h3>
      {children}
    </div>
  );
}
function StatusBadge({ status }) {
  const styles = {
    ONLINE: "bg-green-100 text-green-800",
    OFFLINE: "bg-red-100 text-red-800",
    UNKNOWN: "bg-gray-100 text-gray-800",
  };
  return (
    <span className={`inline-block px-3 py-1 text-xs font-semibold rounded ${styles[status] || styles.UNKNOWN}`}>
      {status}
    </span>
  );
}
