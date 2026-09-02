import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import { AuthProvider } from "./auth/AuthContext";
import ProtectedRoute from "./auth/ProtectedRoute";

import AdminDashboard from "./pages/AdminDashboard";
import EmployeeApp from "./pages/EmployeeApp";
import Login from "./pages/Login";


export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route
            path="/login"
            element={<Login />}
          />

          <Route
            element={
              <ProtectedRoute
                allowedRoles={[
                  "EMPLOYEE",
                  "HR",
                  "ADMIN",
                ]}
              />
            }
          >
            <Route
              path="/app"
              element={
                <EmployeeApp />
              }
            />
          </Route>

          <Route
            element={
              <ProtectedRoute
                allowedRoles={[
                  "HR",
                  "ADMIN",
                ]}
              />
            }
          >
            <Route
              path="/admin"
              element={
                <AdminDashboard />
              }
            />
          </Route>

          <Route
            path="/"
            element={
              <Navigate
                to="/login"
                replace
              />
            }
          />

          <Route
            path="*"
            element={
              <Navigate
                to="/login"
                replace
              />
            }
          />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}