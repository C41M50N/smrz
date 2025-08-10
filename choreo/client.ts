import { createRouterClient } from "@orpc/server";
import { router } from "./src/routers";

const client = createRouterClient(router, { context: { request: new Request("http://localhost:8080/rpc/huh") } });

const result = await client.test.testProcedure1()
console.log(result); // Should log "Hello, World!"

const resultWithInput = await client.test.testProcedure2({ name: "Alice" })
console.log(resultWithInput); // Should log "Hello, Alice!"

const youtubeResult = await client.content.ingestURL({ url: "https://www.youtube.com/watch?v=VdrEq0cODu4" })
console.log(youtubeResult);
