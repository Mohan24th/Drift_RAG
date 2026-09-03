import { useState } from "react";

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

  const navigate = useNavigate();

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
          {
            replace: true,
          }
        );
      } else {
        navigate(
          "/admin",
          {
            replace: true,
          }
        );
      }

    } catch (err) {
      setError(
        err.message ||
          "Unable to sign in. Please check your credentials."
      );
    } finally {
      setLoading(false);
    }
  }


  return (
    <div className="login-page">

      <div className="login-shell">

        {/* ---------------------------------------- */}
        {/* Brand */}
        {/* ---------------------------------------- */}

        <div className="login-brand">

          <div className="login-brand-mark">
            DR
          </div>

          <div>
            <div className="login-brand-name">
              Drift RAG
            </div>

            <div className="login-brand-subtitle">
              Company Knowledge Platform
            </div>
          </div>

        </div>


        {/* ---------------------------------------- */}
        {/* Login card */}
        {/* ---------------------------------------- */}

        <section className="login-card">

          <div className="login-heading">

            <span className="section-kicker">
              SECURE ACCESS
            </span>

            <h1>
              Welcome back
            </h1>

            <p>
              Sign in to access your
              company knowledge.
            </p>

          </div>


          <form
            className="login-form"
            onSubmit={
              handleSubmit
            }
          >

            <label>
              <span>
                Username
              </span>

              <input
                type="text"
                value={
                  username
                }
                onChange={(
                  event
                ) =>
                  setUsername(
                    event.target.value
                  )
                }
                placeholder="Enter your username"
                autoComplete="username"
                autoFocus
                required
              />
            </label>


            <label>
              <span>
                Password
              </span>

              <input
                type="password"
                value={
                  password
                }
                onChange={(
                  event
                ) =>
                  setPassword(
                    event.target.value
                  )
                }
                placeholder="Enter your password"
                autoComplete="current-password"
                required
              />
            </label>


            {error && (
              <div className="login-error">
                <strong>
                  Sign in failed
                </strong>

                <span>
                  {error}
                </span>
              </div>
            )}


            <button
              type="submit"
              className="login-button"
              disabled={loading}
            >
              {loading
                ? "Signing in..."
                : "Sign in"}
            </button>

          </form>


          <div className="login-footer">
            <span>
              Your access is protected
              by role-based permissions.
            </span>
          </div>

        </section>


        {/* ---------------------------------------- */}
        {/* Footer */}
        {/* ---------------------------------------- */}

        <p className="login-copyright">
          Drift RAG · Company Knowledge
        </p>

      </div>

    </div>
  );
}