import {
  useState,
} from "react";

import {
  queryDocument,
} from "../api/client";

import { useAuth } from "../auth/AuthContext";

const DOCUMENT_ID =
  "647e4ef2-d359-4a93-8a27-f4bece148ee1";

export default function EmployeeApp() {
  const {
    token,
    user,
    logout,
  } = useAuth();

  const [
    question,
    setQuestion,
  ] = useState("");

  const [
    result,
    setResult,
  ] = useState(null);

  const [
    error,
    setError,
  ] = useState("");

  const [
    loading,
    setLoading,
  ] = useState(false);

  async function handleAsk(
    event
  ) {
    event.preventDefault();

    const trimmed =
      question.trim();

    if (!trimmed) {
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const data =
        await queryDocument(
          DOCUMENT_ID,
          trimmed,
          3,
          token
        );

      setResult(data);
    } catch (err) {
      setError(
        err.message ||
          "Unable to get an answer."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <header>
        <div>
          <h1>
            Drift RAG
          </h1>

          <p>
            Welcome,{" "}
            {user.username}
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
          Ask Company AI
        </h2>

        <form
          onSubmit={
            handleAsk
          }
        >
          <textarea
            value={
              question
            }
            onChange={(
              event
            ) =>
              setQuestion(
                event.target
                  .value
              )
            }
            placeholder="Ask a question about company policy..."
            rows={5}
          />

          <button
            type="submit"
            disabled={
              loading ||
              !question.trim()
            }
          >
            {loading
              ? "Thinking..."
              : "Ask"}
          </button>
        </form>

        {error && (
          <p>
            {error}
          </p>
        )}

        {result && (
          <section>
            <h3>
              Answer
            </h3>

            <p>
              {result.answer}
            </p>

            <h3>
              Sources
            </h3>

            {result.sources.map(
              (
                source,
                index
              ) => (
                <article
                  key={
                    `${source.version_number}-${source.chunk_index}-${index}`
                  }
                >
                  <strong>
                    {
                      source.document_name
                    }
                  </strong>

                  <span>
                    {" "}
                    • v
                    {
                      source.version_number
                    }
                  </span>

                  <p>
                    {
                      source.text
                    }
                  </p>
                </article>
              )
            )}
          </section>
        )}
      </section>
    </main>
  );
}