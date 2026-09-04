import {
  useEffect,
  useState,
} from "react";

import {
  getAvailableDocuments,
  queryDocument,
} from "../api/client";

import { useAuth } from "../auth/AuthContext";


export default function EmployeeApp() {
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
    selectedDocumentId,
    setSelectedDocumentId,
  ] = useState("");

  const [
    question,
    setQuestion,
  ] = useState("");

  const [
    result,
    setResult,
  ] = useState(null);

  const [
    loadingDocuments,
    setLoadingDocuments,
  ] = useState(true);

  const [
    loadingAnswer,
    setLoadingAnswer,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState("");


  // --------------------------------------------------
  // Load approved documents
  // --------------------------------------------------

  useEffect(() => {
    let cancelled = false;

    async function loadDocuments() {
      setLoadingDocuments(true);
      setError("");

      try {
        const data =
          await getAvailableDocuments(
            token
          );

        if (cancelled) {
          return;
        }

        setDocuments(
          Array.isArray(data)
            ? data
            : []
        );

        if (
          Array.isArray(data) &&
          data.length > 0
        ) {
          setSelectedDocumentId(
            data[0].id
          );
        } else {
          setSelectedDocumentId("");
        }

      } catch (err) {
        if (cancelled) {
          return;
        }

        setError(
          err.message ||
            "Unable to load company policies."
        );
      } finally {
        if (!cancelled) {
          setLoadingDocuments(
            false
          );
        }
      }
    }

    if (token) {
      loadDocuments();
    }

    return () => {
      cancelled = true;
    };
  }, [token]);


  // --------------------------------------------------
  // Ask question
  // --------------------------------------------------

  async function handleAsk(
    event
  ) {
    event.preventDefault();

    const trimmedQuestion =
      question.trim();

    if (!trimmedQuestion) {
      setError(
        "Please enter a question."
      );
      return;
    }

    if (!selectedDocumentId) {
      setError(
        "Please select a policy."
      );
      return;
    }

    setLoadingAnswer(true);
    setError("");
    setResult(null);

    try {
      const data =
        await queryDocument(
          selectedDocumentId,
          trimmedQuestion,
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
      setLoadingAnswer(
        false
      );
    }
  }


  // --------------------------------------------------
  // Change selected policy
  // --------------------------------------------------

  function handleDocumentChange(
    event
  ) {
    setSelectedDocumentId(
      event.target.value
    );

    setQuestion("");
    setResult(null);
    setError("");
  }


  return (
    <div className="employee-page">

      {/* ============================================== */}
      {/* Header */}
      {/* ============================================== */}

      <header className="app-header">

        <div className="brand">

          <div className="brand-mark">
            DR
          </div>

          <div>
            <h1>
              Drift RAG
            </h1>

            <span>
              Company Knowledge Assistant
            </span>
          </div>

        </div>


        <div className="user-area">

          <div className="user-info">
            <strong>
              {user?.username}
            </strong>

            <span>
              Employee
            </span>
          </div>

          <button
            type="button"
            className="secondary-button"
            onClick={logout}
          >
            Sign out
          </button>

        </div>

      </header>


      {/* ============================================== */}
      {/* Main */}
      {/* ============================================== */}

      <main className="employee-content">

        {/* -------------------------------------------- */}
        {/* Hero */}
        {/* -------------------------------------------- */}

        <section className="hero-section">

          <div className="hero-badge">
            COMPANY AI
          </div>

          <h2>
            Ask about your company policies
          </h2>

          <p>
            Get answers from the latest
            approved company documents.
          </p>

        </section>


        {/* -------------------------------------------- */}
        {/* Question card */}
        {/* -------------------------------------------- */}

        <section className="question-card">

          <form
            onSubmit={
              handleAsk
            }
          >

            <label
              className="field-label"
            >
              Policy
            </label>


            {loadingDocuments ? (
              <div className="loading-box">
                Loading approved policies...
              </div>
            ) : documents.length === 0 ? (
              <div className="empty-box">

                <strong>
                  No approved policies available
                </strong>

                <p>
                  There are currently no
                  approved company documents
                  available for questions.
                </p>

              </div>
            ) : (
              <select
                className="policy-select"
                value={
                  selectedDocumentId
                }
                onChange={
                  handleDocumentChange
                }
                disabled={
                  loadingAnswer
                }
              >
                {documents.map(
                  (document) => (
                    <option
                      key={
                        document.id
                      }
                      value={
                        document.id
                      }
                    >
                      {document.name}
                    </option>
                  )
                )}
              </select>
            )}


            <label
              className="field-label question-label"
            >
              Your question
            </label>


            <textarea
              className="question-input"
              value={
                question
              }
              onChange={(
                event
              ) =>
                setQuestion(
                  event.target.value
                )
              }
              placeholder="e.g. How many vacation days do employees get?"
              rows={5}
              disabled={
                loadingDocuments ||
                documents.length === 0 ||
                loadingAnswer
              }
            />


            <div className="question-footer">

              <span className="input-hint">
                Answers are based on
                approved company policies.
              </span>

              <button
                type="submit"
                className="primary-button"
                disabled={
                  loadingAnswer ||
                  loadingDocuments ||
                  documents.length === 0 ||
                  !question.trim()
                }
              >
                {loadingAnswer
                  ? "Finding answer..."
                  : "Ask question"}
              </button>

            </div>

          </form>

        </section>


        {/* -------------------------------------------- */}
        {/* Error */}
        {/* -------------------------------------------- */}

        {error && (
          <section className="error-card">

            <strong>
              Something went wrong
            </strong>

            <p>
              {error}
            </p>

          </section>
        )}


        {/* -------------------------------------------- */}
        {/* Result */}
        {/* -------------------------------------------- */}

        {result && (
          <section className="answer-section">

            <div className="section-heading">

              <span className="section-kicker">
                RESPONSE
              </span>

              <h3>
                Answer
              </h3>

            </div>


            <div className="answer-card">

              <p className="answer-text">
                {result.answer}
              </p>

            </div>


            {/* ---------------------------------------- */}
            {/* Sources */}
            {/* ---------------------------------------- */}

            <div className="sources-header">

              <span className="section-kicker">
                SOURCES
              </span>

              <h3>
                Based on these policy sections
              </h3>

            </div>


            <div className="sources-list">

              {Array.isArray(
                result.sources
              ) &&
                result.sources.map(
                  (
                    source,
                    index
                  ) => (
                    <article
                      className="source-card"
                      key={
                        `${source.document_name}-${source.version_number}-${source.chunk_index}-${index}`
                      }
                    >

                      <div className="source-top">

                        <div>

                          <strong>
                            {
                              source.document_name
                            }
                          </strong>

                          <span>
                            Version v
                            {
                              source.version_number
                            }
                          </span>

                        </div>

                        <span className="source-badge">
                          Source
                        </span>

                      </div>


                      <p>
                        {
                          source.text
                        }
                      </p>

                    </article>
                  )
                )}

            </div>

          </section>
        )}

      </main>

    </div>
  );
}