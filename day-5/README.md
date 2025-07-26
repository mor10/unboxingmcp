# Developing and Deploying a Remote MCP Server with GitHub Authentication Using Cloudflare Workers

This guide provides instructions for developing and deploying a Model Context Protocol (MCP) server with GitHub authentication on Cloudflare Workers. It covers setting up the server, testing it locally, and connecting it to various MCP clients like Claude and Cursor.

## Table of Contents

- [Incomplete List of More MCP Deployment Options](#incomplete-list-of-mcp-deployment-options)
- [Local Development and Testing](#local-development-and-testing)
  - [Step 1: Start with a template](#step-1-start-with-a-template)
  - [Step 2: Set up a GitHub OAuth App for Local Development](#step-2-set-up-a-github-oauth-app-for-local-development)
  - [Step 3: Test the Local Server](#step-3-test-the-local-server)
    - [Test the Local Server Using the MCP Inspector](#test-the-local-server-using-the-mcp-inspector)
    - [Test the Local Server Using VS Code](#test-the-local-server-using-vs-code)
    - [Test the Local Server Using Claude Desktop](#test-the-local-server-using-claude-desktop)
- [Deploying the MCP Server to Cloudflare Workers](#deploying-the-mcp-server-to-cloudflare-workers)
  - [Step 1: Set up a GitHub OAuth App for Production](#step-1-set-up-a-github-oauth-app-for-production)
  - [Step 2: Set up a KV namespace](#step-2-set-up-a-kv-namespace)
  - [Step 3: Deploy with Wrangler](#step-3-deploy-with-wrangler)
  - [Step 4: Test the Deployment with MCP Inspector](#step-4-test-the-deployment-with-mcp-inspector)
  - [Step 5: Access the MCP Server from MCP Clients](#step-5-access-the-mcp-server-from-mcp-clients)
- [Further Reading](#further-reading)

## Incomplete List of More MCP Deployment Options

- [Azure API Management](https://github.com/Azure-Samples/remote-mcp-apim-functions-python/tree/mcp-authspec-2025-06-18)
- [Cloudflare](https://developers.cloudflare.com/agents/guides/remote-mcp-server/)
- [Google Cloud](https://cloud.google.com/blog/topics/developers-practitioners/build-and-deploy-a-remote-mcp-server-to-google-cloud-run-in-under-10-minutes)
- [AWS](https://aws.amazon.com/solutions/guidance/deploying-model-context-protocol-servers-on-aws/)
- [Heroku](https://www.heroku.com/blog/building-mcp-servers-on-heroku/)

## Local Development and Testing

_These instructions are modified from the [Cloudflare guide](https://developers.cloudflare.com/agents/guides/remote-mcp-server/) to focus on how to build and deploy your own custom server._

### Step 1: Start with a template

The easiest way to get started is to use a template. This way you get the Cloudflare CLI, the Cloudflare Workers SDK, and the Model Context Protocol SDK all set up for you. The following command sets up a new TypeScript project with GitHub OAuth support built in:

```bash
npm create cloudflare@latest -- my-mcp-server --template=cloudflare/ai/demos/remote-mcp-github-oauth
```

Follow the instructions in terminal, and say "No" to deploying the project.

Install  the dependencies:
```bash
npm install
```

### Step 2: Set up a GitHub OAuth App for Local Development

> [!IMPORTANT]
> Set up separate GitHub OAuth Apps for production and development environments. This way you can test your server locally without affecting the production app. See the [GitHub OAuth documentation](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app) for more details.

1. Create a new [GitHub OAuth App](https://github.com/settings/applications/new)
2. Set "Application Name" to something you'll recognize like `Useful MCP Server (localhost)` to differentiate it from your production app
3. "Application description" is optional
4. Set "Homepage URL" to `http://localhost:8788`
5. Set "Authorization callback URL" to `http://localhost:8788/callback`
6. Leave "Enable Device Flow" unchecked
7. Activate "Register Application"

On the application page you'll see the `Client ID`. Copy it and follow the steps below:

1. Make a copy of `.dev.vars.example` and rename it to `.dev.vars`
2. In `.dev.vars`, set `GITHUB_CLIENT_ID` to the `Client ID` you copied
3. Activate the "Generate a new client secret" button to generate a secret
4. In `.dev.vars`, set `GITHUB_CLIENT_SECRET` to the secret you generated
5. Leave `COOKIE_ENCRYPTION_KEY` as is, or set it to a random string

### Step 3: Test the Local Server

#### Test the Local Server Using the MCP Inspector

Run the server locally:
```bash
npm start
```
This uses `wrangler dev` to start the server on `http://localhost:8788`.

Open a separate terminal and run the following command to start the MCP Inspector:
```bash
npx @modelcontextprotocol/inspector@latest
```
This will open the Inspector UI in your browser.

- UI set "Transport Type" to `SSE` 
- Set "Server ULR" to `http://localhost:8788/sse`
- Click "Connect"
- Use the functions in the main panel to access the MCP server tools, resources, prompts, and more.

#### Test the Local Server Using VS Code

1. Open the Command Palette Shift + CMD/CTRL + P
2. Select "MCP: Open User Configuration". This opens `mcp.json`
3. In `mcp.json`:

  ```json
  {
    "servers": {
      "weather-server": {
        "command": "npx",
        "args": [
          "mcp-remote",
          "http://localhost:8788/sse"
        ]
      }
    }
  }
  ```

Activating the MCP server in VS Code will trigger a browser window to open for authentication. Follow the prompts to log in with your GitHub account.

#### Test the Local Server Using Claude Desktop

1. Open `claude_desktop_config.js` in an editor:
 
  File location:
  - MacOS / Linux `~/Library/Application/Support/Claude/claude_desktop_config.json`
  - Windows `AppData\Claude\claude_desktop_config.json`

2. In `claude_desktop_config.js`

  ```json
  {
    "mcpServers": {
      "weather-server": {
        "command": "npx",
        "args": [
          "mcp-remote",
          "http://localhost:8788/sse"
        ]
      }
    }
   }
   ```

Activating the MCP server in Claude Desktop will trigger a browser window to open for authentication. Follow the prompts to log in with your GitHub account.

## Deploying the MCP Server to Cloudflare Workers

Once you've tested your server locally, you can deploy it to Cloudflare Workers. This will allow you to access it from anywhere and connect it to various MCP clients.

### Step 1: Set up a GitHub OAuth App for Production

1. Create a new [GitHub OAuth App](https://github.com/settings/applications/new)
2. Set "Application Name" to something you'll recognize like `Useful MCP Server (production)` to differentiate it from your development app
3. "Application description" is optional
4. Set "Homepage URL" to `https://<your-useful-mcp-name>.<your-cloudflare-subdomain>.workers.dev`
5. Set "Authorization callback URL" to `https://<your-useful-mcp-name>.<your-cloudflare-subdomain>.workers.dev/callback`
6. Get the `Client ID` and generate a `Client secret` 
- Set secrets via Wrangler
```bash
npx wrangler secret put GITHUB_CLIENT_ID
npx wrangler secret put GITHUB_CLIENT_SECRET
npx wrangler secret put COOKIE_ENCRYPTION_KEY # add any random string here e.g. openssl rand -hex 32
```
#### Step 2: Set up a KV namespace
- Create the KV namespace: 
```bash
npx wrangler kv namespace create "OAUTH_KV"
```
- Update the `wrangler.jsonc` file with the resulting KV ID:

```json
{
  "kvNamespaces": [
    {
      "binding": "OAUTH_KV",
      "id": "<YOUR_KV_NAMESPACE_ID>"
    }
  ]
}
```

#### Step 3: Deploy with Wrangler

Deploy the MCP server to your Cloudflare `workers.dev` domain:
```bash
npx wrangler deploy
```

#### Step 4: Test the Deployment with MCP Inspector

1. Open the MCP Inspector
2. Set the "Server URL" to `https://<your-useful-mcp-name>.<your-cloudflare-subdomain>.workers.dev/sse`
3. In the main area, start the OAuth flow and click through the "Simple OAuth" process, following the instructions.
4. Once authenticated, you should see the tools working in the Inspector UI.

#### Step 5: Access the MCP Server from MCP Clients
Config settings for VS Code, Claude Desktop, etc:

```json
"weather-server": {
  "command": "npx",
  "args": [
    "mcp-remote",
    "https://<your-useful-mcp-name>.<your-cloudflare-subdomain>.workers.dev/sse"
  ]
}
```

## Further Reading

See [README.md](weather-server-github-auth/README.md) for more details on how the MCP server works and how to customize it for your needs.
