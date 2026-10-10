import { useEffect, useState, useCallback } from "react";
import { Link } from "react-router-dom";
import api from "../api/client";
import Layout from "../components/Layout";
import { useAuth } from "../context/AuthContext";
import { useSocket } from "../context/SocketContext";

export default function Devices() {
  const { isAdmin } = useAuth();
  const { socket } = useSocket();
  const [devices, setDevices] = useState([]);
  const [filter, setFilter] = useState("ALL");
  const [loading, setLoading] = useState(true);

  const fetchDevices = useCallback(async () => {
    try {
      const res = await api.get("/api/devices");
      setDevices(res.data.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDevices();
  }, [fetchDevices]);

  useEffect(() => {
    if (!socket) return;
    const handler = () => fetchDevices();
    socket.on("device_deleted", handler);
    socket.on("device_status_change", handler);
    socket.on("device_heartbeat", handler);
    return () => {
      socket.off("device_deleted", handler);
      socket.off("device_status_change", handler);
      socket.off("device_heartbeat", handler);
    };
  }, [socket, fetchDevices]);

  const deleteDevice = async (device) => {
    const confirmMsg =
      `Delete device "${device.device_name}" (ID ${device.device_id})?\n\n` +
      `This removes ALL its metrics, events, and sessions. Cannot be undone.`;

    if (!window.confirm(confirmMsg)) return;

    try {
      await api.delete(`/api/devices/${device.device_id}`);
      fetchDevices();
    } catch (err) {
      alert(err.response?.data?.message || "Failed to delete device");
    }
  };

  const filtered =
    filter === "ALL" ? devices : devices.filter((d) => d.status === filter);

  return (
    <Layout>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Devices</h2>
        <div className="flex gap-2">
          {["ALL", "ONLINE", "OFFLINE", "UNKNOWN"].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1 text-sm rounded border ${
                filter === f
                  ? "bg-blue-600 text-white border-blue-600"
                  : "bg-white text-gray-700 border-gray-300 hover:bg-gray-50"
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-lg shadow">
        {loading ? (
          <div className="p-6 text-center text-gray-500">Loading...</div>
        ) : filtered.length === 0 ? (
          <div className="p-6 text-center text-gray-500">No devices match.</div>
        ) : (
          <table className="w-full text-left">
            <thead className="bg-gray-50 text-xs uppercase text-gray-500">
              <tr>
                <th className="px-6 py-3">ID</th>
                <th className="px-6 py-3">Device Name</th>
                <th className="px-6 py-3">Hostname</th>
                <th className="px-6 py-3">OS</th>
                <th className="px-6 py-3">IP</th>
                <th className="px-6 py-3">Status</th>
                <th className="px-6 py-3">Last Active</th>
                <th className="px-6 py-3"></th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((d) => (
                <tr key={d.device_id} className="border-t hover:bg-gray-50">
                  <td className="px-6 py-3 text-sm text-gray-500">{d.device_id}</td>
                  <td className="px-6 py-3 text-sm font-medium">{d.device_name}</td>
                  <td className="px-6 py-3 text-sm text-gray-600">{d.hostname}</td>
                  <td className="px-6 py-3 text-sm text-gray-600">
                    {d.operating_system || "-"}
                  </td>
                  <td className="px-6 py-3 text-sm text-gray-600">{d.ip_address || "-"}</td>
                  <td className="px-6 py-3">
                    <StatusBadge status={d.status} />
                  </td>
                  <td className="px-6 py-3 text-sm text-gray-600">
                    {d.last_active_time
                      ? new Date(d.last_active_time).toLocaleString()
                      : "-"}
                  </td>
                  <td className="px-6 py-3 whitespace-nowrap">
                    <Link
                      to={`/devices/${d.device_id}`}
                      className="text-sm text-blue-600 hover:underline mr-3"
                    >
                      View
                    </Link>
                    {isAdmin && (
                      <button
                        onClick={() => deleteDevice(d)}
                        className="text-sm text-red-600 hover:underline"
                      >
                        Delete
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </Layout>
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