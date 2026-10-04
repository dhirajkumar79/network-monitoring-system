import { useEffect, useState } from "react";
import api from "../api/client";
import { useAuth } from "../context/AuthContext";
export default function Dashboard() {
  const { user, logout } = useAuth();
  const [devices, setDevices] = useState([]);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [devicesRes, eventsRes] = await Promise.all([
          api.get("/api/devices"),
          api.get("/api/events?limit=5"),
        ]);
        setDevices(devicesRes.data.data);
        setEvents(eventsRes.data.data);
      } catch (err) {
        console.error("Fetch error:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);
  const total = devices.length;
  const online = devices.filter((d) => d.status === "ONLINE").length;
  const offline = devices.filter((d) => d.status === "OFFLINE").length;
  const unknown = devices.filter((d) => d.status === "UNKNOWN").length;
  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <h1 className="text-xl font-bold text-gray-800">
            Network Monitoring Dashboard
          </h1>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">
              {user?.username} ({user?.role})
            </span>
            <button
              onClick={logout}
              className="text-sm bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded"
            >
              Logout
            </button>
          </div>
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-6 py-8">
        {loading ? (
          <div className="text-center text-gray-500">Loading...</div>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
              <StatCard label="Total Devices" value={total} color="blue" />
              <StatCard label="Online" value={online} color="green" />
              <StatCard label="Offline" value={offline} color="red" />
              <StatCard label="Unknown" value={unknown} color="gray" />
            </div>
            <div className="bg-white rounded-lg shadow mb-8">
              <div className="px-6 py-4 border-b">
                <h2 className="font-semibold text-gray-800">Devices</h2>
              </div>
              <table className="w-full text-left">
                <thead className="bg-gray-50 text-xs uppercase text-gray-500">
                  <tr>
                    <th className="px-6 py-3">Device</th>
                    <th className="px-6 py-3">Hostname</th>
                    <th className="px-6 py-3">IP</th>
                    <th className="px-6 py-3">Status</th>
                    <th className="px-6 py-3">Last Active</th>
                  </tr>
                </thead>
                <tbody>
                  {devices.length === 0 ? (
                    <tr>
                      <td colSpan="5" className="px-6 py-4 text-center text-gray-500">
                        No devices yet
                      </td>
                    </tr>
                  ) : (
                    devices.map((d) => (
                      <tr key={d.device_id} className="border-t hover:bg-gray-50">
                        <td className="px-6 py-3 text-sm">{d.device_name}</td>
                        <td className="px-6 py-3 text-sm text-gray-600">{d.hostname}</td>
                        <td className="px-6 py-3 text-sm text-gray-600">{d.ip_address || "-"}</td>
                        <td className="px-6 py-3"><StatusBadge status={d.status} /></td>
                        <td className="px-6 py-3 text-sm text-gray-600">
                          {d.last_active_time ? new Date(d.last_active_time).toLocaleString() : "-"}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b">
                <h2 className="font-semibold text-gray-800">Recent Events</h2>
              </div>
              <ul className="divide-y">
                {events.length === 0 ? (
                  <li className="px-6 py-4 text-center text-gray-500">No events yet</li>
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
          </>
        )}
      </main>
    </div>
  );
}
function StatCard({ label, value, color }) {
  const colors = {
    blue: "bg-blue-500",
    green: "bg-green-500",
    red: "bg-red-500",
    gray: "bg-gray-400",
  };
  return (
    <div className="bg-white rounded-lg shadow p-5">
      <div className="text-sm text-gray-500 mb-1">{label}</div>
      <div className="flex items-center gap-3">
        <span className={`inline-block w-3 h-3 rounded-full ${colors[color]}`} />
        <span className="text-3xl font-bold text-gray-800">{value}</span>
      </div>
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
    <span className={`inline-block px-2 py-1 text-xs font-semibold rounded ${styles[status] || styles.UNKNOWN}`}>
      {status}
    </span>
  );
}
