import { createContext, useContext, useEffect, useState } from "react";
import { io } from "socket.io-client";
import { API_BASE_URL } from "../api/client";
const SocketContext = createContext(null);
export function SocketProvider({ children }) {
  const [socket, setSocket] = useState(null);
  const [connected, setConnected] = useState(false);
  useEffect(() => {
    const s = io(API_BASE_URL, {
      transports: ["websocket", "polling"],
    });
    s.on("connect", () => {
      console.log("[socket] connected", s.id);
      setConnected(true);
      s.emit("subscribe_dashboard");
    });
    s.on("disconnect", () => {
      console.log("[socket] disconnected");
      setConnected(false);
    });
    s.on("server_message", (data) => {
      console.log("[socket] server_message:", data);
    });
    setSocket(s);
    return () => {
      s.disconnect();
    };
  }, []);
  return (
    <SocketContext.Provider value={{ socket, connected }}>
      {children}
    </SocketContext.Provider>
  );
}
export function useSocket() {
  return useContext(SocketContext);
}
