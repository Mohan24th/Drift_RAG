import {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

import { login as loginRequest } from "../api/client";

const AuthContext = createContext(null);

const STORAGE_KEY = "drift-rag-auth";

export function AuthProvider({
  children,
}) {
  const [
    auth,
    setAuth,
  ] = useState(null);

  useEffect(() => {
    const stored =
      localStorage.getItem(
        STORAGE_KEY
      );

    if (!stored) {
      return;
    }

    try {
      setAuth(
        JSON.parse(stored)
      );
    } catch {
      localStorage.removeItem(
        STORAGE_KEY
      );
    }
  }, []);

  async function login(
    username,
    password
  ) {
    const data =
      await loginRequest(
        username,
        password
      );

    const payload =
      decodeJwtPayload(
        data.access_token
      );

    const authState = {
      token: data.access_token,
      username: payload.username,
      role: payload.role,
      userId: payload.sub,
    };

    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify(
        authState
      )
    );

    setAuth(
      authState
    );

    return authState;
  }

  function logout() {
    localStorage.removeItem(
      STORAGE_KEY
    );

    setAuth(null);
  }

  const value = {
    auth,
    token: auth?.token || null,
    user: auth
      ? {
          id: auth.userId,
          username:
            auth.username,
          role: auth.role,
        }
      : null,
    isAuthenticated:
      Boolean(auth?.token),
    login,
    logout,
  };

  return (
    <AuthContext.Provider
      value={value}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context =
    useContext(
      AuthContext
    );

  if (!context) {
    throw new Error(
      "useAuth must be used inside AuthProvider"
    );
  }

  return context;
}

function decodeJwtPayload(
  token
) {
  const parts =
    token.split(".");

  if (parts.length !== 3) {
    throw new Error(
      "Invalid JWT."
    );
  }

  const payload =
    parts[1]
      .replace(/-/g, "+")
      .replace(/_/g, "/");

  const decoded =
    decodeURIComponent(
      atob(payload)
        .split("")
        .map(
          (char) =>
            `%${(
              "00" +
              char.charCodeAt(
                0
              ).toString(16)
            ).slice(-2)}`
        )
        .join("")
    );

  return JSON.parse(
    decoded
  );
}