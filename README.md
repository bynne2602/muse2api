# Muse2API Community

[English](README.md) | [Tiếng Việt](README.vi.md)

Self-hosted, OpenAI-compatible API bridge for the Muse web app. This community fork keeps the upstream license and credits while focusing on a straightforward self-hosted setup.

> This project is an unofficial third-party integration. It is not affiliated with or endorsed by Muse. Use it only with accounts and access you are authorized to use, and follow the service's terms.

## Quick start with Docker

1. Install Docker Engine and the Docker Compose plugin.
2. Clone this repository and enter its directory:

   ```sh
   git clone https://github.com/bynne2602/muse2api.git
   cd muse2api
   ```

3. Create your local configuration and set a unique API key:

   ```sh
   cp .env.example .env
   ```

   Edit `.env` and set `MUSE2API_KEY` to a long, random secret. Do not share it or commit `.env`.

4. Start the service:

   ```sh
   docker compose up -d --build
   ```

5. Open `http://localhost:18610/admin?key=YOUR_KEY`, sign in to Muse in the browser flow, and add your own account. Keep this service private or put it behind HTTPS and a trusted access control layer before exposing it to the internet.

Generated files and account data are stored in `./data`. Back up that directory securely. Never publish account cookies, API keys, browser profiles, or generated private media.

## Run with Python

Requires Python 3.10+, Chromium/Chrome, and the system libraries needed by Chromium.

```sh
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env`, set a unique `MUSE2API_KEY`, then run:

```sh
python -m uvicorn app:app --host 127.0.0.1 --port 18610
```

## API examples

Send `Authorization: Bearer YOUR_KEY` with protected API requests.

```sh
curl http://localhost:18610/v1/models \
  -H "Authorization: Bearer YOUR_KEY"
```

Chat example:

```sh
curl http://localhost:18610/v1/chat/completions \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"muse-spark","messages":[{"role":"user","content":"Hello"}]}'
```

Image generation is available at `/v1/images/generations` and video generation at `/v1/videos`. Video requests return a task ID; poll `/v1/videos/{task_id}` for completion. Generated files are served from `/v1/media/{filename}`.

## Configuration

| Variable | Default | Description |
| --- | --- | --- |
| `MUSE2API_KEY` | Generated on first start | Admin and API key. Set a unique value before exposing the service. |
| `MUSE2API_HOST` | `0.0.0.0` | Bind address inside the service/container. |
| `MUSE2API_PORT` | `18610` | HTTP port. |
| `MUSE2API_PUBLIC_BASE` | Empty | Public base URL shown to clients. |
| `MUSE2API_CHROMIUM` | Auto-detected | Chromium/Chrome executable path. |
| `MUSE2API_CDP_PORT` | `19210` | Internal browser debugging port. Do not expose publicly. |
| `MUSE2API_IMAGE_TIMEOUT` | `240` | Image generation timeout in seconds. |
| `MUSE2API_VIDEO_TIMEOUT` | `600` | Video generation timeout in seconds. |
| `MUSE2API_CHAT_TIMEOUT` | `300` | Chat timeout in seconds. |
| `MUSE2API_UPDATER_ENABLED` | `0` | Enables the upstream online updater when set to `1`. Leave disabled for a fork unless you have configured and reviewed its repository target. |
| `MUSE2API_ALLOW_WEB_PUSH` | `0` | Enables repository publishing from the admin panel when set to `1`. Keep disabled for normal deployments. |

## Development

Install dependencies, then run the local checks:

```sh
python -m pip install -r requirements.txt
python tests/test_admin_base_url.py
python tests/test_async_images.py
python tests/test_media_delete.py
python tests/test_media_selection.py
python tests/test_session_health.py
python tests/test_vm_wait.py engine.py --assert
```

These checks do not verify live Muse account access or real generation. Do not use real credentials in test fixtures.

## License and attribution

This project is distributed under the [MIT License](LICENSE). It is derived from [czg86389-hub/muse2api](https://github.com/czg86389-hub/muse2api); preserve the upstream license and attribution when redistributing. See the Git history and upstream repository for contributor credits.

Contributions are welcome. Open an issue or pull request in your fork repository.
