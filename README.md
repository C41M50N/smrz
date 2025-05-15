# smrz
smrz is an API for summarizing content from URLs. It provides a simple API to fetch and summarize text from web pages.
It is designed to be easy to use and integrate into other applications.

## API Reference

### `GET /`
- **Description**: Returns a simple greeting message.
- **Response**: `"Hello, World!"`

### `GET /summarize`
- **Description**: Summarizes the content from the given URL.
- **Query Parameters**:
  - `url` (string, required): The URL of the content to summarize. Must start with `http://` or `https://`.
- **Response**:
  - On success: A JSON object containing the summary.
    ```json
    {
      "summary": "..."
    }
    ```
  - On error: A JSON object containing an error message.
    ```json
    {
      "error": "..."
    }
    ```

### `GET /summarize/stream`
- **Description**: Streams the summary of the content from the given URL.
- **Query Parameters**:
  - `url` (string, required): The URL of the content to summarize. Must start with `http://` or `https://`.
- **Response**:
  - On success: A stream of JSON objects containing the summary.
    ```json
    {
      "summary": "..."
    }
    ```
  - On error: A JSON object containing an error message.
    ```json
    {
      "error": "..."
    }
    ```