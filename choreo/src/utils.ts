//////////////////////////////////////////////////////////////////////////////
///////////////////////////////// YOUTUBE ///////////////////////////////////
//////////////////////////////////////////////////////////////////////////////

// Regular expression patterns to match various YouTube URL formats and capture the video ID.
// The video ID is typically 11 characters long and can contain letters (upper and lower case),
// numbers, underscores, and hyphens.
const VALID_YOUTUBE_URL_PATTERNS: string[] = [
    "(?:https?:\\/\\/)?(?:www\\.)?youtube\\.com\\/watch\\?v=([a-zA-Z0-9_-]{11})",  // Standard format
    "(?:https?:\\/\\/)?youtu\\.be\\/([a-zA-Z0-9_-]{11})",  // Shortened format
    "(?:https?:\\/\\/)?(?:www\\.)?youtube\\.com\\/embed\\/([a-zA-Z0-9_-]{11})",  // Embed format
    "(?:https?:\\/\\/)?(?:www\\.)?youtube\\.com\\/v\\/([a-zA-Z0-9_-]{11})",  // Older embed format
    "(?:https?:\\/\\/)?(?:www\\.)?youtube\\.com\\/shorts\\/([a-zA-Z0-9_-]{11})",  // Shorts format
    "(?:https?:\\/\\/)?(?:www\\.)?youtube\\.com\\/live\\/([a-zA-Z0-9_-]{11})",  // Live format
];

/**
 * Check if the given URL is a valid YouTube video URL.
 */
export function isYoutubeURL(url: string): boolean {
    return VALID_YOUTUBE_URL_PATTERNS.some(pattern => new RegExp(pattern).test(url));
}

/**
 * Extracts the YouTube video ID from a given YouTube video URL.
 */
export function parseYoutubeVideoId(url: string): string {
    for (const pattern of VALID_YOUTUBE_URL_PATTERNS) {
        const match = url.match(new RegExp(pattern));
        if (match) {
            // The video ID is in the first capturing group
            const videoId = match[1];
            // Further validation: ensure the extracted ID is exactly 11 characters
            // and contains only valid characters. This is mostly handled by the regex
            // but an explicit check can be an extra safeguard.
            if (videoId && videoId.length === 11 && /^[a-zA-Z0-9_-]+$/.test(videoId)) {
                return videoId;
            }
        }
    }

    // If no pattern matched or the extracted ID was not valid
    throw new Error("Invalid YouTube video URL or unable to extract video ID.");
}

/**
 * Normalize a YouTube URL to a standard format.
 * This function will convert any valid YouTube URL to the standard watch format.
 */
export function normalizeYoutubeURL(url: string): string {
    const videoId = parseYoutubeVideoId(url);
    return `https://www.youtube.com/watch?v=${videoId}`;
}

/**
 * Normalize a URL by removing query parameters and fragments, removing trailing slashes,
 * and following redirects to get the final URL.
 */
export async function normalizeURL(url: string): Promise<string> {
    try {
        // Follow redirects to get the final URL
        const response = await fetch(url, { 
            method: 'HEAD',
            redirect: 'follow'
        });
        
        // Use the final redirected URL
        const finalUrl = response.url;
        
        // Parse and normalize the URL
        const { protocol, host, pathname } = new URL(finalUrl);
        return `${protocol}//${host}${pathname.replace(/\/+$/, "")}`;
    } catch (error) {
        // If fetch fails, normalize the original URL without following redirects
        const { protocol, host, pathname } = new URL(url);
        return `${protocol}//${host}${pathname.replace(/\/+$/, "")}`;
    }
}
