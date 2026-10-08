import { useEffect, useState, useCallback } from "react";
import api from "../api/client";
import Layout from "../components/Layout";
import { useAuth } from "../context/AuthContext";
import { useSocket } from "../context/SocketContext";
export default function Sessions() {
  const { isAdmin } = useAuth();
  const { socket } = useSocket();
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const fetchSessions = useCallback(async () => {
    try {
      const res = await api.get("/api/sessions");
      setSessions(res.data.data);
    } catch (err) {
      console.error("Failed to load sessions:", err);
    } finally {
      setLoading(false);
    }
  }, []);
  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);
  useEffect(() => {
    if (!socket) return;
    const handler = () => fetchSessions();
    socket.on("session_update", handler);
    return () => socket.off("session_update", handler);
  }, [socket, fetchSessions]);
  const endSession = async (id) => {
    if (!window.confirm("End this session?")) return;
    try {
      await api.post(`/api/sessions/${id}/end`);
      fetchSessions();
    } catch (err) {
      alert(err.response?.data?.message || "Failed to end session");
    }
  };
  return (
    <Layout>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Sessions</h2>
        <button
          onClick={fetchSessions}
          className="text-sm bg-gray-200 hover:bg-gray-300 px-3 py-1 rounded"
        >
          Refresh
        </button>
      </div>
      <div className="bg-white rounded-lg shadow">
        {loading ? (
          <div className="p-6 text-center text-gray-500">Loading...</div>
        ) : sessions.length === 0 ? (
          <div className="p-6 text-center text-gray-500">No sessions yet</div>
        ) : (
          <table className="w-full text-left">
            <thead className="bg-gray-50 text-xs uppercase text-gray-500">
              <tr>
                <th className="px-6 py-3">ID</th>
                <th className="px-6 py-3">Device</th>
                <th className="px-6 py-3">User</th>
                <th className="px-6 py-3">Type</th>
                <th className="px-6 py-3">Status</th>
                <th className="px-6 py-3">Start</th>
                <th className="px-6 py-3">End</th>
                <th className="px-6 py-3"></th>
              </tr>
            </thead>
            <tbody>
              {sessions.map((s) => (
                <tr key={s.session_id} className="border-t hover:bg-gray-50">
                  <td className="px-6 py-3 text-sm text-gray-500">{s.session_id}</td>
                  <td className="px-6 py-3 text-sm">{s.device_id}</td>
                  <td className="px-6 py-3 text-sm">{s.user_id}</td>
                  <td className="px-6 py-3 text-sm">{s.session_type}</td>
                  <td className="px-6 py-3">
                    <StatusBadge status={s.connection_status} />
                  </td>
                  <td className="px-6 py-3 text-xs text-gray-600">
                    {new Date(s.start_time).toLocaleString()}
                  </td>
                  <td className="px-6 py-3 text-xs text-gray-600">
                    {s.end_time ? new Date(s.end_time).toLocaleString() : "-"}
                  </td>
                  <td className="px-6 py-3">
                    {isAdmin &&
                      (s.connection_status === "CONNECTING" ||
                        s.connection_status === "CONNECTED") && (
                        <button
                          onClick={() => endSession(s.session_id)}
                          className="text-sm bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded"
                        >
                          End
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
    CONNECTING: "bg-yellow-100 text-yellow-800",
    CONNECTED: "bg-green-100 text-green-800",
    DISCONNECTED: "bg-gray-100 text-gray-700",
    FAILED: "bg-red-100 text-red-800",
  };
  return (
    <span className={`inline-block px-2 py-1 text-xs font-semibold rounded ${styles[status] || styles.DISCONNECTED}`}>
      {status}
    </span>
  );
}
