
type ErrorResponse = { error: string };

type SummaryResponse = {
  summary: string;
}

export async function fetchSummary(url: string): Promise<SummaryResponse> {
  const res = await fetch(`http://127.0.0.1:8000/summarize?url=${encodeURIComponent(url)}`);
  if (!res.ok) {
    const errorResponse = await res.json() as ErrorResponse;
    throw new Error(`Error: ${errorResponse.error}`);
  }
  return res.json() as Promise<SummaryResponse>;
}
