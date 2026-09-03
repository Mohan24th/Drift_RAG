import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  analyzeDrift,
  approveVersion,
  createDocument,
  getDocument,
  getDocumentVersions,
  getDocuments,
  uploadDocumentVersion,
} from "../api/client";

import { useAuth } from "../auth/AuthContext";


const DEFAULT_DRIFT_QUERIES = [
  "How many vacation days do employees get?",
  "When should employees request leave?",
  "Can unused leave be carried forward?",
  "Who approves leave requests?",
];


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
    selectedDocumentId,
    setSelectedDocumentId,
  ] = useState("");

  const [
    selectedDocument,
    setSelectedDocument,
  ] = useState(null);

  const [
    versions,
    setVersions,
  ] = useState([]);

  const [
    loadingDocuments,
    setLoadingDocuments,
  ] = useState(true);

  const [
    loadingDetails,
    setLoadingDetails,
  ] = useState(false);


  // --------------------------------------------------
  // Create document
  // --------------------------------------------------

  const [
    showCreate,
    setShowCreate,
  ] = useState(false);

  const [
    documentName,
    setDocumentName,
  ] = useState("");

  const [
    documentFile,
    setDocumentFile,
  ] = useState(null);

  const [
    creating,
    setCreating,
  ] = useState(false);


  // --------------------------------------------------
  // Upload version
  // --------------------------------------------------

  const [
    uploadFile,
    setUploadFile,
  ] = useState(null);

  const [
    uploading,
    setUploading,
  ] = useState(false);


  // --------------------------------------------------
  // Drift
  // --------------------------------------------------

  const [
    fromVersion,
    setFromVersion,
  ] = useState("");

  const [
    toVersion,
    setToVersion,
  ] = useState("");

  const [
    driftQueries,
    setDriftQueries,
  ] = useState(
    DEFAULT_DRIFT_QUERIES.join("\n")
  );

  const [
    driftResult,
    setDriftResult,
  ] = useState(null);

  const [
    analyzing,
    setAnalyzing,
  ] = useState(false);


  // --------------------------------------------------
  // Messages
  // --------------------------------------------------

  const [
    error,
    setError,
  ] = useState("");

  const [
    message,
    setMessage,
  ] = useState("");


  // --------------------------------------------------
  // Load documents
  // --------------------------------------------------

  useEffect(() => {
    async function loadDocuments() {
      setLoadingDocuments(true);

      try {
        const data =
          await getDocuments(
            token
          );

        setDocuments(
          data
        );

        if (
          data.length > 0 &&
          !selectedDocumentId
        ) {
          setSelectedDocumentId(
            data[0].id
          );
        }
      } catch (err) {
        setError(
          err.message ||
            "Failed to load documents."
        );
      } finally {
        setLoadingDocuments(
          false
        );
      }
    }

    loadDocuments();
  }, [
    token,
    selectedDocumentId,
  ]);


  // --------------------------------------------------
  // Load selected document
  // --------------------------------------------------

  useEffect(() => {
    if (
      !selectedDocumentId
    ) {
      return;
    }

    async function loadDetails() {
      setLoadingDetails(true);
      setError("");
      setDriftResult(null);

      try {
        const [
          document,
          documentVersions,
        ] = await Promise.all([
          getDocument(
            selectedDocumentId,
            token
          ),
          getDocumentVersions(
            selectedDocumentId,
            token
          ),
        ]);

        setSelectedDocument(
          document
        );

        setVersions(
          documentVersions
        );

        if (
          documentVersions.length >=
          2
        ) {
          setFromVersion(
            String(
              documentVersions[1]
                .version_number
            )
          );

          setToVersion(
            String(
              documentVersions[0]
                .version_number
            )
          );
        } else if (
          documentVersions.length === 1
        ) {
          setFromVersion(
            String(
              documentVersions[0]
                .version_number
            )
          );

          setToVersion("");
        } else {
          setFromVersion("");
          setToVersion("");
        }
      } catch (err) {
        setError(
          err.message ||
            "Failed to load document details."
        );
      } finally {
        setLoadingDetails(
          false
        );
      }
    }

    loadDetails();
  }, [
    selectedDocumentId,
    token,
  ]);


  // --------------------------------------------------
  // Derived values
  // --------------------------------------------------

  const nextVersion =
    useMemo(() => {
      if (
        versions.length === 0
      ) {
        return 1;
      }

      return (
        Math.max(
          ...versions.map(
            (version) =>
              version.version_number
          )
        ) + 1
      );
    }, [versions]);


  // --------------------------------------------------
  // Refresh selected document
  // --------------------------------------------------

  async function refreshDocument() {
    if (
      !selectedDocumentId
    ) {
      return;
    }

    const [
      document,
      documentVersions,
    ] = await Promise.all([
      getDocument(
        selectedDocumentId,
        token
      ),
      getDocumentVersions(
        selectedDocumentId,
        token
      ),
    ]);

    setSelectedDocument(
      document
    );

    setVersions(
      documentVersions
    );

    if (
      documentVersions.length >= 2
    ) {
      setFromVersion(
        String(
          documentVersions[1]
            .version_number
        )
      );

      setToVersion(
        String(
          documentVersions[0]
            .version_number
        )
      );
    }
  }


  // --------------------------------------------------
  // Create new document
  // --------------------------------------------------

  async function handleCreateDocument(
    event
  ) {
    event.preventDefault();

    const name =
      documentName.trim();

    if (!name) {
      setError(
        "Document name cannot be empty."
      );
      return;
    }

    if (!documentFile) {
      setError(
        "Choose a PDF or TXT file."
      );
      return;
    }

    setCreating(true);
    setError("");
    setMessage("");

    try {
      const document =
        await createDocument(
          name,
          token
        );

      const version =
        await uploadDocumentVersion(
          document.id,
          1,
          documentFile,
          token
        );

      const data =
        await getDocuments(
          token
        );

      setDocuments(
        data
      );

      setSelectedDocumentId(
        document.id
      );

      setDocumentName("");
      setDocumentFile(null);
      setShowCreate(false);

      setMessage(
        `${document.name} created. v${version.version_number} is waiting for approval.`
      );
    } catch (err) {
      setError(
        err.message ||
          "Failed to create document."
      );
    } finally {
      setCreating(false);
    }
  }


  // --------------------------------------------------
  // Upload next version
  // --------------------------------------------------

  async function handleUpload(
    event
  ) {
    event.preventDefault();

    if (!uploadFile) {
      setError(
        "Choose a PDF or TXT file."
      );
      return;
    }

    setUploading(true);
    setError("");
    setMessage("");

    try {
      const result =
        await uploadDocumentVersion(
          selectedDocumentId,
          nextVersion,
          uploadFile,
          token
        );

      setMessage(
        `v${result.version_number} uploaded and is waiting for approval.`
      );

      setUploadFile(null);

      event.target.reset();

      await refreshDocument();
    } catch (err) {
      setError(
        err.message ||
          "Failed to upload version."
      );
    } finally {
      setUploading(false);
    }
  }


  // --------------------------------------------------
  // Approve version
  // --------------------------------------------------

  async function handleApprove(
    versionNumber
  ) {
    const confirmed =
      window.confirm(
        `Approve version v${versionNumber}?`
      );

    if (!confirmed) {
      return;
    }

    setError("");
    setMessage("");

    try {
      await approveVersion(
        selectedDocumentId,
        versionNumber,
        token
      );

      setMessage(
        `v${versionNumber} is now approved.`
      );

      await refreshDocument();
    } catch (err) {
      setError(
        err.message ||
          "Failed to approve version."
      );
    }
  }


  // --------------------------------------------------
  // Drift analysis
  // --------------------------------------------------

  async function handleAnalyzeDrift(
    event
  ) {
    event.preventDefault();

    if (
      !fromVersion ||
      !toVersion
    ) {
      setError(
        "Select both versions."
      );
      return;
    }

    if (
      Number(fromVersion) >=
      Number(toVersion)
    ) {
      setError(
        "The 'from' version must be older than the 'to' version."
      );
      return;
    }

    const queries =
      driftQueries
        .split("\n")
        .map(
          (query) =>
            query.trim()
        )
        .filter(Boolean);

    if (
      queries.length === 0
    ) {
      setError(
        "Add at least one question for drift analysis."
      );
      return;
    }

    setAnalyzing(true);
    setError("");
    setDriftResult(null);

    try {
      const result =
        await analyzeDrift(
          selectedDocumentId,
          {
            from_version:
              Number(fromVersion),
            to_version:
              Number(toVersion),
            queries,
            top_k: 3,
          },
          token
        );

      setDriftResult(
        result
      );
    } catch (err) {
      setError(
        err.message ||
          "Drift analysis failed."
      );
    } finally {
      setAnalyzing(false);
    }
  }


  return (
    <div className="admin-page">

      {/* ------------------------------------------- */}
      {/* Header */}
      {/* ------------------------------------------- */}

      <header className="admin-header">

        <div className="brand">
          <div className="brand-mark">
            DR
          </div>

          <div>
            <h1>
              Drift RAG
            </h1>

            <span>
              Administration
            </span>
          </div>
        </div>


        <div className="admin-user">

          <div>
            <strong>
              {user.username}
            </strong>

            <span>
              {user.role}
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


      {/* ------------------------------------------- */}
      {/* Messages */}
      {/* ------------------------------------------- */}

      {error && (
        <div className="admin-alert error">
          <strong>
            Error
          </strong>

          <span>
            {error}
          </span>
        </div>
      )}


      {message && (
        <div className="admin-alert success">
          <strong>
            Done
          </strong>

          <span>
            {message}
          </span>
        </div>
      )}


      {/* ------------------------------------------- */}
      {/* Dashboard */}
      {/* ------------------------------------------- */}

      <main className="admin-layout">

        {/* ========================================= */}
        {/* Sidebar */}
        {/* ========================================= */}

        <aside className="document-sidebar">

          <div className="sidebar-header">
            <div>
              <span className="section-kicker">
                KNOWLEDGE BASE
              </span>

              <h2>
                Documents
              </h2>
            </div>

            <button
              type="button"
              className="add-button"
              onClick={() =>
                setShowCreate(
                  !showCreate
                )
              }
            >
              {showCreate
                ? "×"
                : "+"}
            </button>
          </div>


          {/* New document form */}

          {showCreate && (
            <form
              className="create-document-form"
              onSubmit={
                handleCreateDocument
              }
            >
              <h3>
                Add document
              </h3>

              <input
                type="text"
                value={
                  documentName
                }
                onChange={(
                  event
                ) =>
                  setDocumentName(
                    event.target
                      .value
                  )
                }
                placeholder="Human Rights Policy"
                maxLength={200}
                required
              />

              <input
                type="file"
                accept=".pdf,.txt"
                onChange={(
                  event
                ) =>
                  setDocumentFile(
                    event.target
                      .files?.[0] ||
                      null
                  )
                }
              />

              <button
                type="submit"
                className="primary-button"
                disabled={
                  creating
                }
              >
                {creating
                  ? "Creating..."
                  : "Create & Upload v1"}
              </button>
            </form>
          )}


          <div className="document-list">

            {loadingDocuments && (
              <p className="muted">
                Loading...
              </p>
            )}

            {!loadingDocuments &&
              documents.length ===
                0 && (
                <p className="muted">
                  No documents yet.
                </p>
              )}

            {documents.map(
              (document) => (
                <button
                  key={
                    document.id
                  }
                  type="button"
                  className={
                    selectedDocumentId ===
                    document.id
                      ? "document-item active"
                      : "document-item"
                  }
                  onClick={() =>
                    setSelectedDocumentId(
                      document.id
                    )
                  }
                >
                  <span className="document-icon">
                    DOC
                  </span>

                  <span>
                    <strong>
                      {
                        document.name
                      }
                    </strong>

                    <small>
                      {new Date(
                        document.created_at
                      ).toLocaleDateString()}
                    </small>
                  </span>
                </button>
              )
            )}

          </div>

        </aside>


        {/* ========================================= */}
        {/* Content */}
        {/* ========================================= */}

        <section className="admin-content">

          {!selectedDocument && (
            <div className="empty-dashboard">
              <div className="empty-icon">
                DR
              </div>

              <h2>
                Select a document
              </h2>

              <p>
                Choose a document from
                the knowledge base to
                manage versions and
                review drift.
              </p>
            </div>
          )}


          {selectedDocument && (
            <>

              {/* ----------------------------------- */}
              {/* Document header */}
              {/* ----------------------------------- */}

              <div className="document-heading">

                <div>
                  <span className="section-kicker">
                    DOCUMENT
                  </span>

                  <h2>
                    {
                      selectedDocument.name
                    }
                  </h2>

                  <p>
                    {
                      selectedDocument
                        .versions_count
                    }{" "}
                    version
                    {
                      selectedDocument
                        .versions_count === 1
                        ? ""
                        : "s"
                    }
                  </p>
                </div>

                <div className="document-meta">
                  Created{" "}
                  {new Date(
                    selectedDocument.created_at
                  ).toLocaleDateString()}
                </div>

              </div>


              {/* ----------------------------------- */}
              {/* Version history */}
              {/* ----------------------------------- */}

              <section className="admin-card">

                <div className="card-header">
                  <div>
                    <span className="section-kicker">
                      HISTORY
                    </span>

                    <h3>
                      Versions
                    </h3>
                  </div>
                </div>


                {loadingDetails ? (
                  <p className="muted">
                    Loading versions...
                  </p>
                ) : versions.length ===
                  0 ? (
                  <div className="empty-state">
                    <strong>
                      No versions uploaded
                    </strong>

                    <span>
                      Upload the first version
                      using the panel below.
                    </span>
                  </div>
                ) : (
                  <div className="version-list">

                    {versions.map(
                      (version) => (
                        <div
                          className="version-row"
                          key={
                            version.id
                          }
                        >

                          <div className="version-number">
                            <strong>
                              v
                              {
                                version.version_number
                              }
                            </strong>
                          </div>


                          <div className="version-info">
                            <strong>
                              {
                                version.status
                              }
                            </strong>

                            <span>
                              Uploaded{" "}
                              {new Date(
                                version.created_at
                              ).toLocaleDateString()}
                            </span>
                          </div>


                          <span
                            className={
                              version.status ===
                              "APPROVED"
                                ? "status-badge approved"
                                : "status-badge draft"
                            }
                          >
                            {
                              version.status ===
                              "APPROVED"
                                ? "Approved"
                                : "Draft"
                            }
                          </span>


                          {version.status ===
                            "DRAFT" && (
                            <button
                              type="button"
                              className="approve-button"
                              onClick={() =>
                                handleApprove(
                                  version.version_number
                                )
                              }
                            >
                              Approve
                            </button>
                          )}

                        </div>
                      )
                    )}

                  </div>
                )}

              </section>


              {/* ----------------------------------- */}
              {/* Upload */}
              {/* ----------------------------------- */}

              <section className="admin-card">

                <div className="card-header">
                  <div>
                    <span className="section-kicker">
                      DOCUMENT MANAGEMENT
                    </span>

                    <h3>
                      Upload new version
                    </h3>

                    <p>
                      This will create{" "}
                      <strong>
                        v
                        {
                          nextVersion
                        }
                      </strong>{" "}
                      as a draft.
                    </p>
                  </div>
                </div>


                <form
                  className="upload-area"
                  onSubmit={
                    handleUpload
                  }
                >

                  <label className="file-picker">

                    <input
                      type="file"
                      accept=".pdf,.txt"
                      onChange={(
                        event
                      ) =>
                        setUploadFile(
                          event.target
                            .files?.[0] ||
                            null
                        )
                      }
                    />

                    <span>
                      {uploadFile
                        ? uploadFile.name
                        : "Choose a PDF or TXT file"}
                    </span>

                    <small>
                      Maximum 10 MB
                    </small>

                  </label>


                  <button
                    type="submit"
                    className="primary-button"
                    disabled={
                      uploading ||
                      !uploadFile
                    }
                  >
                    {uploading
                      ? "Uploading..."
                      : `Upload v${nextVersion}`}
                  </button>

                </form>

              </section>


              {/* ----------------------------------- */}
              {/* Drift */}
              {/* ----------------------------------- */}

              {versions.length >=
                2 && (
                <section className="admin-card">

                  <div className="card-header">
                    <div>
                      <span className="section-kicker">
                        POLICY ANALYSIS
                      </span>

                      <h3>
                        Compare versions
                      </h3>

                      <p>
                        Find questions whose
                        answers may have changed.
                      </p>
                    </div>
                  </div>


                  <form
                    className="drift-form"
                    onSubmit={
                      handleAnalyzeDrift
                    }
                  >

                    <div className="version-selects">

                      <label>
                        <span>
                          From
                        </span>

                        <select
                          value={
                            fromVersion
                          }
                          onChange={(
                            event
                          ) =>
                            setFromVersion(
                              event.target
                                .value
                            )
                          }
                        >
                          <option value="">
                            Select
                          </option>

                          {versions.map(
                            (
                              version
                            ) => (
                              <option
                                key={
                                  version.id
                                }
                                value={
                                  version.version_number
                                }
                              >
                                v
                                {
                                  version.version_number
                                }
                              </option>
                            )
                          )}
                        </select>
                      </label>


                      <span className="version-arrow">
                        →
                      </span>


                      <label>
                        <span>
                          To
                        </span>

                        <select
                          value={
                            toVersion
                          }
                          onChange={(
                            event
                          ) =>
                            setToVersion(
                              event.target
                                .value
                            )
                          }
                        >
                          <option value="">
                            Select
                          </option>

                          {versions.map(
                            (
                              version
                            ) => (
                              <option
                                key={
                                  version.id
                                }
                                value={
                                  version.version_number
                                }
                              >
                                v
                                {
                                  version.version_number
                                }
                              </option>
                            )
                          )}
                        </select>
                      </label>

                    </div>


                    <label>
                      <span>
                        Questions to evaluate
                      </span>

                      <textarea
                        rows={5}
                        value={
                          driftQueries
                        }
                        onChange={(
                          event
                        ) =>
                          setDriftQueries(
                            event.target
                              .value
                          )
                        }
                      />

                      <small>
                        One question per line.
                      </small>
                    </label>


                    <button
                      type="submit"
                      className="primary-button"
                      disabled={
                        analyzing
                      }
                    >
                      {analyzing
                        ? "Analyzing..."
                        : "Run drift analysis"}
                    </button>

                  </form>

                </section>
              )}


              {/* ----------------------------------- */}
              {/* Drift results */}
              {/* ----------------------------------- */}

              {driftResult && (
                <section className="drift-results">

                  <div className="drift-summary">

                    <div>
                      <span className="section-kicker">
                        DRIFT RESULT
                      </span>

                      <h3>
                        v
                        {
                          driftResult.from_version
                        }
                        {" "}
                        →
                        {" "}
                        v
                        {
                          driftResult.to_version
                        }
                      </h3>
                    </div>


                    <div className="drift-stat">
                      <span>
                        Overall
                      </span>

                      <strong>
                        {
                          driftResult
                            .overall_level
                        }
                      </strong>
                    </div>


                    <div className="drift-stat">
                      <span>
                        Score
                      </span>

                      <strong>
                        {Number(
                          driftResult
                            .overall_score
                        ).toFixed(3)}
                      </strong>
                    </div>


                    <div className="drift-stat">
                      <span>
                        Affected
                      </span>

                      <strong>
                        {
                          driftResult
                            .affected_queries
                        }
                        /
                        {
                          driftResult
                            .queries_evaluated
                        }
                      </strong>
                    </div>

                  </div>


                  <div className="drift-reports">

                    {driftResult.reports.map(
                      (
                        report,
                        index
                      ) => (
                        <article
                          className="drift-report"
                          key={`${report.query}-${index}`}
                        >

                          <div className="report-header">

                            <div>
                              <span className="report-number">
                                {index + 1}
                              </span>

                              <h4>
                                {
                                  report.query
                                }
                              </h4>
                            </div>

                          </div>


                          <div className="metrics-grid">

                            <div>
                              <span>
                                Retrieval overlap
                              </span>

                              <strong>
                                {(
                                  report
                                    .retrieval_overlap *
                                  100
                                ).toFixed(0)}
                                %
                              </strong>
                            </div>

                            <div>
                              <span>
                                Rank change
                              </span>

                              <strong>
                                {(
                                  report
                                    .rank_change *
                                  100
                                ).toFixed(0)}
                                %
                              </strong>
                            </div>

                            <div>
                              <span>
                                Semantic change
                              </span>

                              <strong>
                                {(
                                  report
                                    .semantic_change *
                                  100
                                ).toFixed(1)}
                                %
                              </strong>
                            </div>

                          </div>


                          {report.changes
                            ?.length >
                            0 && (
                            <div className="changes-list">

                              <span className="section-kicker">
                                CHANGES
                              </span>

                              {report.changes.map(
                                (
                                  change,
                                  changeIndex
                                ) => (
                                  <div
                                    className="change-item"
                                    key={`${change.chunk_index}-${changeIndex}`}
                                  >

                                    <div className="change-type">
                                      {
                                        change.change_type
                                      }

                                      {" · Chunk "}
                                      {
                                        change.chunk_index
                                      }
                                    </div>


                                    <div className="change-columns">

                                      <div>
                                        <span>
                                          Previous
                                        </span>

                                        <p>
                                          {
                                            change.v1_text ||
                                            "Not present"
                                          }
                                        </p>
                                      </div>


                                      <div>
                                        <span>
                                          New
                                        </span>

                                        <p>
                                          {
                                            change.v2_text ||
                                            "Not present"
                                          }
                                        </p>
                                      </div>

                                    </div>

                                  </div>
                                )
                              )}

                            </div>
                          )}

                        </article>
                      )
                    )}

                  </div>

                </section>
              )}

            </>
          )}

        </section>

      </main>

    </div>
  );
}