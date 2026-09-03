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


  // --------------------------------------------------
  // Documents
  // --------------------------------------------------

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
    loadingDocumentDetails,
    setLoadingDocumentDetails,
  ] = useState(false);


  // --------------------------------------------------
  // Create document
  // --------------------------------------------------

  const [
    showCreateDocument,
    setShowCreateDocument,
  ] = useState(false);

  const [
    newDocumentName,
    setNewDocumentName,
  ] = useState("");

  const [
    newDocumentFile,
    setNewDocumentFile,
  ] = useState(null);

  const [
    creatingDocument,
    setCreatingDocument,
  ] = useState(false);


  // --------------------------------------------------
  // General messages
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
  // Existing version upload
  // --------------------------------------------------

  const [
    selectedFile,
    setSelectedFile,
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
    analyzingDrift,
    setAnalyzingDrift,
  ] = useState(false);


  // --------------------------------------------------
  // Load documents
  // --------------------------------------------------

  useEffect(() => {
    async function loadDocuments() {
      setLoadingDocuments(true);
      setError("");

      try {
        const data =
          await getDocuments(
            token
          );

        setDocuments(data);

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

    async function loadDocumentDetails() {
      setLoadingDocumentDetails(
        true
      );

      setError("");
      setMessage("");
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
        setLoadingDocumentDetails(
          false
        );
      }
    }

    loadDocumentDetails();
  }, [
    selectedDocumentId,
    token,
  ]);


  // --------------------------------------------------
  // Derived values
  // --------------------------------------------------

  const nextVersionNumber =
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

  async function refreshSelectedDocument(
    documentId = selectedDocumentId
  ) {
    if (!documentId) {
      return;
    }

    const [
      document,
      documentVersions,
    ] = await Promise.all([
      getDocument(
        documentId,
        token
      ),
      getDocumentVersions(
        documentId,
        token
      ),
    ]);

    setSelectedDocument(
      document
    );

    setVersions(
      documentVersions
    );
  }


  // --------------------------------------------------
  // Create new document + v1
  // --------------------------------------------------

  async function handleCreateDocument(
    event
  ) {
    event.preventDefault();

    const name =
      newDocumentName.trim();

    if (!name) {
      setError(
        "Document name cannot be empty."
      );
      return;
    }

    if (!newDocumentFile) {
      setError(
        "Choose a PDF or TXT file."
      );
      return;
    }

    const extension =
      newDocumentFile.name
        .split(".")
        .pop()
        ?.toLowerCase();

    if (
      !["pdf", "txt"].includes(
        extension
      )
    ) {
      setError(
        "Only PDF and TXT files are supported."
      );
      return;
    }

    setCreatingDocument(true);
    setError("");
    setMessage("");

    try {
      // ----------------------------------------------
      // 1. Create document metadata
      // ----------------------------------------------
      const document =
        await createDocument(
          name,
          token
        );

      // ----------------------------------------------
      // 2. Upload first version
      // ----------------------------------------------
      const version =
        await uploadDocumentVersion(
          document.id,
          1,
          newDocumentFile,
          token
        );

      // ----------------------------------------------
      // 3. Refresh list
      // ----------------------------------------------
      const updatedDocuments =
        await getDocuments(
          token
        );

      setDocuments(
        updatedDocuments
      );

      // ----------------------------------------------
      // 4. Select newly created document
      // ----------------------------------------------
      setSelectedDocumentId(
        document.id
      );

      // ----------------------------------------------
      // 5. Reset form
      // ----------------------------------------------
      setNewDocumentName("");
      setNewDocumentFile(null);
      setShowCreateDocument(
        false
      );

      setMessage(
        `${document.name} created successfully. Version v${version.version_number} is currently DRAFT.`
      );

    } catch (err) {
      setError(
        err.message ||
          "Failed to create document."
      );
    } finally {
      setCreatingDocument(
        false
      );
    }
  }


  // --------------------------------------------------
  // Existing version upload
  // --------------------------------------------------

  async function handleUpload(
    event
  ) {
    event.preventDefault();

    if (
      !selectedDocumentId
    ) {
      setError(
        "Select a document first."
      );
      return;
    }

    if (!selectedFile) {
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
          nextVersionNumber,
          selectedFile,
          token
        );

      setMessage(
        `Version v${result.version_number} uploaded successfully as DRAFT.`
      );

      setSelectedFile(null);

      event.target.reset();

      await refreshSelectedDocument();

    } catch (err) {
      setError(
        err.message ||
          "Failed to upload document version."
      );
    } finally {
      setUploading(false);
    }
  }


  // --------------------------------------------------
  // Approve
  // --------------------------------------------------

  async function handleApprove(
    versionNumber
  ) {
    setError("");
    setMessage("");

    try {
      await approveVersion(
        selectedDocumentId,
        versionNumber,
        token
      );

      setMessage(
        `Version v${versionNumber} has been approved.`
      );

      await refreshSelectedDocument();

    } catch (err) {
      setError(
        err.message ||
          `Failed to approve v${versionNumber}.`
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
      !selectedDocumentId
    ) {
      setError(
        "Select a document first."
      );
      return;
    }

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
      Number(fromVersion) ===
      Number(toVersion)
    ) {
      setError(
        "Select two different versions."
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
        "Enter at least one drift query."
      );
      return;
    }

    setAnalyzingDrift(
      true
    );

    setError("");
    setMessage("");
    setDriftResult(null);

    try {
      const result =
        await analyzeDrift(
          selectedDocumentId,
          {
            from_version:
              Number(
                fromVersion
              ),
            to_version:
              Number(
                toVersion
              ),
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
      setAnalyzingDrift(
        false
      );
    }
  }


  return (
    <main>

      {/* ------------------------------------------------ */}
      {/* Header */}
      {/* ------------------------------------------------ */}

      <header>
        <div>
          <h1>
            Drift RAG Admin
          </h1>

          <p>
            Signed in as{" "}
            <strong>
              {user.username}
            </strong>{" "}
            ({user.role})
          </p>
        </div>

        <button
          onClick={logout}
          type="button"
        >
          Sign out
        </button>
      </header>


      {/* ------------------------------------------------ */}
      {/* Global messages */}
      {/* ------------------------------------------------ */}

      {error && (
        <article>
          <strong>
            Error
          </strong>

          <p>
            {error}
          </p>
        </article>
      )}


      {message && (
        <article>
          <strong>
            Success
          </strong>

          <p>
            {message}
          </p>
        </article>
      )}


      {/* ------------------------------------------------ */}
      {/* Documents */}
      {/* ------------------------------------------------ */}

      <section>
        <header>
          <h2>
            Documents
          </h2>

          <button
            type="button"
            onClick={() =>
              setShowCreateDocument(
                (current) =>
                  !current
              )
            }
          >
            {showCreateDocument
              ? "Cancel"
              : "+ Add New Document"}
          </button>
        </header>


        {/* ---------------------------------------------- */}
        {/* Create new document */}
        {/* ---------------------------------------------- */}

        {showCreateDocument && (
          <article>
            <h3>
              Create New Document
            </h3>

            <form
              onSubmit={
                handleCreateDocument
              }
            >
              <label>
                Document name

                <input
                  type="text"
                  value={
                    newDocumentName
                  }
                  onChange={(
                    event
                  ) =>
                    setNewDocumentName(
                      event.target
                        .value
                    )
                  }
                  placeholder="Human Rights Policy"
                  maxLength={200}
                  required
                />
              </label>

              <label>
                Initial document

                <input
                  type="file"
                  accept=".pdf,.txt"
                  onChange={(
                    event
                  ) =>
                    setNewDocumentFile(
                      event.target
                        .files?.[0] ||
                        null
                    )
                  }
                />
              </label>

              <p>
                The uploaded file will
                become version{" "}
                <strong>
                  v1 DRAFT
                </strong>
                . You can approve it
                after reviewing it.
              </p>

              <button
                type="submit"
                disabled={
                  creatingDocument
                }
              >
                {creatingDocument
                  ? "Creating..."
                  : "Create Document"}
              </button>
            </form>
          </article>
        )}


        {/* ---------------------------------------------- */}
        {/* Document list */}
        {/* ---------------------------------------------- */}

        {loadingDocuments && (
          <p>
            Loading documents...
          </p>
        )}

        {!loadingDocuments &&
          documents.length ===
            0 && (
            <p>
              No documents found.
            </p>
          )}

        {!loadingDocuments &&
          documents.length > 0 && (
            <div>
              {documents.map(
                (document) => (
                  <button
                    key={
                      document.id
                    }
                    type="button"
                    onClick={() =>
                      setSelectedDocumentId(
                        document.id
                      )
                    }
                  >
                    {document.name}
                  </button>
                )
              )}
            </div>
          )}
      </section>


      {/* ------------------------------------------------ */}
      {/* Selected document */}
      {/* ------------------------------------------------ */}

      {selectedDocument && (
        <>

          <section>
            <h2>
              {
                selectedDocument.name
              }
            </h2>

            <p>
              Created:{" "}
              {new Date(
                selectedDocument.created_at
              ).toLocaleString()}
            </p>

            <p>
              Versions:{" "}
              {
                selectedDocument
                  .versions_count
              }
            </p>
          </section>


          {/* -------------------------------------------- */}
          {/* Version history */}
          {/* -------------------------------------------- */}

          <section>
            <h2>
              Version History
            </h2>

            {loadingDocumentDetails && (
              <p>
                Loading versions...
              </p>
            )}

            {!loadingDocumentDetails &&
              versions.length ===
                0 && (
                <p>
                  No versions found.
                </p>
              )}

            {!loadingDocumentDetails &&
              versions.map(
                (version) => (
                  <article
                    key={
                      version.id
                    }
                  >
                    <h3>
                      v
                      {
                        version.version_number
                      }
                    </h3>

                    <p>
                      Status:{" "}
                      <strong>
                        {
                          version.status
                        }
                      </strong>
                    </p>

                    <p>
                      Created:{" "}
                      {new Date(
                        version.created_at
                      ).toLocaleString()}
                    </p>

                    {version.approved_at && (
                      <p>
                        Approved:{" "}
                        {new Date(
                          version.approved_at
                        ).toLocaleString()}
                      </p>
                    )}

                    {version.status ===
                      "DRAFT" && (
                      <button
                        type="button"
                        onClick={() =>
                          handleApprove(
                            version.version_number
                          )
                        }
                      >
                        Approve v
                        {
                          version.version_number
                        }
                      </button>
                    )}
                  </article>
                )
              )}
          </section>


          {/* -------------------------------------------- */}
          {/* Upload next version */}
          {/* -------------------------------------------- */}

          <section>
            <h2>
              Upload New Version
            </h2>

            <p>
              Next version:{" "}
              <strong>
                v
                {
                  nextVersionNumber
                }
              </strong>
            </p>

            <form
              onSubmit={
                handleUpload
              }
            >
              <input
                type="file"
                accept=".pdf,.txt"
                onChange={(
                  event
                ) =>
                  setSelectedFile(
                    event.target
                      .files?.[0] ||
                      null
                  )
                }
              />

              <button
                type="submit"
                disabled={
                  uploading ||
                  !selectedFile
                }
              >
                {uploading
                  ? "Uploading..."
                  : "Upload Version"}
              </button>
            </form>
          </section>


          {/* -------------------------------------------- */}
          {/* Drift */}
          {/* -------------------------------------------- */}

          <section>
            <h2>
              Drift Analysis
            </h2>

            {versions.length <
              2 && (
              <p>
                At least two versions
                are required for
                comparison.
              </p>
            )}

            {versions.length >=
              2 && (
              <form
                onSubmit={
                  handleAnalyzeDrift
                }
              >
                <label>
                  From version

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
                      Select version
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
                          }{" "}
                          (
                          {
                            version.status
                          }
                          )
                        </option>
                      )
                    )}
                  </select>
                </label>

                <label>
                  To version

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
                      Select version
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
                          }{" "}
                          (
                          {
                            version.status
                          }
                          )
                        </option>
                      )
                    )}
                  </select>
                </label>

                <label>
                  Queries

                  <textarea
                    rows={8}
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
                </label>

                <button
                  type="submit"
                  disabled={
                    analyzingDrift
                  }
                >
                  {analyzingDrift
                    ? "Analyzing..."
                    : "Run Drift Analysis"}
                </button>
              </form>
            )}
          </section>


          {/* -------------------------------------------- */}
          {/* Drift result */}
          {/* -------------------------------------------- */}

          {driftResult && (
            <section>
              <h2>
                Drift Result
              </h2>

              <article>
                <h3>
                  Overall Drift:{" "}
                  {
                    driftResult.overall_level
                  }
                </h3>

                <p>
                  Overall score:{" "}
                  {
                    driftResult.overall_score
                  }
                </p>

                <p>
                  Queries evaluated:{" "}
                  {
                    driftResult.queries_evaluated
                  }
                </p>

                <p>
                  Affected queries:{" "}
                  {
                    driftResult.affected_queries
                  }
                  {" / "}
                  {
                    driftResult.queries_evaluated
                  }
                </p>
              </article>

              {driftResult.reports.map(
                (
                  report,
                  index
                ) => (
                  <article
                    key={`${report.query}-${index}`}
                  >
                    <h3>
                      {report.query}
                    </h3>

                    <p>
                      Retrieval overlap:{" "}
                      {
                        report.retrieval_overlap
                      }
                    </p>

                    <p>
                      Rank change:{" "}
                      {
                        report.rank_change
                      }
                    </p>

                    <p>
                      Semantic change:{" "}
                      {
                        report.semantic_change
                      }
                    </p>

                    {report.changes
                      ?.length > 0 && (
                      <div>
                        <h4>
                          Changes
                        </h4>

                        {report.changes.map(
                          (
                            change,
                            changeIndex
                          ) => (
                            <article
                              key={
                                `${change.chunk_index}-${changeIndex}`
                              }
                            >
                              <p>
                                <strong>
                                  Chunk{" "}
                                  {
                                    change.chunk_index
                                  }
                                </strong>
                                {" — "}
                                {
                                  change.change_type
                                }
                              </p>

                              {change.v1_text && (
                                <div>
                                  <strong>
                                    Previous
                                    version
                                  </strong>

                                  <p>
                                    {
                                      change.v1_text
                                    }
                                  </p>
                                </div>
                              )}

                              {change.v2_text && (
                                <div>
                                  <strong>
                                    New version
                                  </strong>

                                  <p>
                                    {
                                      change.v2_text
                                    }
                                  </p>
                                </div>
                              )}
                            </article>
                          )
                        )}
                      </div>
                    )}
                  </article>
                )
              )}
            </section>
          )}

        </>
      )}
    </main>
  );
}