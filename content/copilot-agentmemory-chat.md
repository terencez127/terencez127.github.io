Title: Use GitHub Copilot as Agentmemory’s chat provider
Date: 2026-11-18 12:59
Slug: copilot-agentmemory-chat
Category: Tutorials
Tags: Agentmemory, GitHub Copilot

Agentmemory speaks the OpenAI chat completions API. A loopback-only wrapper translates its requests into GitHub Copilot calls through the Copilot SDK and CLI. The wrapper runs on your machine; GitHub handles the prompts.

This tutorial uses Agentmemory 0.9.33 and `ghcp-sdk-oai-wrapper` v0.4.2. On macOS, I verified that Agentmemory could compress an observation, persist it, and read back a session summary on the Copilot route. The steps below are a source-based recipe, not a freshly tested installation on every platform.

## 1. Prepare an isolated test account

Use a fresh OS login with no connected agents, a POSIX-style shell, Git, Go 1.25.12 or newer, Node.js 20+, `curl`, `jq`, and `lsof`. Install the [Copilot CLI](https://github.com/github/copilot-cli) and authorize it for your Copilot account. Follow the [Agentmemory 0.9.33 installation instructions](https://www.npmjs.com/package/@agentmemory/agentmemory/v/0.9.33), including its native runtime prerequisites.

Why a separate login? Agentmemory 0.9.33 writes first-run preferences and `.env` under `~/.agentmemory` even if you pass a new `--data-dir`. Use the test account’s normal home, leave `AGENTMEMORY_ENV_FILE` unset, and start without inherited provider or endpoint overrides. Don’t point the tutorial at an existing store.

The examples use **8080** for the wrapper and **8081** for Agentmemory, not as requirements. Check both with `lsof -nP -iTCP:8080 -sTCP:LISTEN` and the same command for 8081. If either is occupied, pick another free port and substitute it wherever that service appears. The worker must share the host’s loopback network: inside a network-isolated container, `127.0.0.1` refers to the container, not the host. Don’t solve that mismatch by exposing the wrapper on all interfaces.

## 2. Build the wrapper with a loopback listener

The stock wrapper at this revision listens on `":" + cfg.Port`. That selects a port **on all interfaces**. Patch the address before you start it. From a new working directory:

```sh
git clone https://github.com/olohmann/ghcp-sdk-oai-wrapper.git
cd ghcp-sdk-oai-wrapper
git checkout --detach 16279dc08365a179a37884394b61738cb22bf975
```

In [`cmd/server/main.go`](https://github.com/olohmann/ghcp-sdk-oai-wrapper/blob/16279dc08365a179a37884394b61738cb22bf975/cmd/server/main.go), change just this field:

```diff
-		Addr:         ":" + cfg.Port,
+		Addr:         "127.0.0.1:" + cfg.Port,
```

Inspect `git diff`. If the listener address is the only change, build the binary from the repository root:

```sh
go build -ldflags '-X main.version=0.4.2' -o ./ghcp-sdk-oai-wrapper ./cmd/server
```

## 3. Start the wrapper with two different credentials

| Credential | Who needs it | What it authorizes |
| --- | --- | --- |
| Local bearer | Wrapper `API_KEY` and Agentmemory `OPENAI_API_KEY` | Agentmemory calling the wrapper. Generate a random secret with your password manager. An empty `API_KEY` disables authentication. |
| Copilot credential | Wrapper `GITHUB_TOKEN` only | The wrapper calling Copilot on your behalf. Use a credential approved for your account. Never put it in Agentmemory’s `.env`. |

Create `$HOME/.config/copilot-wrapper/proxy.env` **outside the checkout**, in an owner-only directory (`0700`), with file mode `0600`. Set `umask 077` before creating private files. In a private editor, replace the two markers below. Don’t enter credentials in shell commands or commit the file. The startup command sources this file as shell code, so quote values and source only a file you wrote and inspected.

```sh
PORT=8080
MODE=openai
LOG_LEVEL=warn
API_KEY='REPLACE_WITH_RANDOM_LOCAL_BEARER'
GITHUB_TOKEN='REPLACE_WITH_YOUR_COPILOT_CREDENTIAL'
```

From the wrapper checkout, start it in the foreground. This discovers your CLI on `PATH` rather than assuming an installation directory:

```sh
(
  set +x
  set -eu
  umask 077
  unset API_KEY GITHUB_TOKEN
  set -a
  . "$HOME/.config/copilot-wrapper/proxy.env"
  set +a
  : "${API_KEY:?missing local bearer}" "${GITHUB_TOKEN:?missing Copilot credential}"
  case "$API_KEY:$GITHUB_TOKEN" in *REPLACE_WITH_*) exit 1 ;; esac
  COPILOT_CLI_PATH=$(command -v copilot)
  test -x "$COPILOT_CLI_PATH"
  export COPILOT_CLI_PATH
  exec ./ghcp-sdk-oai-wrapper
)
```

In a second terminal, set the **nonsecret** port to the value you chose. First establish who owns the listener, *before* sending it a bearer:

```sh
WRAPPER_PORT=8080
WRAPPER_URL="http://127.0.0.1:$WRAPPER_PORT"
lsof -nP -iTCP:"$WRAPPER_PORT" -sTCP:LISTEN
for path in /healthz /v1/models; do
  curl -q --noproxy '*' -sS --max-time 10 -o /dev/null \
    -w "$path: %{http_code}\n" "$WRAPPER_URL$path"
done
```

Expect your wrapper listening only on `127.0.0.1`, **200** from `/healthz`, and **401** from `/v1/models` without credentials. If these differ, stop here. Now list the chat models your account can use. This sends the local header through standard input rather than putting the bearer in curl’s arguments:

```sh
(
  set +x
  set +a
  set -eu
  unset API_KEY GITHUB_TOKEN
  . "$HOME/.config/copilot-wrapper/proxy.env"
  unset GITHUB_TOKEN
  printf 'Authorization: Bearer %s\n' "${API_KEY:?missing local bearer}" |
    curl -q --noproxy '*' -fsS --max-time 30 --header @- "$WRAPPER_URL/v1/models"
) | jq -r '.data[].id'
```

Choose one returned ID for `OPENAI_MODEL`. If the list is empty or the request fails, don’t guess a model name. Check the local bearer first, then the wrapper’s Copilot credential, entitlement, and CLI path.

## 4. Point Agentmemory at the chat endpoint

Create `~/.agentmemory/.env` privately in the fresh account (directory `0700`, file `0600`). Replace every marker with a **literal** value; don’t assume the dotenv reader expands shell variables. The wrapper base URL ends in `/v1`, not in a specific operation such as `/chat/completions`.

```dotenv
AGENTMEMORY_LLM_PROVIDER=openai
OPENAI_BASE_URL=http://127.0.0.1:8080/v1
OPENAI_MODEL=REPLACE_WITH_ID_FROM_MODEL_LIST
OPENAI_API_KEY=REPLACE_WITH_SAME_LOCAL_BEARER_AS_WRAPPER
```

Here `openai` names an API format, not a destination. Leave `OPENAI_REASONING_EFFORT` unset; the pinned wrapper doesn’t forward it.

Start Agentmemory against a fresh directory. In the second terminal, keep these variables for shutdown:

```sh
umask 077
AM_DATA_DIR=$(mktemp -d "$HOME/agentmemory-test.XXXXXXXX")
AM_PORT=8081
agentmemory --data-dir "${AM_DATA_DIR:?missing test directory}" --port "$AM_PORT"
```

**During onboarding**, deselect all agents, explicitly choose **OpenAI**, leave automatic context injection off, and decline connections. In 0.9.33, **Skip** removes the provider selection; it doesn’t keep the value you prepared.

Before submitting a prompt, confirm the running worker uses your provider, chat URL, and model ID. On the native Compose path, inspect those three fields in `compose/worker-compose.yaml` under the test data directory and in its referenced `.agentmemory-filtered.env`. Match the config to the running worker; explicit `environment` entries take precedence. Check the bearer privately. Don’t dump entire environments into a terminal log or support ticket. A healthy wrapper is no use if the worker is calling a different endpoint.

## 5. Verify a stored fact, not just an HTTP response

In one labeled test session, submit an invented observation: **“Violet leases expire after 37 seconds. A lease belongs to exactly one tenant.”** Allow native compression to finish, or trigger it once. Read the stored observation. It should be marked complete and retain both the expiry and the tenant rule. Then request a session summary and retrieve the saved summary separately. If all you have is a plausible chat response, you haven’t verified persistence.

When finished, stop only this instance:

```sh
agentmemory stop --data-dir "${AM_DATA_DIR:?missing test directory}" --port "${AM_PORT:?missing test port}"
```

Stop the foreground wrapper with Ctrl-C and confirm its listener has closed. For a permanent install, configure your own user-service manager and verify the restarted worker’s effective route before connecting real agents.

**Privacy boundary:** Loopback restricts incoming connections; it does not make chat inference local or disable Copilot tools. The SDK or CLI may retain session state after shutdown. Keep credentials, logs, and state out of repositories and blog attachments. Don’t forward the wrapper port, and use only data you’re permitted to send to GitHub.

Sources: [pinned wrapper source and MIT license](https://github.com/olohmann/ghcp-sdk-oai-wrapper/tree/16279dc08365a179a37884394b61738cb22bf975) by Oliver Lohmann · [GitHub Copilot SDK](https://github.com/github/copilot-sdk) · [Agentmemory](https://github.com/rohitg00/agentmemory).
