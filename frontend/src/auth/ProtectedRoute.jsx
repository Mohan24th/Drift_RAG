import {
  Navigate,
  Outlet,
} from "react-router-dom";

import { useAuth } from "./AuthContext";

export default function ProtectedRoute({
  allowedRoles,
}) {
  const {
    isAuthenticated,
    user,
  } = useAuth();

  if (!isAuthenticated) {
    return (
      <Navigate
        to="/login"
        replace
      />
    );
  }

  if (
    allowedRoles &&
    !allowedRoles.includes(
      user?.role
    )
  ) {
    return (
      <Navigate
        to="/app"
        replace
      />
    );
  }

  return <Outlet />;
}