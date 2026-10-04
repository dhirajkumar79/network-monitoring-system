import { useEffect, useState } from "react";
import api from "../api/client";
import Layout from "../components/Layout";
export default function Alerts() {
  const [events, setEvents] = useState([]);
  const [severity, setSeverity] = useState("ALL");
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    const fetchEvents = async () => {
      try {
        const url =
          severity === "ALL"
            ? "/api/events?limit=200"
            : `/api/events?limit=200&severity=${severity}`;
        const res = await api.get(url);
        setEvents(res.data.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    setLoading(true);
    fetchEvents();
  }, [severity]);
  return (
    <Layout>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Alerts & Events</h2>
        <div className="flex gap-2">
          {["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"].map((s) => (
            <button
              key={s}
              onClick={() => setSeverity(s)}
              className={`px-3 py-1 text-sm rounded border ${
                severity === s
                  ? "bg-blue-600 text-white border-blue-600"
                  : "bg-white text-gray-700 border-gray-300 hover:bg-gray-50"
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>
      <div className="bg-white rounded-lg shadow">
        {loading ? (
          <div className="p-6 text-center text-gray-500">Loading...</div>
        ) : events.length === 0 ? (
          <div className="p-6 text-center text-gray-500">No events</div>
        ) : (
          <ul className="divide-y">
            {events.map((e) => (
              <li key={e.event_id} className="px-6 py-4">
                <div className="flex justify-between items-start">
                  <div>
                    <span className="font-medium text-gray-800">{e.event_type}</span>
                    <SeverityBadge severity={e.severity} />
                    <div className="text-sm text-gray-600 mt-1">{e.description}</div>
                  </div>
                  <div className="text-xs text-gray-400 whitespace-nowrap ml-4">
                    {new Date(e.timestamp).toLocaleString()}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </Layout>
  );
}
function SeverityBadge({ severity }) {
  const styles = {
    CRITICAL: "bg-red-600 text-white",
    HIGH: "bg-red-100 text-red-800",
    MEDIUM: "bg-yellow-100 text-yellow-800",
    LOW: "bg-gray-100 text-gray-700",
  };
  return (
    <span className={`ml-2 inline-block px-2 py-0.5 text-xs font-semibold rounded ${styles[severity] || styles.LOW}`}>
      {severity}
    </span>
  );
}
