import {
  useEffect,
  useState,
} from "react";

import {
  getDocuments,
} from "../api/client";

import { useAuth } from "../auth/AuthContext";

export default function AdminDashboard() {
  const {
    token,
    user,
    logout,
  } = useAuth();

  const [
    documents,
    setDocuments,
  ] = useState([]);

  const [
    loading,
    setLoading,
  ] = useState(true);

  const [
    error,
    setError,
  ] = useState("");

  useEffect(() => {
    async function loadDocuments() {
      try {
        const data =
          await getDocuments(
            token
          );

        setDocuments(
          data
        );
      } catch (err) {
        setError(
          err.message ||
            "Failed to load documents."
        );
      } finally {
        setLoading(
          false
        );
      }
    }

    loadDocuments();
  }, [token]);

  return (
    <main>
      <header>
        <div>
          <h1>
            Drift RAG Admin
          </h1>

          <p>
            Signed in as{" "}
            {user.username}
            {" "}
            ({user.role})
          </p>
        </div>

        <button
          onClick={logout}
        >
          Sign out
        </button>
      </header>

      <section>
        <h2>
          Documents
        </h2>

        {loading && (
          <p>
            Loading...
          </p>
        )}

        {error && (
          <p>
            {error}
          </p>
        )}

        {!loading &&
          !error &&
          documents.length ===
            0 && (
            <p>
              No documents found.
            </p>
          )}

        {documents.map(
          (document) => (
            <article
              key={
                document.id
              }
            >
              <h3>
                {document.name}
              </h3>

              <p>
                Created:{" "}
                {
                  new Date(
                    document.created_at
                  ).toLocaleString()
                }
              </p>
            </article>
          )
        )}
      </section>
    </main>
  );
}