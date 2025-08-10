import { mkdirSync, writeFileSync } from "node:fs";
import { cwd } from "node:process";
import { onError, os } from "@orpc/server";
import slugify from "slugify";
import z from "zod";
import { fetchCleanHTML, fetchRawArticleMetadata, fetchYoutubeMetadata, fetchYoutubeVideoTranscription } from "../clients/orion";
import { ARTICLE_TO_MARKDOWN_PROMPT_1, IMPROVE_TRANSCRIPT_PROMPT_1, LLMClient, SUMMARIZE_PROMPT_1 } from "../lib/llm-client";
import type { ArticleMetadata, YoutubeVideoMetadata } from "../lib/types";
import { isYoutubeURL, normalizeURL, normalizeYoutubeURL } from "../utils";

export const contentRouter = {
  ingestURL: os
    .$context<{ request: Request }>()
    .route({
      method: "POST",
      path: "/ingest-url",
      description: "Ingest a URL and process its content",
    })
    .input(z.object({ url: z.url() }))
    .use(onError((error) => {
      console.error('Error handling request:', JSON.stringify(error));
    }))
    .use(async ({ next, context }) => {
      const start = performance.now();
      const res = await next();
      const end = performance.now();
      console.log(`💥 ${new Date().toISOString()} - ${context.request.method} ${new URL(context.request.url).pathname} took ${((end - start) / 1000).toFixed(4)}s`);
      return res;
    })
    .handler(async ({ input }) => {
      let id: string;
      let finalMetadata: ArticleMetadata | YoutubeVideoMetadata;
      let finalContent: string;
      let finalSummary: string;

      if (isYoutubeURL(input.url)) {
        const youtubeURL = normalizeYoutubeURL(input.url);
        const videoTranscriptionPromise = fetchYoutubeVideoTranscription(youtubeURL);
        const videoMetadataPromise = fetchYoutubeMetadata(youtubeURL);
        const [transcriptionResponse, metadata] = await Promise.all([videoTranscriptionPromise, videoMetadataPromise]);

        const improveTranscriptReadabilityLLMClient = new LLMClient({
          model: "gemini-2.5-flash-lite-preview-06-17",
          system_prompt: IMPROVE_TRANSCRIPT_PROMPT_1,
          log_key: "transcript-readability",
        });

        const summaryLLMClient = new LLMClient({
          model: "gemini-2.5-flash-lite-preview-06-17",
          system_prompt: SUMMARIZE_PROMPT_1,
          log_key: "transcript-summary",
        });

        const improveTranscriptPromise = improveTranscriptReadabilityLLMClient.generateTextResponse(
          `Improve the readability of the following video transcript: ${transcriptionResponse.transcription}`,
          0.825
        );

        const summaryPromise = summaryLLMClient.generateTextResponse(
          `Summarize the following content: ${transcriptionResponse.transcription}`,
          0.585
        );

        const [improvedTranscript, summary] = await Promise.all([improveTranscriptPromise, summaryPromise]);

        // ####################################################################

        const slugTitle = slugify(metadata.title, { lower: true, strict: true });
        const BASE_PATH = `${cwd()}/output/${new Date().toISOString()}_${slugTitle}`;
        mkdirSync(BASE_PATH, { recursive: true });
        writeFileSync(`${BASE_PATH}/${slugTitle}_summary.md`, summary);
        writeFileSync(`${BASE_PATH}/${slugTitle}.md`, improvedTranscript);

        // ####################################################################

        id = youtubeURL;
        finalMetadata = metadata;
        finalContent = improvedTranscript;
        finalSummary = summary;
        
      } else {
        const normalizedURL = await normalizeURL(input.url);

        const cleanHTML = await fetchCleanHTML(input.url);

        const articleToMarkdownLLMClient = new LLMClient({
          model: "gpt-5-mini-2025-08-07",
          system_prompt: ARTICLE_TO_MARKDOWN_PROMPT_1,
          log_key: "article-to-markdown",
        });
        
        const articleToMarkdownPromise = articleToMarkdownLLMClient.generateTextResponse(
          `Convert the following article to markdown: ${cleanHTML}`,
        );

        const rawArticleMetadataPromise = fetchRawArticleMetadata(normalizedURL);

        const extractArticleMetadataLLMClient = new LLMClient({
          model: "gpt-4.1-nano-2025-04-14",
          system_prompt: "You are an expert at extracting metadata from articles.",
          log_key: "article-metadata-extraction",
        });

        const extractArticleMetadataPromise = extractArticleMetadataLLMClient.generateStructuredResponse(
          z.object({
            title: z.string(),
            author: z.string().nullable(),
            published_date: z.string().nullable(),
            favicon: z.string().nullable(),
            meta_image: z.string().nullable(),
          }),
          `Extract metadata from the following article: ${cleanHTML}`,
        );

        const [articleMarkdown, rawArticleMetadata, extractArticleMetadata] = await Promise.all([
          articleToMarkdownPromise,
          rawArticleMetadataPromise,
          extractArticleMetadataPromise,
        ]);

        // consolidate metadata (use LLM assisted metadata values for missing fields) (rawArticleMetadata as the base)
        const metadata = {
          title: rawArticleMetadata.title ?? extractArticleMetadata.title,
          author: rawArticleMetadata.author ?? extractArticleMetadata.author,
          published_date: rawArticleMetadata.published_date ?? extractArticleMetadata.published_date,
          favicon: rawArticleMetadata.favicon ?? extractArticleMetadata.favicon,
          meta_image: rawArticleMetadata.meta_image ?? extractArticleMetadata.meta_image,
        };

        const summaryLLMClient = new LLMClient({
          model: "gemini-2.5-flash-lite-preview-06-17",
          system_prompt: SUMMARIZE_PROMPT_1,
          log_key: "article-summary",
        });

        const summary = await summaryLLMClient.generateTextResponse(
          `Summarize the following content: ${articleMarkdown}`,
          0.585
        );

        // ####################################################################

        const slugTitle = slugify(metadata.title, { lower: true, strict: true });
        const BASE_PATH = `${cwd()}/output/${new Date().toISOString()}_${slugTitle}`;
        mkdirSync(BASE_PATH, { recursive: true });
        writeFileSync(`${BASE_PATH}/${slugTitle}_clean.html`, cleanHTML);
        writeFileSync(`${BASE_PATH}/${slugTitle}_summary.md`, summary);
        writeFileSync(`${BASE_PATH}/${slugTitle}.md`, articleMarkdown);

        // ####################################################################

        id = normalizedURL;
        finalMetadata = metadata;
        finalContent = articleMarkdown;
        finalSummary = summary;
      }

      return {
        id,
        metadata: finalMetadata,
        content: finalContent,
        summary: finalSummary,
      };
    }),
};
