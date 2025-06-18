from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app import __version__
from app.api.routes import router as api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for the FastAPI application.
    This is used to perform startup and shutdown tasks.
    """
    print(f"✅ Starting upto the FastAPI application")
    yield
    print(f"❎ Shutting down the FastAPI application")
    
app = FastAPI(
    title="tds-virtual-ta",
    version=__version__,
    description="Virtual Teaching Assistant (Virtual TA) is an innovative, intelligent and automated assistant designed specifically for the Tools in Data Science (TDS) course offered by the IIT Madras Online Degree Program. This cutting-edge system revolutionizes the learning experience by providing students with accurate, context-aware answers to their questions.",
    openapi_tags=[
        {
            "name": "API",
            "description": "Endpoints for interacting with the Virtual TA API.",
        },
    ],
    lifespan=lifespan
)
app.router.redirect_slashes = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def strip_trailing_slash(request: Request, call_next):
    scope = request.scope
    path = scope["path"]
    if path != "/" and path.endswith("/"):
        scope["path"] = path[:-1]
    return await call_next(request)

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def get_application_root_ui():
    html_content = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>tds-virtual-ta</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link
      href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
      rel="stylesheet"
    />
    <style>
      body {
        font-family: "Inter", sans-serif;
        background: #ffffff;
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
        margin: 0;
        color: #e2e8f0;
      }
      .glass-container {
        background: #1f1e1e;
        border-radius: 20px;
        box-shadow: 0 16px 32px 0 rgba(0, 0, 0, 0.3);
        padding: 30px;
        max-width: 1000px;
        width: 100%;
      }
      .code-block-wrapper {
        position: relative;
        background-color: #242425;
        border-radius: 16px;
        padding: 1rem;
        margin-top: 1rem;
        overflow-x: auto;
        font-family: "Fira Code", "Cascadia Code", monospace;
        font-size: 0.8em;
        color: #ffffff;
      }
      .copy-button {
        position: absolute;
        top: 10px;
        right: 10px;
        background: #333;
        border: none;
        padding: 4px;
        border-radius: 4px;
        cursor: pointer;
        color: #ffffff;
      }
      .github-icon {
        width: 18px;
        height: 18px;
        fill: #ffffff;
        margin-top: 2px;
        margin-right: 6px;
      }
      .accordion {
        margin-top: 1rem;
        border: 1px solid #2d2d2d;
        border-radius: 6px;
        overflow: hidden;
      }
      .accordion-item {
        border-bottom: 1px solid #2d2d2d;
      }
      .accordion-item:last-child {
        border-bottom: none;
      }
      .accordion-header {
        padding: 12px 16px;
        background-color: #242425;
        cursor: pointer;
        display: flex;
        justify-content: space-between;
        align-items: center;
        min-height: 44px;
      }
      .accordion-header:hover {
        background-color: #2d2d2d;
      }
      .accordion-content {
        padding: 0;
        max-height: 0;
        overflow: hidden;
        transition: max-height 0.3s ease-out;
      }
      .accordion-content.active {
        max-height: 500px;
        padding: 16px;
      }
      .environment-tag {
        display: inline-block;
        width: 60px;
        text-align: center;
        padding: 2px 0;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 500;
        margin-right: 8px;
      }
      .linux-tag {
        background-color: #3a3a3a;
        color: #8ab4f8;
      }
      .macos-tag {
        background-color: #3a3a3a;
        color: #a5d6ff;
      }
      .windows-tag {
        background-color: #3a3a3a;
        color: #81c995;
      }
      .test-tag {
        background-color: #3a3a3a;
        color: #f8b88b;
      }
      .arrow {
        transition: transform 0.2s ease;
      }
      .arrow.rotate-90 {
        transform: rotate(90deg);
      }
    </style>
  </head>
  <body>
    <div class="glass-container">
      <div class="flex items-center text-gray-400 mb-6">
        <svg
          class="github-icon"
          viewBox="0 0 16 16"
          version="1.1"
          aria-hidden="true"
        >
          <path
            fill-rule="evenodd"
            d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38C13.71 14.53 16 11.54 16 8c0-4.42-3.58-8-8-8z"
          ></path>
        </svg>
        <span class="text-base text-white bg-white-800 mr-2"
          >tds-virtual-ta</span
        >
        <span
          class="px-3 py-1.5 bg-gray-800 text-white text-xs font-medium rounded-full"
          >ai assistant</span
        >
      </div>
      <h1 class="text-white text-xl font-semibold mb-4">
        Welcome to the Virtual TA Chatbot
      </h1>
      <p class="mb-4 text-white-400">
        Virtual Teaching Assistant (Virtual TA) is an innovative, intelligent
        and automated assistant designed specifically for the Tools in Data
        Science (TDS) course offered by the IIT Madras Online Degree Program.
        This cutting-edge system revolutionizes the learning experience by
        providing students with accurate, context-aware answers to their
        questions.
      </p>
      <p class="mb-4 text-white-400">
        To use the chatbot, send a
        <code class="text-green-400">POST</code> request to the
        <code class="text-green-400">/api</code> endpoint with a JSON body.
        Optionally, include an image for analysis.
      </p>
      
      <script>
        function copyCode(elementId) {
          const code = document.getElementById(elementId).innerText;
          navigator.clipboard.writeText(code).then(() => {
            alert("Code copied to clipboard!");
          });
        }

        function toggleAccordion(element) {
          const content = element.nextElementSibling;
          content.classList.toggle("active");
          const arrow = element.querySelector(".arrow");
          arrow.classList.toggle("rotate-90");
        }

        function updateEndpoint() {
          const newEndpoint = document.getElementById("apiEndpoint").value;
          const commandElement = document.getElementById("dynamicCommand");
          commandElement.textContent = commandElement.textContent.replace(
            /curl -X POST ".*?"/,
            `curl -X POST "${newEndpoint}"`
          );

          // Update all other curl commands in the document
          document.querySelectorAll(".dynamic-endpoint").forEach((el) => {
            el.textContent = newEndpoint;
          });
        }

        async function testEndpoint() {
          const endpoint = document.getElementById("apiEndpoint").value;
          const testResult = document.getElementById("testResult");
          const responseStatus = document.getElementById("responseStatus");
          const responseData = document.getElementById("responseData");
          const testButton = document.getElementById("testButton");

          testButton.disabled = true;
          testButton.innerHTML = `
                <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Testing...
            `;

          testResult.classList.add("hidden");
          responseStatus.textContent = "";
          responseData.textContent = "Testing...";

          try {
            const response = await fetch(endpoint, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                // Add authentication header if needed
                // "Authorization": "Bearer YOUR_API_KEY"
              },
              body: JSON.stringify({
                question: "Test question to check API functionality",
              }),
            });

            let data;
            const contentType = response.headers.get("Content-Type");
            if (contentType && contentType.includes("application/json")) {
              data = await response.json();
            } else {
              data = await response.text();
            }

            responseStatus.textContent = `${response.status} ${response.statusText}`;
            responseStatus.className = `ml-2 px-2 py-1 rounded ${
              response.ok ? "bg-green-600 text-white" : "bg-red-600 text-white"
            }`;

            responseData.textContent =
              typeof data === "object" ? JSON.stringify(data, null, 2) : data;
            testResult.classList.remove("hidden");
          } catch (error) {
            responseStatus.textContent = "Error";
            responseStatus.className =
              "ml-2 px-2 py-1 rounded bg-red-600 text-white";
            responseData.textContent = error.message;
            testResult.classList.remove("hidden");
          } finally {
            testButton.disabled = false;
            testButton.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    Test API Endpoint
                `;
          }
        }
      </script>
      <div class="accordion">
        <!-- API Endpoint Tester -->
        <div class="accordion-item">
          <div class="accordion-header" onclick="toggleAccordion(this)">
            <div class="flex items-center">
              <span class="environment-tag test-tag">Test</span>
              <span class="ml-2 text-gray-300">API Endpoint Tester</span>
            </div>
            <svg
              class="arrow w-4 h-4 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 5l7 7-7 7"
              ></path>
            </svg>
          </div>
          <div class="accordion-content bg-gray-900">
            <div class="mb-4">
              <label
                for="apiEndpoint"
                class="block text-sm font-medium text-gray-300 mb-1"
              >
                API Endpoint URL
              </label>
              <div class="flex">
                <input
                  type="text"
                  id="apiEndpoint"
                  value="https://app.example.com/api/"
                  class="flex-1 bg-gray-700 text-white rounded-l-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                />
                <button
                  onclick="updateEndpoint()"
                  class="bg-blue-600 hover:bg-blue-800 text-white px-3 py-2 rounded-r-md text-sm"
                >
                  Update
                </button>
              </div>
              <p class="mt-1 text-xs text-gray-400">
                Here enter your deployed API endpoint URL for testing purposes.
              </p>
            </div>

            <div class="code-block-wrapper">
              <button
                class="copy-button"
                onclick="copyCode('dynamicCommand')"
                title="Copy to clipboard"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  xml:space="preserve"
                  width="16"
                  height="16"
                  viewBox="0 0 96 96"
                >
                  <path
                    d="M72 12h-4.697C65.652 7.342 61.223 4 56 4H40c-5.223 0-9.652 3.342-11.303 8H24c-6.63 0-12 5.37-12 12v56c0 6.63 5.37 12 12 12h48c6.63 0 12-5.37 12-12V24c0-6.63-5.37-12-12-12zm-32 0h16a4 4 0 0 1 0 8H40a4 4 0 0 1 0-8zm36 68c0 2.21-1.79 4-4 4H24c-2.21 0-4-1.79-4-4V24c0-2.21 1.79-4 4-4h4.697c1.648 4.658 6.08 8 11.303 8h16c5.223 0 9.652-3.342 11.303-8H72c2.21 0 4 1.79 4 4v56z"
                  ></path>
                </svg>
              </button>
              <pre
                id="testCommand"
              ><code id="dynamicCommand">curl -X POST "https://app.example.com/api/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Test question",
    "image": "'"$(curl -s "https://tds.s-anand.net/images/test-image.webp" | base64 -w0)"'"
  }'</code></pre>
            </div>

            <div class="mt-4">
              <button
                id="testButton"
                onclick="testEndpoint()"
                class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm flex items-center"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  class="h-4 w-4 mr-2"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M13 10V3L4 14h7v7l9-11h-7z"
                  />
                </svg>
                Test API Endpoint
              </button>
              <div id="testResult" class="mt-3 hidden">
                <div class="flex items-center text-sm font-medium">
                  <span>Response Status:</span>
                  <span
                    id="responseStatus"
                    class="ml-2 px-2 py-1 rounded"
                  ></span>
                </div>
                <pre
                  id="responseData"
                  class="mt-2 bg-gray-800 p-3 rounded text-xs overflow-auto max-h-40"
                ></pre>
              </div>
            </div>
          </div>
        </div>

        <!-- Linux Command -->
        <div class="accordion-item">
          <div class="accordion-header" onclick="toggleAccordion(this)">
            <div class="flex items-center">
              <span class="environment-tag linux-tag">Linux</span>
              <span class="ml-2 text-gray-300">Linux Command</span>
            </div>
            <svg
              class="arrow w-4 h-4 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 5l7 7-7 7"
              ></path>
            </svg>
          </div>
          <div class="accordion-content bg-gray-900">
            <div class="code-block-wrapper">
              <button
                class="copy-button"
                onclick="copyCode('linuxCommand')"
                title="Copy to clipboard"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  xml:space="preserve"
                  width="16"
                  height="16"
                  viewBox="0 0 96 96"
                >
                  <path
                    d="M72 12h-4.697C65.652 7.342 61.223 4 56 4H40c-5.223 0-9.652 3.342-11.303 8H24c-6.63 0-12 5.37-12 12v56c0 6.63 5.37 12 12 12h48c6.63 0 12-5.37 12-12V24c0-6.63-5.37-12-12-12zm-32 0h16a4 4 0 0 1 0 8H40a4 4 0 0 1 0-8zm36 68c0 2.21-1.79 4-4 4H24c-2.21 0-4-1.79-4-4V24c0-2.21 1.79-4 4-4h4.697c1.648 4.658 6.08 8 11.303 8h16c5.223 0 9.652-3.342 11.303-8H72c2.21 0 4 1.79 4 4v56z"
                  ></path>
                </svg>
              </button>
              <pre
                id="linuxCommand"
              ><code>curl -X POST "<span class="dynamic-endpoint">https://app.example.com/api/</span>" \
  -H "Content-Type: application/json" \
  -d "$(jq -n \
    --arg question "YOUR_QUESTION_HERE" \
    --arg image "$(curl -s "IMAGE_URL" | base64 -w0)" \
    '{question: $question, image: $image}')"</code></pre>
            </div>
            <div class="mt-2 text-sm text-gray-400">
              <p>
                Requirements: Install <code class="text-blue-400">jq</code> if
                missing:
              </p>
              <pre
                class="bg-gray-800 p-2 rounded mt-1"
              ><code>sudo apt install jq    # Debian/Ubuntu
sudo dnf install jq    # Fedora</code></pre>
            </div>
          </div>
        </div>

        <!-- macOS Command -->
        <div class="accordion-item">
          <div class="accordion-header" onclick="toggleAccordion(this)">
            <div class="flex items-center">
              <span class="environment-tag macos-tag">macOS</span>
              <span class="ml-2 text-gray-300">macOS Command</span>
            </div>
            <svg
              class="arrow w-4 h-4 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 5l7 7-7 7"
              ></path>
            </svg>
          </div>
          <div class="accordion-content bg-gray-900">
            <div class="code-block-wrapper">
              <button
                class="copy-button"
                onclick="copyCode('macosCommand')"
                title="Copy to clipboard"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  xml:space="preserve"
                  width="16"
                  height="16"
                  viewBox="0 0 96 96"
                >
                  <path
                    d="M72 12h-4.697C65.652 7.342 61.223 4 56 4H40c-5.223 0-9.652 3.342-11.303 8H24c-6.63 0-12 5.37-12 12v56c0 6.63 5.37 12 12 12h48c6.63 0 12-5.37 12-12V24c0-6.63-5.37-12-12-12zm-32 0h16a4 4 0 0 1 0 8H40a4 4 0 0 1 0-8zm36 68c0 2.21-1.79 4-4 4H24c-2.21 0-4-1.79-4-4V24c0-2.21 1.79-4 4-4h4.697c1.648 4.658 6.08 8 11.303 8h16c5.223 0 9.652-3.342 11.303-8H72c2.21 0 4 1.79 4 4v56z"
                  ></path>
                </svg>
              </button>
              <pre
                id="macosCommand"
              ><code>curl -X POST "<span class="dynamic-endpoint">https://app.example.com/api/</span>" \
  -H "Content-Type: application/json" \
  -d "$(jq -n \
    --arg question "YOUR_QUESTION_HERE" \
    --arg image "$(curl -s "IMAGE_URL" | base64)" \
    '{question: $question, image: $image}')"</code></pre>
            </div>
            <div class="mt-2 text-sm text-gray-400">
              <p>Note: If your API requires single-line base64, use:</p>
              <pre
                class="bg-gray-800 p-2 rounded mt-1"
              ><code>curl -s "IMAGE_URL" | base64 | tr -d '\n'</code></pre>
            </div>
          </div>
        </div>

        <!-- Windows Command -->
        <div class="accordion-item">
          <div class="accordion-header" onclick="toggleAccordion(this)">
            <div class="flex items-center">
              <span class="environment-tag windows-tag">Windows</span>
              <span class="ml-2 text-gray-300">PowerShell Command</span>
            </div>
            <svg
              class="arrow w-4 h-4 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 5l7 7-7 7"
              ></path>
            </svg>
          </div>
          <div class="accordion-content bg-gray-900">
            <div class="code-block-wrapper">
              <button
                class="copy-button"
                onclick="copyCode('windowsCommand')"
                title="Copy to clipboard"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  xml:space="preserve"
                  width="16"
                  height="16"
                  viewBox="0 0 96 96"
                >
                  <path
                    d="M72 12h-4.697C65.652 7.342 61.223 4 56 4H40c-5.223 0-9.652 3.342-11.303 8H24c-6.63 0-12 5.37-12 12v56c0 6.63 5.37 12 12 12h48c6.63 0 12-5.37 12-12V24c0-6.63-5.37-12-12-12zm-32 0h16a4 4 0 0 1 0 8H40a4 4 0 0 1 0-8zm36 68c0 2.21-1.79 4-4 4H24c-2.21 0-4-1.79-4-4V24c0-2.21 1.79-4 4-4h4.697c1.648 4.658 6.08 8 11.303 8h16c5.223 0 9.652-3.342 11.303-8H72c2.21 0 4 1.79 4 4v56z"
                  ></path>
                </svg>
              </button>
              <pre
                id="windowsCommand"
              ><code>$imageBase64 = [Convert]::ToBase64String((Invoke-WebRequest -Uri "IMAGE_URL" -UseBasicParsing).Content)
$body = @{
    question = "YOUR_QUESTION_HERE"
    image = $imageBase64
} | ConvertTo-Json -Compress

curl.exe -X POST "<span class="dynamic-endpoint">https://app.example.com/api/</span>" `
    -H "Content-Type: application/json" `
    -d $body</code></pre>
            </div>
          </div>
        </div>
      </div>
      <footer class="mt-6 text-sm text-slate-400">
        Explore the
        <a href="/docs" class="text-sky-400 hover:underline"
          >API documentation</a
        >
        or check out the source code on
        <a
          href="https://github.com/dopeforce/tds-virtual-ta"
          target="_blank"
          class="text-sky-400 hover:underline"
          >GitHub</a
        >.
      </footer>
    </div>
  </body>
</html>
"""
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
app.include_router(api_router, prefix="/api", tags=["API"])