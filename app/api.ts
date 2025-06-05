
type ErrorResponse = { error: string };

type SummaryResponse = {
  title: string;
  content: string;
  summary: string;
}

export async function fetchSummary(url: string): Promise<SummaryResponse> {
  const res = await fetch(`http://127.0.0.1:8000/smrz?url=${encodeURIComponent(url)}`);
  if (!res.ok) {
    const errorResponse = await res.json() as ErrorResponse;
    throw new Error(`Error: ${errorResponse.error}`);
  }
  return res.json() as Promise<SummaryResponse>;
}
