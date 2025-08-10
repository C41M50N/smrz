
const BASE_URL = 'http://127.0.0.1:8000';

async function handleError(response: Response): Promise<never> {
  if ('error' in response) {
    console.error('Error details:', await response.json());
    throw new Error(`HTTP error! status: ${response.status}, details: ${JSON.stringify(await response.json())}`);
  }
  console.error('HTTP error:', response.statusText);
  throw new Error(`HTTP error! status: ${response.status}`);
}


export async function fetchCleanHTML(url: string): Promise<string> {
  const response = await fetch(`${BASE_URL}/clean-html?url=${encodeURIComponent(url)}`);
  if (!response.ok) {
    await handleError(response);
  }
  return await response.json() as string;
}


type FetchRawArticleMetadataResponse = {
  title: string;
  author: string | null;
  published_date: string | null;
  favicon: string | null;
  meta_image: string | null;
};

export async function fetchRawArticleMetadata(url: string): Promise<FetchRawArticleMetadataResponse> {
  const response = await fetch(`${BASE_URL}/article-metadata?url=${encodeURIComponent(url)}`);
  if (!response.ok) {
    await handleError(response);
  }
  return await response.json() as FetchRawArticleMetadataResponse;
}


type FetchYoutubeVideoMetadataResponse = {
  title: string;
  channel: string | null;
  published_date: string | null;
  thumbnail_url: string | null;
};

export async function fetchYoutubeMetadata(youtube_url: string): Promise<FetchYoutubeVideoMetadataResponse> {
  const response = await fetch(`${BASE_URL}/youtube-metadata?url=${encodeURIComponent(youtube_url)}`);
  if (!response.ok) {
    await handleError(response);
  }
  return await response.json() as FetchYoutubeVideoMetadataResponse;
}


type FetchYoutubeVideoTranscriptionResponse = {
  transcription: string;
};

export async function fetchYoutubeVideoTranscription(youtube_url: string): Promise<FetchYoutubeVideoTranscriptionResponse> {
  const response = await fetch(`${BASE_URL}/youtube-transcription?url=${encodeURIComponent(youtube_url)}`);
  if (!response.ok) {
    await handleError(response);
  }
  return await response.json() as FetchYoutubeVideoTranscriptionResponse;
}
