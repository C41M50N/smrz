import { OpenAPIHandler } from '@orpc/openapi/fetch'
import { CORSPlugin } from '@orpc/server/plugins'
import { router } from './routers'

const handler = new OpenAPIHandler(router, {
  plugins: [
    new CORSPlugin()
  ]
})

const server = Bun.serve({
  port: 8080,
  async fetch(request: Request) {
    const { matched, response } = await handler.handle(request, {
      prefix: '/rpc',
      context: {
        request
      } // Provide initial context if needed
    })

    if (matched) {
      return response
    }

    return new Response('Not found', { status: 404 })
  }
})

console.log(`🚀 Server started at http://127.0.0.1:${server.port}`);
