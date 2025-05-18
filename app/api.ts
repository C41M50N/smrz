
type ErrorResponse = { error: string };

type SummaryResponse = {
  summary: string;
} | ErrorResponse;

export async function fetchSummary(url: string): Promise<SummaryResponse> {
  const res = await fetch(`http://127.0.0.1:8000/summarize?url=${encodeURIComponent(url)}`);
  return res.json() as Promise<SummaryResponse>;
}
