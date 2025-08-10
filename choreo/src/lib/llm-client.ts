import { createGoogleGenerativeAI } from "@ai-sdk/google";
import { createOpenAI } from "@ai-sdk/openai";
import { createOpenRouter, type OpenRouterLanguageModel } from "@openrouter/ai-sdk-provider";
import { generateObject, generateText, zodSchema, type LanguageModel } from "ai";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import type { z, ZodType } from "zod";

type Provider = "Google" | "OpenAI" | "OpenRouter";

type ModelDetails = {
  name: string;
  provider: Provider;
  cost_per_1M_input_tokens: number; // in USD
  cost_per_1M_output_tokens: number; // in USD
  reasoning?: boolean;
};

const MODEL_REGISTRY = {
  // Google Gemini models
  "gemini-2.5-flash-lite-preview-06-17": {
    name: "Gemini 2.5 Flash Lite Preview",
    provider: "Google",
    cost_per_1M_input_tokens: 5, // 0.05 USD
    cost_per_1M_output_tokens: 20, // 0.20 USD
  },
  // OpenAI models
  "gpt-5-mini-2025-08-07": {
    name: "GPT-5 Mini",
    provider: "OpenAI",
    cost_per_1M_input_tokens: 25, // 0.25 USD
    cost_per_1M_output_tokens: 200, // 2.00 USD
    reasoning: true,
  },
  "gpt-5-nano-2025-08-07": {
    name: "GPT-5 Nano",
    provider: "OpenAI",
    cost_per_1M_input_tokens: 5, // 0.05 USD
    cost_per_1M_output_tokens: 40, // 0.40 USD
    reasoning: true,
  },
  "gpt-4.1-mini-2025-04-14": {
    name: "GPT-4.1 Mini",
    provider: "OpenAI",
    cost_per_1M_input_tokens: 15, // 0.15 USD
    cost_per_1M_output_tokens: 60, // 0.60 USD
  },
  "gpt-4.1-nano-2025-04-14": {
    name: "GPT-4.1 Nano",
    provider: "OpenAI",
    cost_per_1M_input_tokens: 10, // 0.10 USD
    cost_per_1M_output_tokens: 40, // 0.40 USD
  },
  // OpenRouter models
  "openai/gpt-4.1-mini": {
    name: "GPT-4.1 Mini",
    provider: "OpenRouter",
    cost_per_1M_input_tokens: 40, // 0.40 USD
    cost_per_1M_output_tokens: 160, // 1.60 USD
  },
  "openai/gpt-4.1-nano": {
    name: "GPT-4.1 Nano",
    provider: "OpenRouter",
    cost_per_1M_input_tokens: 10, // 0.10 USD
    cost_per_1M_output_tokens: 40, // 0.40 USD
  },
} satisfies Record<string, ModelDetails>;

export type Model = keyof typeof MODEL_REGISTRY;

type ReasoningEffort = "low" | "medium" | "high";

// ############################################################################

const google = createGoogleGenerativeAI({ apiKey: process.env.GEMINI_API_KEY });
const openai = createOpenAI({ apiKey: process.env.OPENAI_API_KEY });
const openrouter = createOpenRouter({ apiKey: process.env.OPENROUTER_API_KEY });

// ############################################################################

type CreateLLMClientParams = {
  model: Model;
  system_prompt: string;
  log_key?: string; // Optional key to identify logs from this client
};

export class LLMClient {
  private model: Model;
  private system_prompt: string;
  private log_key?: string;
  private model_client: LanguageModel | OpenRouterLanguageModel;
  constructor(params: CreateLLMClientParams) {
    this.model = params.model;
    this.system_prompt = params.system_prompt;
    this.log_key = params.log_key;
    this.model_client = this._getModelClient();
  }

  async generateTextResponse(user_prompt: string, temp: number = 0.7, reasoning_effort: ReasoningEffort = "low"): Promise<string> {
    const modelDetails = this._getModelDetails();

    
    let generateTextOptions: Partial<Parameters<typeof generateText>[0]>;
    if (modelDetails.reasoning) {
      generateTextOptions = {
        model: this.model_client as LanguageModel,
        system: this.system_prompt,
        prompt: user_prompt,
        providerOptions: {
          openai: {
            reasoningEffort: reasoning_effort
          }
        }
      };
    } else {
      generateTextOptions = {
        model: this.model_client as LanguageModel,
        system: this.system_prompt,
        prompt: user_prompt,
        temperature: temp,
      };
    }
    
    const start_time = performance.now();
    const { text, usage } = await generateText({ model: this.model_client as LanguageModel, ...generateTextOptions });
    const response_time = performance.now() - start_time;

    // biome-ignore lint/style/noNonNullAssertion: Assuming usage is always defined
    const cost = ((usage.inputTokens! / 1_000_000) * modelDetails.cost_per_1M_input_tokens) + ((usage.outputTokens! / 1_000_000) * modelDetails.cost_per_1M_output_tokens);

    if (this.log_key) {
      console.log(`[LLMClient] [${this.log_key}]: Took ${(response_time / 1000).toFixed(2)}s to generate response with ${modelDetails.name} (${modelDetails.provider}) - ${usage.inputTokens} input tokens, ${usage.outputTokens} output tokens costing ~${(cost / 100).toFixed(4)} USD`);
    }

    return text;
  }

  async generateStructuredResponse<T extends z.ZodType>(schema: T, user_prompt: string, temp: number = 0.7, reasoning_effort: ReasoningEffort = "low"): Promise<z.infer<T>> {
    const modelDetails = this._getModelDetails();

    let generateTextOptions: Partial<Parameters<typeof generateObject>[0]>;
    if (modelDetails.reasoning) {
      generateTextOptions = {
        model: this.model_client as LanguageModel,
        system: this.system_prompt,
        prompt: user_prompt,
        schema: zodSchema(schema),
        providerOptions: {
          openai: {
            reasoningEffort: reasoning_effort
          }
        }
      };
    } else {
      generateTextOptions = {
        model: this.model_client as LanguageModel,
        system: this.system_prompt,
        prompt: user_prompt,
        temperature: temp,
        schema: zodSchema(schema),
      };
    }

    const start_time = performance.now();
    const { object, usage } = await generateObject({ model: this.model_client as LanguageModel, ...generateTextOptions });
    const response_time = performance.now() - start_time;

    // biome-ignore lint/style/noNonNullAssertion: Assuming usage is always defined
    const cost = ((usage.inputTokens! / 1_000_000) * modelDetails.cost_per_1M_input_tokens) + ((usage.outputTokens! / 1_000_000) * modelDetails.cost_per_1M_output_tokens);

    if (this.log_key) {
      console.log(`[LLMClient] [${this.log_key}]: Took ${(response_time / 1000).toFixed(2)}s to generate structured response with ${modelDetails.name} (${modelDetails.provider}) - ${usage.inputTokens} input tokens, ${usage.outputTokens} output tokens costing ~${(cost / 100).toFixed(4)} USD`);
    }

    return object as z.infer<typeof schema>;
  }

  _getModelDetails(): ModelDetails {
    const modelDetails = MODEL_REGISTRY[this.model];
    if (!modelDetails) {
      throw new Error(`Model not found: ${this.model}`);
    }
    return modelDetails;
  }

  _getModelClient(): LanguageModel | OpenRouterLanguageModel {
    const modelDetails = this._getModelDetails();
    if (modelDetails.provider === "Google") {
      return google(this.model);
    } else if (modelDetails.provider === "OpenAI") {
      return openai(this.model);
    } else if (modelDetails.provider === "OpenRouter") {
      return openrouter(this.model);
    } else {
      throw new Error(`Unsupported provider: ${modelDetails.provider}`);
    }
  }
}

// ############################################################################

// TODO: add a tl;dr section to the prompt

export const SUMMARIZE_PROMPT_1 = readFileSync(join(__dirname, "../../prompts/summarize-1.md"), "utf-8");
export const IMPROVE_TRANSCRIPT_PROMPT_1 = readFileSync(join(__dirname, "../../prompts/improve-transcript-1.md"), "utf-8");
export const ARTICLE_TO_MARKDOWN_PROMPT_1 = readFileSync(join(__dirname, "../../prompts/article-to-markdown-1.md"), "utf-8");
