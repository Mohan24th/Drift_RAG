const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";

const AUTH_STORAGE_KEY = "drift-rag-auth";


function handleUnauthorized() {
  localStorage.removeItem(
    AUTH_STORAGE_KEY
  );

  window.location.href = "/login?expired=1";
}


async function request(
  path,
  options = {}
) {
  const response = await fetch(
    `${API_BASE_URL}${path}`,
    {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
    }
  );

  let data = null;

  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (response.status === 401) {
    handleUnauthorized();

    const error = new Error(
      "Your session has expired. Please sign in again."
    );

    error.status = 401;
    error.data = data;

    throw error;
  }

  if (!response.ok) {
    const error = new Error(
      data?.detail ||
        data?.error ||
        "Request failed."
    );

    error.status = response.status;
    error.data = data;

    throw error;
  }

  return data;
}


async function uploadRequest(
  path,
  formData,
  token
) {
  const response = await fetch(
    `${API_BASE_URL}${path}`,
    {
      method: "POST",
      headers: {
        Authorization:
          `Bearer ${token}`,
      },
      body: formData,
    }
  );

  let data = null;

  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (response.status === 401) {
    handleUnauthorized();

    const error = new Error(
      "Your session has expired. Please sign in again."
    );

    error.status = 401;
    throw error;
  }

  if (!response.ok) {
    const error = new Error(
      data?.detail ||
        data?.error ||
        "Upload failed."
    );

    error.status = response.status;
    error.data = data;

    throw error;
  }

  return data;
}


export async function login(
  username,
  password
) {
  return request(
    "/auth/login",
    {
      method: "POST",
      body: JSON.stringify({
        username,
        password,
      }),
    }
  );
}


export async function createDocument(
  name,
  token
) {
  return request(
    "/documents/",
    {
      method: "POST",
      headers: {
        Authorization:
          `Bearer ${token}`,
      },
      body: JSON.stringify({
        name,
      }),
    }
  );
}


export async function getDocuments(
  token
) {
  return request(
    "/documents/",
    {
      headers: {
        Authorization:
          `Bearer ${token}`,
      },
    }
  );
}


export async function getAvailableDocuments(
  token
) {
  return request(
    "/documents/available",
    {
      headers: {
        Authorization:
          `Bearer ${token}`,
      },
    }
  );
}


export async function getDocument(
  documentId,
  token
) {
  return request(
    `/documents/${documentId}`,
    {
      headers: {
        Authorization:
          `Bearer ${token}`,
      },
    }
  );
}


export async function getDocumentVersions(
  documentId,
  token
) {
  return request(
    `/documents/${documentId}/versions`,
    {
      headers: {
        Authorization:
          `Bearer ${token}`,
      },
    }
  );
}


export async function uploadDocumentVersion(
  documentId,
  versionNumber,
  file,
  token
) {
  const formData =
    new FormData();

  formData.append(
    "file",
    file
  );

  formData.append(
    "version_number",
    String(versionNumber)
  );

  return uploadRequest(
    `/documents/${documentId}/versions`,
    formData,
    token
  );
}


export async function approveVersion(
  documentId,
  versionNumber,
  token
) {
  return request(
    `/documents/${documentId}/versions/${versionNumber}/approve`,
    {
      method: "POST",
      headers: {
        Authorization:
          `Bearer ${token}`,
      },
    }
  );
}


export async function queryDocument(
  documentId,
  question,
  topK = 3,
  token
) {
  return request(
    `/documents/${documentId}/query`,
    {
      method: "POST",
      headers: {
        Authorization:
          `Bearer ${token}`,
      },
      body: JSON.stringify({
        question,
        top_k: topK,
      }),
    }
  );
}


export async function analyzeDrift(
  documentId,
  payload,
  token
) {
  return request(
    `/documents/${documentId}/drift`,
    {
      method: "POST",
      headers: {
        Authorization:
          `Bearer ${token}`,
      },
      body: JSON.stringify(
        payload
      ),
    }
  );
}