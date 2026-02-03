const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000';

const DEFAULT_TIMEOUT_MS = 12000;

function withTimeout(signal?: AbortSignal, timeoutMs = DEFAULT_TIMEOUT_MS) {
  const controller = new AbortController();
  let didTimeout = false;

  const timer = setTimeout(() => {
    didTimeout = true;
    controller.abort();
  }, timeoutMs);

  if (signal) {
    if (signal.aborted) {
      controller.abort();
    } else {
      signal.addEventListener('abort', () => controller.abort(), { once: true });
    }
  }

  return {
    signal: controller.signal,
    timedOut: () => didTimeout,
    cleanup: () => clearTimeout(timer),
  } as const;
}

export async function fetchPreview(markdown: string, signal?: AbortSignal) {
  const { signal: mergedSignal, timedOut, cleanup } = withTimeout(signal);

  try {
    const res = await fetch(`${API_BASE}/api/preview`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ markdown }),
      signal: mergedSignal,
    });

    if (!res.ok) {
      throw new Error(`Preview request failed: ${res.status}`);
    }

    return res.json();
  } catch (err) {
    if (err instanceof DOMException && err.name === 'AbortError' && timedOut()) {
      throw new Error('timeout');
    }
    throw err;
  } finally {
    cleanup();
  }
}

export async function generateDocx(
  markdown: string,
  config: Record<string, unknown>,
) {
  const { signal: mergedSignal, timedOut, cleanup } = withTimeout();

  try {
    const res = await fetch(`${API_BASE}/api/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ markdown, config }),
      signal: mergedSignal,
    });

    if (!res.ok) {
      throw new Error(`Generate request failed: ${res.status}`);
    }

    return res.blob();
  } catch (err) {
    if (err instanceof DOMException && err.name === 'AbortError' && timedOut()) {
      throw new Error('timeout');
    }
    throw err;
  } finally {
    cleanup();
  }
}

export async function fetchExportStats() {
  const { signal: mergedSignal, timedOut, cleanup } = withTimeout();

  try {
    const res = await fetch(`${API_BASE}/api/exports/stats`, { signal: mergedSignal });

    if (!res.ok) {
      throw new Error(`Export stats request failed: ${res.status}`);
    }

    return res.json();
  } catch (err) {
    if (err instanceof DOMException && err.name === 'AbortError' && timedOut()) {
      throw new Error('timeout');
    }
    throw err;
  } finally {
    cleanup();
  }
}
