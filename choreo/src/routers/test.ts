import { os } from "@orpc/server";
import z from "zod";

export const testRouter = {
  testProcedure1: os
    .handler(async () => {
      return `Hello, World!`;
    }),
  testProcedure2: os
    .input(z.object({
      name: z.string(),
    }))
    .handler(async ({ input }) => {
      return `Hello, ${input.name}!`;
    }),
};
