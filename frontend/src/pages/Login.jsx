import {
  useState,
} from "react";
import {
  Navigate,
  useNavigate,
} from "react-router-dom";

import { useAuth } from "../auth/AuthContext";

export default function Login() {
  const {
    login,
    isAuthenticated,
    user,
  } = useAuth();

  const navigate =
    useNavigate();

  const [
    username,
    setUsername,
  ] = useState("");

  const [
    password,
    setPassword,
  ] = useState("");

  const [
    error,
    setError,
  ] = useState("");

  const [
    loading,
    setLoading,
  ] = useState(false);

  if (isAuthenticated) {
    if (
      user?.role === "EMPLOYEE"
    ) {
      return (
        <Navigate
          to="/app"
          replace
        />
      );
    }

    return (
      <Navigate
        to="/admin"
        replace
      />
    );
  }

  async function handleSubmit(
    event
  ) {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      const loggedInUser =
        await login(
          username.trim(),
          password
        );

      if (
        loggedInUser.role ===
        "EMPLOYEE"
      ) {
        navigate(
          "/app",
          { replace: true }
        );
      } else {
        navigate(
          "/admin",
          { replace: true }
        );
      }
    } catch (err) {
      setError(
        err.message ||
          "Login failed."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <section>
        <h1>
          Drift RAG
        </h1>

        <p>
          Company Knowledge
          Assistant
        </p>

        <form
          onSubmit={
            handleSubmit
          }
        >
          <label>
            Username
            <input
              type="text"
              value={
                username
              }
              onChange={(
                event
              ) =>
                setUsername(
                  event.target
                    .value
                )
              }
              autoComplete="username"
              required
            />
          </label>

          <label>
            Password
            <input
              type="password"
              value={
                password
              }
              onChange={(
                event
              ) =>
                setPassword(
                  event.target
                    .value
                )
              }
              autoComplete="current-password"
              required
            />
          </label>

          {error && (
            <p>
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={
              loading
            }
          >
            {loading
              ? "Signing in..."
              : "Sign in"}
          </button>
        </form>
      </section>
    </main>
  );
}