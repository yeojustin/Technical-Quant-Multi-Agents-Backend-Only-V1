const DEFAULT_ADK_URL = "http://localhost:8000";

/** Resolved at request time so deployments can set ADK_API_URL without rebuilding. */
export function getAdkBaseUrl(): string {
  return process.env.ADK_API_URL || DEFAULT_ADK_URL;
}

export async function proxyToAdk(
  request: Request,
  pathSegments: string[]
): Promise<Response> {
  const path = pathSegments.join("/");
  const requestUrl = new URL(request.url);
  const targetUrl = `${getAdkBaseUrl()}/${path}${requestUrl.search}`;

  const headers = new Headers();
  const contentType = request.headers.get("content-type");
  if (contentType) headers.set("content-type", contentType);
  const accept = request.headers.get("accept");
  if (accept) headers.set("accept", accept);

  const byokKey =
    request.headers.get("x-gemini-api-key") ||
    request.headers.get("X-Gemini-Api-Key");
  if (byokKey) headers.set("X-Gemini-Api-Key", byokKey);

  const init: RequestInit & { duplex?: "half" } = {
    method: request.method,
    headers,
  };

  if (request.method !== "GET" && request.method !== "HEAD") {
    init.body = request.body;
    init.duplex = "half";
  }

  const upstream = await fetch(targetUrl, init);

  if (upstream.status === 204) {
    return new Response(null, { status: 204 });
  }

  const responseHeaders = new Headers();
  for (const name of ["content-type", "content-disposition", "cache-control"]) {
    const value = upstream.headers.get(name);
    if (value) responseHeaders.set(name, value);
  }

  const isSse = upstream.headers
    .get("content-type")
    ?.includes("text/event-stream");
  if (isSse) {
    responseHeaders.set("cache-control", "no-cache");
    responseHeaders.set("connection", "keep-alive");
  }

  return new Response(upstream.body, {
    status: upstream.status,
    headers: responseHeaders,
  });
}
