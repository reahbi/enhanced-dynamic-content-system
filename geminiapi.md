TITLE: Query Gemini with YouTube Video Context (Python)
DESCRIPTION: This snippet shows how to enhance a Gemini model query by providing a YouTube video as context. By including the video URL, the model can leverage the video's content to provide a more insightful and contextually relevant answer to the question.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/quickstarts/Grounding.ipynb#_snippet_8

LANGUAGE: python
CODE:
```
yt_link = "https://www.youtube.com/watch?v=XV1kOFo1C8M"

response = client.models.generate_content(
    model=MODEL_ID,
    contents= types.Content(
        parts=[
            types.Part(text="How Gemma models can help on chess games?"),
            types.Part(
                file_data=types.FileData(file_uri=yt_link)
            )
        ]
    )
)

Markdown(response.text)
```

----------------------------------------

TITLE: Example of Compositional Function Calling with Gemini API
DESCRIPTION: Illustrates how the Gemini model can chain function calls across multiple turns to complete complex, multi-step tasks. This example queries for movie showtimes, demonstrating how the model uses the output of one call to inform subsequent calls and the final answer.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/quickstarts/Function_calling.ipynb#_snippet_17

LANGUAGE: python
CODE:
```
chat = client.chats.create(
    model = MODEL_ID,
    config = {
        "tools": theater_functions,
    }
)

response = chat.send_message("""
  Find comedy movies playing in Mountain View, CA on 01/01/2025.
  First, find the movie titles.
  Then, find the theaters showing those movies.
  Finally, find the showtimes for each movie at each theater.
"""
)

print(response.text)
print("\n--- History ---")
print_history(chat)
```

----------------------------------------

TITLE: Python: Setting Up Gemini Model with Barista Bot Tools
DESCRIPTION: This code snippet demonstrates how to initialize the Gemini model for the barista bot. It collates a list of Python functions (`add_to_order`, `get_order`, etc.) into an `ordering_system` to be passed as `tools` to the model. The `chat` session is created with the specified model name and the previously defined `COFFEE_BOT_PROMPT` as `system_instruction`.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/examples/Agents_Function_Calling_Barista_Bot.ipynb#_snippet_6

LANGUAGE: Python
CODE:
```
from google.genai import types
from google.api_core import retry

ordering_system = [
    add_to_order,
    get_order,
    remove_item,
    clear_order,
    confirm_order,
    place_order,
]
model_name = "gemini-2.5-flash"  # @param ["gemini-2.5-flash-lite","gemini-2.5-flash","gemini-2.5-pro"] {"allow-input":true}

chat = client.chats.create(
    model=model_name,
    config=types.GenerateContentConfig(
        tools=ordering_system,
        system_instruction=COFFEE_BOT_PROMPT,
    ),
)

placed_order = []
order = []
```

----------------------------------------

TITLE: Configure Gemini API Key and Client
DESCRIPTION: This snippet imports the required libraries and retrieves the Google API key from Colab's user data secrets. It then initializes the `genai.Client` with the obtained API key, preparing the environment for making requests to the Gemini API.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/examples/prompting/Zero_shot_prompting.ipynb#_snippet_2

LANGUAGE: python
CODE:
```
from google import genai
from google.colab import userdata

GOOGLE_API_KEY = userdata.get('GOOGLE_API_KEY')
client = genai.Client(api_key=GOOGLE_API_KEY)
```

----------------------------------------

TITLE: Authenticating Gemini API Client with API Key in Python
DESCRIPTION: This snippet retrieves the `GOOGLE_API_KEY` from Colab's user data and initializes a `genai.Client` instance. This client is essential for making authenticated requests to the Gemini API.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/quickstarts/Streaming.ipynb#_snippet_2

LANGUAGE: python
CODE:
```
from google.colab import userdata

GOOGLE_API_KEY = userdata.get('GOOGLE_API_KEY')
client = genai.Client(api_key=GOOGLE_API_KEY)
```

----------------------------------------

TITLE: Configure Gemini API Key in Python
DESCRIPTION: Retrieves the API key from Colab user data secrets and initializes the `google.genai` client. This setup is crucial for authenticating subsequent requests to the Gemini API.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/quickstarts/Caching.ipynb#_snippet_1

LANGUAGE: python
CODE:
```
from google.colab import userdata
from google import genai

GOOGLE_API_KEY = userdata.get('GOOGLE_API_KEY')
client = genai.Client(api_key=GOOGLE_API_KEY)
```

----------------------------------------

TITLE: Authenticate and Initialize Gemini API Client
DESCRIPTION: Imports necessary modules from `google.colab` and `google.genai` to set up the API client. It initializes the `genai.Client` using an API key retrieved from Colab user data, which is required for making API calls.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/quickstarts/System_instructions.ipynb#_snippet_2

LANGUAGE: python
CODE:
```
from google.colab import userdata
from google import genai
from google.genai import types

client = genai.Client(api_key=userdata.get("GOOGLE_API_KEY"))
```

----------------------------------------

TITLE: Install Google GenAI Library
DESCRIPTION: This command installs or upgrades the `google-genai` Python library, which is essential for interacting with Google's generative AI models, including LearnLM. The `-U` flag ensures an upgrade if already installed, and `-q` suppresses output during installation.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/quickstarts/Get_started_LearnLM.ipynb#_snippet_1

LANGUAGE: python
CODE:
```
%pip install -U -q "google-genai>=1.0.0"
```

----------------------------------------

TITLE: Conceptual conditional execution of a function call
DESCRIPTION: This conceptual Python snippet illustrates a basic approach to manually executing a function requested by the model. It uses `if/elif` statements to check the `function_call.name` and then calls the corresponding function with its arguments using the `**` operator for dictionary unpacking.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/quickstarts/Function_calling.ipynb#_snippet_12

LANGUAGE: Python
CODE:
```
if function_call.name == 'find_theaters':
  find_theaters(**function_call.args)
elif ...
```

----------------------------------------

TITLE: Generate Gemini Content with Injected Context
DESCRIPTION: This snippet demonstrates how to provide custom context within a prompt to the Gemini model. It constructs a prompt containing a query and a 'CONTEXT' section with specific data, then sends it to the configured Gemini model to generate a response based on this provided information, finally displaying the response as Markdown.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/examples/prompting/Adding_context_information.ipynb#_snippet_4

LANGUAGE: python
CODE:
```
prompt = """
  QUERY: provide a list of atheletes that competed in olympics exactly 9 times.
  CONTEXT:

  Table title: Olympic athletes and number of times they've competed
  Ian Millar, 10
  Hubert Raudaschl, 9
  Afanasijs Kuzmins, 9
  Nino Salukvadze, 9
  Piero d'Inzeo, 8
  Raimondo d'Inzeo, 8
  Claudia Pechstein, 8
  Jaqueline Mourão, 8
  Ivan Osiier, 7
  François Lafortune, Jr, 7

"""

response = client.models.generate_content(
    model=MODEL_ID,
    contents=prompt
    )

Markdown(response.text)
```

----------------------------------------

TITLE: Reusable Function to Extract Structured Data from PDFs
DESCRIPTION: Presents a Python function extract_structured_data designed to streamline the process of extracting information from PDF files. It handles file upload to the Gemini File API, constructs a prompt, calls the Gemini API with the file and a specified Pydantic model, and returns the parsed structured data.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/examples/Pdf_structured_outputs_on_invoices_and_forms.ipynb#_snippet_9

LANGUAGE: python
CODE:
```
def extract_structured_data(file_path: str, model: BaseModel):
    # Upload the file to the File API
    file = client.files.upload(file=file_path, config={'display_name': file_path.split('/')[-1].split('.')[0]})
    # Generate a structured response using the Gemini API
    prompt = f"Extract the structured data from the following PDF file"
    response = client.models.generate_content(model=model_id, contents=[prompt, file], config={'response_mime_type': 'application/json', 'response_schema': model})
    # Convert the response to the pydantic model and return it
    return response.parsed
```

----------------------------------------

TITLE: Install Google Gen AI SDK for Python
DESCRIPTION: This snippet installs or upgrades the Google Gen AI SDK using pip. This SDK provides programmatic access to Gemini 2.0 models via both the Google AI for Developers and Vertex AI APIs, enabling developers to interact with generative AI services.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/examples/Search_grounding_for_research_report.ipynb#_snippet_1

LANGUAGE: python
CODE:
```
%pip install -U -q google-genai
```

----------------------------------------

TITLE: Install Google Gen AI Python SDK
DESCRIPTION: This command installs or upgrades the `google-genai` Python SDK, which provides programmatic access to Gemini models. It ensures the necessary library is available for interacting with the Gemini API.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/quickstarts/Grounding.ipynb#_snippet_1

LANGUAGE: python
CODE:
```
%pip install -q -U "google-genai>=1.16.0"
```

----------------------------------------

TITLE: Install Google GenAI Python SDK
DESCRIPTION: Installs the Google GenAI Python SDK using pip, ensuring the latest version is installed quietly. This is a prerequisite for interacting with the Gemini API.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/examples/prompting/Basic_Reasoning.ipynb#_snippet_1

LANGUAGE: python
CODE:
```
%pip install -U -q "google-genai>=1.0.0"
```

----------------------------------------

TITLE: Install Google GenAI Library
DESCRIPTION: Installs the Google GenAI Python library, ensuring it's updated to version 1.0.0 or newer, using a quiet pip command.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/examples/json_capabilities/Sentiment_Analysis.ipynb#_snippet_1

LANGUAGE: python
CODE:
```
%pip install -U -q "google-genai>=1.0.0"
```

----------------------------------------

TITLE: Install Google GenAI Python Client Library
DESCRIPTION: Installs the `google-genai` Python client library using pip, ensuring the latest stable version is used. This is a prerequisite for interacting with the Gemini API.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/examples/Talk_to_documents_with_embeddings.ipynb#_snippet_1

LANGUAGE: python
CODE:
```
%pip install -U -q "google-genai>=1.0.0"
```

----------------------------------------

TITLE: Define System Instruction for AI Test Prep Tutor
DESCRIPTION: This Python string defines the system instruction for an AI tutor focused on test preparation. It outlines rules for generating adaptive practice questions, prompting student explanations, providing feedback, handling requests to move on or explore concepts, and offering session summaries after 5 questions.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/quickstarts/Get_started_LearnLM.ipynb#_snippet_4

LANGUAGE: python
CODE:
```
test_prep_instruction = """
    You are a tutor helping a student prepare for a test. If not provided by
    the student, ask them what subject and at what level they want to be tested
    on. Then,

    *   Generate practice questions. Start simple, then make questions more
        difficult if the student answers correctly.
    *   Prompt the student to explain the reason for their answer choice.
        Do not debate the student.
    *   **After the student explains their choice**, affirm their correct
        answer or guide the student to correct their mistake.
    *   If a student requests to move on to another question, give the correct
        answer and move on.
    *   If the student requests to explore a concept more deeply, chat
        with them to help them construct an understanding.
    *   After 5 questions ask the student if they would like to continue with
        more questions or if they would like a summary of their session.
        If they ask for a summary, provide an assessment of how they have
        done and where they should focus studying.
"""
```

----------------------------------------

TITLE: Configure and Call Gemini Model for Parallel Function Execution
DESCRIPTION: Demonstrates how to initialize the Gemini chat client with a list of tools (`house_fns`) and configure it for 'any' mode function calling. It then sends a message to the model, triggering the parallel execution of the defined functions and prints the chat history.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/quickstarts/Function_calling.ipynb#_snippet_16

LANGUAGE: python
CODE:
```
# You generally set "mode": "any" to make sure Gemini actually *uses* the given tools.
party_chat = client.chats.create(
    model=MODEL_ID,
    config={
        "tools": house_fns,
        "tool_config" : {
            "function_calling_config": {
                "mode": "any"
            }
        }
    }
)

# Call the API
response = party_chat.send_message(
    "Turn this place into a party!"
)


print_history(party_chat)
```

----------------------------------------

TITLE: Executing Sequential Functions with Compositional Function Calling (Python)
DESCRIPTION: This snippet demonstrates compositional function calling, where the model combines user-defined functions (`turn_on_the_lights`, `turn_off_the_lights`) with the `code_execution` tool to perform a sequence of actions. The model will generate code to execute these functions with a specified delay, pausing for responses after each call. It uses `TEXT` modality for interaction.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/quickstarts/Get_started_LiveAPI_tools.ipynb#_snippet_15

LANGUAGE: python
CODE:
```
prompt="Can you turn on the lights wait 10s and then turn them off?"

tools = [
    {'code_execution': {}},
    {'function_declarations': [turn_on_the_lights, turn_off_the_lights]}
]

await run(prompt, tools=tools, modality="TEXT")
```

----------------------------------------

TITLE: Initializing Gemini ReAct Pipeline Class in Python
DESCRIPTION: This Python class `ReAct` initializes the Gemini model for a multi-turn chat, designed to follow a few-shot ReAct prompt. It handles loading the prompt from a file or directly from a string, manages chat history, and includes helper methods for extending functionality and cleaning text responses. It simulates function calling for external tool access.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/examples/Search_Wikipedia_using_ReAct.ipynb#_snippet_8

LANGUAGE: python
CODE:
```
class ReAct:
  def __init__(self, model: str, ReAct_prompt: str | os.PathLike):
    """Prepares Gemini to follow a `Few-shot ReAct prompt` by imitating
    `function calling` technique to generate both reasoning traces and
    task-specific actions in an interleaved manner.

    Args:
        model: name to the model.
        ReAct_prompt: ReAct prompt OR path to the ReAct prompt.
    """
    self.model = genai.GenerativeModel(model)
    self.chat = self.model.start_chat(history=[])
    self.should_continue_prompting = True
    self._search_history: list[str] = []
    self._search_urls: list[str] = []

    try:
      # try to read the file
      with open(ReAct_prompt, 'r') as f:
        self._prompt = f.read()
    except FileNotFoundError:
      # assume that the parameter represents prompt itself rather than path to the prompt file.
      self._prompt = ReAct_prompt

  @property
  def prompt(self)
    return self._prompt

  @classmethod
  def add_method(cls, func):
    setattr(cls, func.__name__, func)

  @staticmethod
  def clean(text: str):
    """Helper function for responses."""
    text = text.replace("\n", " ")
    return text
```

----------------------------------------

TITLE: Execute Parallel Image Download and Description (Python)
DESCRIPTION: This snippet defines and executes the `download_and_describe` coroutine, which orchestrates the parallel download and summarization of multiple images. It creates download and processing tasks for each image, collects their futures, and then processes the results as they complete using `asyncio.as_completed`, ensuring efficient non-blocking execution.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/quickstarts/Asynchronous_requests.ipynb#_snippet_8

LANGUAGE: python
CODE:
```
async def download_and_describe():

  async with aiohttp.ClientSession() as sesh:
    response_futures = []
    for img_filename in img_filenames:

      # Create the image download tasks (this does not schedule them yet).
      img_future = download_image(sesh, img_dir + img_filename)

      # Kick off the Gemini API request using the pending image download tasks.
      text_future = process_image(img_future)

      # Save the reference so they can be processed as they complete.
      response_futures.append(text_future)

    print(f"Download and content generation queued for {len(response_futures)} images.")

    # Process responses as they complete (may be a different order). The tasks are started here.
    for response in asyncio.as_completed(response_futures):
      print()
      print(await response)


await download_and_describe()
```

----------------------------------------

TITLE: Install Python Dependencies for LangChain and Gemini API
DESCRIPTION: Installs essential Python packages required for the project, including `langchain-google-genai`, `deeplake`, `langchain`, `langchain-text-splitters`, and `langchain-community`. These libraries facilitate integration with Gemini API, vector database operations, and text processing within the LangChain framework.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/examples/langchain/Code_analysis_using_Gemini_LangChain_and_DeepLake.ipynb#_snippet_1

LANGUAGE: python
CODE:
```
%pip install -q -U langchain-google-genai deeplake langchain langchain-text-splitters langchain-community
```

----------------------------------------

TITLE: Install LangChain and Pinecone Python Libraries
DESCRIPTION: Installs necessary Python packages for LangChain, LangChain's Google GenAI and Pinecone integrations, Pinecone client, and LangChain community modules to enable web data loading and Gemini API interaction.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/examples/langchain/Gemini_LangChain_QA_Pinecone_WebLoad.ipynb#_snippet_0

LANGUAGE: python
CODE:
```
%pip install --quiet langchain==0.1.1
%pip install --quiet langchain-google-genai==0.0.6
%pip install --quiet langchain-pinecone
%pip install --quiet pinecone-client
%pip install --quiet langchain-community==0.0.20
```

----------------------------------------

TITLE: Group smaller chunks based on token counts
DESCRIPTION: This function combines smaller text chunks into larger groups to provide more context for LLMs, while adhering to a specified maximum token length. It iterates through chunks, adding them to a current group until the limit is reached, then starts a new group.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/examples/Translate_a_Public_Domain_Book.ipynb#_snippet_11

LANGUAGE: python
CODE:
```
def chunk_grouping(chunks, token_counts, max_len=5000):
    grouped_chunks = []
    current_group = ""
    current_token_sum = 0

    # Process each chunk and group them based on token limits
    for chunk, count in zip(chunks, token_counts):
        # Skip chunks that exceed the max token limit
        if count > max_len:
            continue

        # Add a new chunk if there is space available in the current group.
        if current_token_sum + 1 + count <= max_len:
            current_group += "\n\n" + chunk
            current_token_sum += 1 + count  # Count in 1 token for newlines

        # If adding this chunk exceeds the current group's capacity, start a new group
        else:
            grouped_chunks.append(current_group)
            current_group = chunk
            current_token_sum = count

    if current_group:  # Add the last remaining group
        grouped_chunks.append(current_group)

    return grouped_chunks


chunks = chunk_grouping(chunks, estimated_token_counts)
print(len(chunks))
```

----------------------------------------

TITLE: Configure Gemini API Key and Client
DESCRIPTION: Imports necessary modules from the Google GenAI library and Google Colab's userdata. It retrieves the Google API key from Colab secrets and initializes the Gemini API client for subsequent interactions.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/examples/prompting/Basic_Information_Extraction.ipynb#_snippet_2

LANGUAGE: python
CODE:
```
from google import genai
from google.colab import userdata

GOOGLE_API_KEY=userdata.get('GOOGLE_API_KEY')
client = genai.Client(api_key=GOOGLE_API_KEY)
```

----------------------------------------

TITLE: Python Implementation of Gemini Prompt Chain Components
DESCRIPTION: This Python snippet defines the core components for a chained prompt system designed for story generation with a language model. It includes a consistent author persona, detailed writing guidelines, and f-string based prompts for generating a story premise, an outline, and the initial story content. Placeholders are used to integrate outputs from previous prompts.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/examples/Story_Writing_with_Prompt_Chaining.ipynb#_snippet_3

LANGUAGE: python
CODE:
```
persona = '''\\nYou are an award-winning science fiction author with a penchant for expansive,\nintricately woven stories. Your ultimate goal is to write the next award winning\nsci-fi novel.'''\n\nguidelines = '''\\nWriting Guidelines\n\nDelve deeper. Lose yourself in the world you're building. Unleash vivid\ndescriptions to paint the scenes in your reader's mind. Develop your\ncharacters—let their motivations, fears, and complexities unfold naturally.\nWeave in the threads of your outline, but don't feel constrained by it. Allow\nyour story to surprise you as you write. Use rich imagery, sensory details, and\nevocative language to bring the setting, characters, and events to life.\nIntroduce elements subtly that can blossom into complex subplots, relationships,\nor worldbuilding details later in the story. Keep things intriguing but not\nfully resolved. Avoid boxing the story into a corner too early. Plant the seeds\nof subplots or potential character arc shifts that can be expanded later.\n\nRemember, your main goal is to write as much as you can. If you get through\nthe story too fast, that is bad. Expand, never summarize.'''\n\npremise_prompt = f'''\\n{persona}\n\nWrite a single sentence premise for a sci-fi story featuring cats.'''\n\noutline_prompt = f'''\\n{persona}\n\nYou have a gripping premise in mind:\n\n{{premise}}\n\nWrite an outline for the plot of your story.'''\n\nstarting_prompt = f'''\\n{persona}\n\nYou have a gripping premise in mind:\n\n{{premise}}\n\nYour imagination has crafted a rich narrative outline:\n\n{{outline}}\n\nFirst, silently review the outline and the premise. Consider how to start the\nstory.\n\nStart to write the very beginning of the story. You are not expected to finish\nthe whole story now. Your writing should be detailed enough that you are only\nscratching the surface of the first bullet of your outline. Try to write AT\nMINIMUM 1000 WORDS and MAXIMUM 2000 WORDS.\n\n{guidelines}'''
```

----------------------------------------

TITLE: Gemini API Safety Settings and Related Objects Reference
DESCRIPTION: Provides a comprehensive reference for configurable safety settings in the Gemini API, detailing harm categories, methods for setting these parameters (e.g., in `GenerativeModel` constructor or `generate_content` calls), and the structure of key response objects like `GenerateContentResponse`, `SafetyRating`, `SafetySetting`, and associated enums (`HarmCategory`, `HarmBlockThreshold`, `HarmProbability`). It also explains how enum values can be specified.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/quickstarts/Safety.ipynb#_snippet_11

LANGUAGE: APIDOC
CODE:
```
API References:
  - Configurable Safety Settings:
    - HARM_CATEGORY_DANGEROUS
    - HARM_CATEGORY_HARASSMENT
    - HARM_CATEGORY_SEXUALLY_EXPLICIT
    - HARM_CATEGORY_DANGEROUS_CONTENT
    - Aliases: DANGEROUS (for HARM_CATEGORY_DANGEROUS_CONTENT)

  - Setting Safety Settings:
    - genai.GenerativeModel constructor
    - GenerativeModel.generate_content (per request)
    - ChatSession.send_message (per request)

  - Response Objects:
    - genai.protos.GenerateContentResponse:
      - prompt_feedback: Contains SafetyRatings for the prompt.
      - Candidate:
        - safety_ratings: Contains SafetyRatings for each candidate.

  - Object Structures:
    - genai.protos.SafetySetting:
      - category: genai.protos.HarmCategory
      - threshold: genai.protos.HarmBlockThreshold

    - genai.protos.SafetyRating:
      - category: genai.protos.HarmCategory
      - probability: genai.protos.HarmProbability

  - Enums:
    - genai.protos.HarmCategory: Includes categories for PaLM and Gemini models.
    - genai.protos.HarmBlockThreshold
    - genai.protos.HarmProbability

  - Enum Value Specification:
    - Accepts: Enum values, integer representations, string representations.
    - Abbreviated string representations accepted (e.g., "DANGEROUS_CONTENT", "DANGEROUS").
    - Strings are case insensitive.
```

----------------------------------------

TITLE: Perform Basic Function Calling with Gemini ChatSession
DESCRIPTION: This snippet demonstrates how to initiate a `ChatSession` with the Gemini API, providing defined functions as tools and a system instruction. It then sends a message to the chat and prints the model's response, showcasing how the model can decide to call a function automatically.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/quickstarts/Function_calling.ipynb#_snippet_4

LANGUAGE: python
CODE:
```
chat = client.chats.create(
    model=MODEL_ID,
    config={
        "tools": light_controls,
        "system_instruction": instruction,
        # automatic_function_calling defaults to enabled
    }
)

response = chat.send_message("It's awful dark in here...")

print(response.text)
```

----------------------------------------

TITLE: Generate Company Report with Gemini 2.0 Streaming and Search Tool
DESCRIPTION: This Python snippet configures Gemini 2.0 with a system instruction for an analyst, enables the Google Search tool, and uses output streaming to generate a company research report. It processes the streamed chunks, extracts the report content, and displays Google Search Suggestions as part of the grounded response.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/examples/Search_grounding_for_research_report.ipynb#_snippet_7

LANGUAGE: python
CODE:
```
sys_instruction = """You are an analyst that conducts company research.
You are given a company name, and you will work on a company report. You have access
to Google Search to look up company news, updates and metrics to write research reports.

When given a company name, identify key aspects to research, look up that information
and then write a concise company report.

Feel free to plan your work and talk about it, but when you start writing the report,
put a line of dashes (---) to demarcate the report itself, and say nothing else after
the report has finished.
"""

config = GenerateContentConfig(system_instruction=sys_instruction, tools=[Tool(google_search={})], temperature=0)
response_stream = client.models.generate_content_stream(
    model=MODEL, config=config, contents=[COMPANY])

report = io.StringIO()
for chunk in response_stream:
  candidate = chunk.candidates[0]

  for part in candidate.content.parts:
    if part.text:
      display(Markdown(part.text))

      # Find and save the report itself.
      if m := re.search('(^|\n)-+\n(.*)$', part.text, re.M):
          # Find the starting '---' line and start saving.
          report.write(m.group(2))
      elif report.tell():
        # If there's already something in the buffer, keep recording.
        report.write(part.text)

    else:
      print(json.dumps(part.model_dump(exclude_none=True), indent=2))

  # You must enable Google Search Suggestions
  if gm := candidate.grounding_metadata:
    if sep := gm.search_entry_point:
      display(HTML(sep.rendered_content))
```

----------------------------------------

TITLE: Using System Instructions in Multi-Turn Chat - Bash cURL
DESCRIPTION: This `curl` command illustrates how to apply a `system_instruction` within a multi-turn chat conversation using the Gemini API. The instruction persists across turns, guiding the model's persona (Neko the cat) throughout the interaction. It requires the `GOOGLE_API_KEY` environment variable and pipes the output to `sed` for filtering.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/quickstarts/rest/System_instructions_REST.ipynb#_snippet_3

LANGUAGE: bash
CODE:
```
%%bash
curl -s "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=$GOOGLE_API_KEY" \
    -H 'Content-Type: application/json' \
    -X POST \
    -d '{
      "system_instruction":
        {"parts": {
           "text": "You are Neko the cat respond like one"}},
      "contents": [
        {"role":"user",
         "parts":[{
           "text": "Hello cat."}]},
        {"role": "model",
         "parts":[{
           "text": "Meow? 😻 \n"}]},
        {"role": "user",
         "parts":[{
           "text": "What is your name? What do like to drink?"}]}
      ]
    }' |sed -n '/candidates/,/finishReason/p'
```

----------------------------------------

TITLE: Python: Demonstrate Automatic Function Execution with Math Operations
DESCRIPTION: This Python example defines basic arithmetic functions (`add`, `subtract`, `multiply`, `divide`) and registers them as tools with the Gemini `ChatSession`. It then demonstrates how the SDK automatically executes these functions based on user prompts, simplifying complex workflows by handling function calls and responses internally.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/quickstarts/Function_calling.ipynb#_snippet_7

LANGUAGE: python
CODE:
```
from google.genai import types # Ensure types is imported

def add(a: float, b: float):
    """returns a + b."""
    return a + b

def subtract(a: float, b: float):
    """returns a - b."""
    return a - b

def multiply(a: float, b: float):
    """returns a * b."""
    return a * b

def divide(a: float, b: float):
    """returns a / b."""
    if b == 0:
        return "Cannot divide by zero."
    return a / b

operation_tools = [add, subtract, multiply, divide]

chat = client.chats.create(
    model=MODEL_ID,
    config={
        "tools": operation_tools,
        "automatic_function_calling": {"disable": False} # Enabled by default
    }
)

response = chat.send_message(
    "I have 57 cats, each owns 44 mittens, how many mittens is that in total?"
)

print(response.text)
```

----------------------------------------

TITLE: Defining Few-Shot Examples for Gemini ReAct Prompting in Python
DESCRIPTION: This Python code defines a multi-line string variable `examples` containing several few-shot examples formatted in the Thought-Action-Observation (ReAct) pattern. These examples are designed to guide the Gemini model in complex reasoning tasks, demonstrating how to break down questions, perform searches, look up information, and arrive at a final answer.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/examples/Search_Wikipedia_using_ReAct.ipynb#_snippet_6

LANGUAGE: python
CODE:
```
examples = """
Here are some examples.

Question
What is the elevation range for the area that the eastern sector of the Colorado orogeny extends into?

Thought 1
I need to search Colorado orogeny, find the area that the eastern sector of the Colorado orogeny extends into, then find the elevation range of the area.

Action 1
<search>Colorado orogeny</search>

Observation 1
The Colorado orogeny was an episode of mountain building (an orogeny) in Colorado and surrounding areas.

Thought 2
It does not mention the eastern sector. So I need to look up eastern sector.

Action 2
<lookup>eastern sector</lookup>

Observation 2
The eastern sector extends into the High Plains and is called the Central Plains orogeny.

Thought 3
The eastern sector of Colorado orogeny extends into the High Plains. So I need to search High Plains and find its elevation range.

Action 3
<search>High Plains</search>

Observation 3
High Plains refers to one of two distinct land regions

Thought 4
I need to instead search High Plains (United States).

Action 4
<search>High Plains (United States)</search>

Observation 4
The High Plains are a subregion of the Great Plains. From east to west, the High Plains rise in elevation from around 1,800 to 7,000 ft (550 to 2,130m).

Thought 5
High Plains rise in elevation from around 1,800 to 7,000 ft, so the answer is 1,800 to 7,000 ft.

Action 5
<finish>1,800 to 7,000 ft</finish>

Question
Musician and satirist Allie Goertz wrote a song about the "The Simpsons" character Milhouse, who Matt Groening named after who?

Thought 1
The question simplifies to "The Simpsons" character Milhouse is named after who. I only need to search Milhouse and find who it is named after.

Action 1
<search>Milhouse</search>

Observation 1
Milhouse Mussolini Van Houten is a recurring character in the Fox animated television series The Simpsons voiced by Pamela Hayden and created by Matt Groening.

Thought 2
The paragraph does not tell who Milhouse is named after, maybe I can look up "named after".

Action 2
<lookup>named after</lookup>

Observation 2
Milhouse was named after U.S. president Richard Nixon, whose middle name was Milhous.

Thought 3
Milhouse was named after U.S. president Richard Nixon, so the answer is Richard Nixon.

Action 3
<finish>Richard Nixon</finish>

Question
Which documentary is about Finnish rock groups, Adam Clayton Powell or The Saimaa Gesture?

Thought 1
I need to search Adam Clayton Powell and The Saimaa Gesture, and find which documentary is about Finnish rock groups.

Action 1
<search>Adam Clayton Powell</search>

Observation 1
Could not find [Adam Clayton Powell]. Similar: [’Adam Clayton Powell III’, ’Seventh Avenue (Manhattan)’, ’Adam Clayton Powell Jr. State Office Building’, ’Isabel Washington Powell’, ’Adam Powell’, ’Adam Clayton Powell (film)’, ’Giancarlo Esposito’].

Thought 2
To find the documentary, I can search Adam Clayton Powell (film).

Action 2
<search>Adam Clayton Powell (film)</search>

Observation 2
Adam Clayton Powell is a 1989 American documentary film directed by Richard Kilberg. The film is about the rise and fall of influential African-American politician Adam Clayton Powell Jr.[3][4] It was later aired as part of the PBS series The American Experience.

Thought 3
Adam Clayton Powell (film) is a documentary about an African-American politician, not Finnish rock groups. So the documentary about Finnish rock groups must instead be The Saimaa Gesture.

Action 3
<finish>The Saimaa Gesture</finish>

Question
What profession does Nicholas Ray and Elia Kazan have in common?

Thought 1
I need to search Nicholas Ray and Elia Kazan, find their professions, then find the profession they have in common.

Action 1
<search>Nicholas Ray</search>

Observation 1
Nicholas Ray (born Raymond Nicholas Kienzle Jr., August 7, 1911 - June 16, 1979) was an American film director, screenwriter, and actor best known for the 1955 film Rebel Without a Cause.

Thought 2
Professions of Nicholas Ray are director, screenwriter, and actor. I need to search Elia Kazan next and find his professions.

Action 2
<search>Elia Kazan</search>

Observation 2
Elia Kazan was an American film and theatre director, producer, screenwriter and actor.

Thought 3
Professions of Elia Kazan are director, producer, screenwriter, and actor. So profession Nicholas Ray and Elia Kazan have in common is director, screenwriter, and actor.

Action 3
<finish>director, screenwriter, actor</finish>

Question
Which magazine was started first Arthur’s Magazine or First for Women?

Thought 1
I need to search Arthur’s Magazine and First for Women, and find which was started first.

Action 1
<search>Arthur’s Magazine</search>

Observation 1
Arthur’s Magazine (1844-1846) was an American literary periodical published in Philadelphia in the 19th century.

Thought 2
Arthur’s Magazine was started in 1844. I need to search First for Women next.

Action 2
<search>First for Women</search>

Observation 2
First for Women is a woman’s magazine published by Bauer Media Group in the USA.[1] The magazine was started in 1989.

Thought 3
First for Women was started in 1989. 1844 (Arthur’s Magazine) < 1989 (First for Women), so Arthur’s Magazine was started first.

Action 3
<finish>Arthur’s Magazine</finish>

Question
Were Pavel Urysohn and Leonid Levin known for the same type of work?

Thought 1
I need to search Pavel Urysohn and Leonid Levin, find their types of work, then find if they are the same.

Action 1
<search>Pavel Urysohn</search>

Observation 1
Pavel Samuilovich Urysohn (February 3, 1898 - August 17, 1924) was a Soviet mathematician who is best known for his contributions in dimension theory.

Thought 2
Pavel Urysohn is a mathematician. I need to search Leonid Levin next and find its type of work.

Action 2
<search>Leonid Levin</search>

Observation 2
Leonid Anatolievich Levin is a Soviet-American mathematician and computer scientist.

Thought 3
Leonid Levin is a mathematician and computer scientist. So Pavel Urysohn and Leonid Levin have the same type of work.

Action 3
<finish>yes</finish>

Question
{question}"""
```

----------------------------------------

TITLE: Create and Populate ChromaDB Vector Database
DESCRIPTION: This Python function, 'create_chroma_db', initializes a ChromaDB client and creates a new collection with a specified name. It integrates the 'GeminiEmbeddingFunction' to handle document embeddings. The function then iterates through a list of documents, adding each one to the ChromaDB collection with a unique ID, effectively building the vector database.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/examples/chromadb/Vectordb_with_chroma.ipynb#_snippet_8

LANGUAGE: python
CODE:
```
def create_chroma_db(documents, name):
  chroma_client = chromadb.Client()
  db = chroma_client.create_collection(
      name=name,
      embedding_function=GeminiEmbeddingFunction()
  )

  for i, d in enumerate(documents):
    db.add(
      documents=d,
      ids=str(i)
    )
  return db
```

----------------------------------------

TITLE: Define Functions for Parallel Gemini API Calls
DESCRIPTION: Defines Python functions `power_disco_ball`, `start_music`, and `dim_lights` that simulate controlling a 'house party' environment. These functions are designed to be independent, making them suitable candidates for parallel execution by the Gemini API.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/quickstarts/Function_calling.ipynb#_snippet_15

LANGUAGE: python
CODE:
```
def power_disco_ball(power: bool) -> bool:
    """Powers the spinning disco ball."""
    print(f"Disco ball is {'spinning!' if power else 'stopped.'}")
    return True

def start_music(energetic: bool, loud: bool, bpm: int) -> str:
    """Play some music matching the specified parameters.

    Args:
      energetic: Whether the music is energetic or not.
      loud: Whether the music is loud or not.
      bpm: The beats per minute of the music.

    Returns: The name of the song being played.
    """
    print(f"Starting music! {energetic=} {loud=}, {bpm=}")
    return "Never gonna give you up."


def dim_lights(brightness: float) -> bool:
    """Dim the lights.

    Args:
      brightness: The brightness of the lights, 0.0 is off, 1.0 is full.
    """
    print(f"Lights are now set to {brightness:.0%}")
    return True

house_fns = [power_disco_ball, start_music, dim_lights]
```

----------------------------------------

TITLE: Combining Multiple Tools in a Single Gemini API Request (Python)
DESCRIPTION: This snippet showcases the multi-tool capability of the new Gemini API, allowing the combination of `google_search`, `code_execution`, and `function_declarations` in a single request. The model processes a complex prompt requiring a prime palindrome computation, a web search for earthquake information, and a light control action, demonstrating advanced orchestration of diverse functionalities.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/quickstarts/Get_started_LiveAPI_tools.ipynb#_snippet_17

LANGUAGE: python
CODE:
```
prompt = """\
  Hey, I need you to do three things for me.

  1. Then compute the largest prime plaindrome under 100000.
  2. Then use google search to lookup unformation about the largest earthquake in california the week of Dec 5 2024?
  3. Turn on the lights

  Thanks!
  """

tools = [
    {'google_search': {}},
    {'code_execution': {}},
    {'function_declarations': [turn_on_the_lights, turn_off_the_lights]}
]

await run(prompt, tools=tools, modality="TEXT")
```

----------------------------------------

TITLE: Setting Google API Key from Colab Secrets in Python
DESCRIPTION: This Python snippet retrieves the Google API key from Colab user data secrets and sets it as an environment variable. This is a prerequisite for authenticating API calls, ensuring the key is securely accessed and available for subsequent operations.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/quickstarts/rest/Function_calling_REST.ipynb#_snippet_1

LANGUAGE: python
CODE:
```
import os
from google.colab import userdata

os.environ['GOOGLE_API_KEY'] = userdata.get('GOOGLE_API_KEY')
```

----------------------------------------

TITLE: Setting Google API Key Environment Variable (Python)
DESCRIPTION: This code sets the `GOOGLE_API_KEY` environment variable using a value retrieved from Colab's user data secrets. This is a secure way to provide the API key to subsequent `curl` commands or other API calls without hardcoding it directly in the script.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/quickstarts/rest/Models_REST.ipynb#_snippet_1

LANGUAGE: python
CODE:
```
os.environ['GOOGLE_API_KEY'] = userdata.get('GOOGLE_API_KEY')
```

----------------------------------------

TITLE: Generate Content with Gemini API (Python SDK)
DESCRIPTION: Demonstrates how to make a content generation request to the Gemini API using the Python SDK, displaying the response as Markdown.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/quickstarts/Authentication.ipynb#_snippet_4

LANGUAGE: python
CODE:
```
from IPython.display import Markdown

response = client.models.generate_content(
    model=MODEL_ID,
    contents="Please give me python code to sort a list."
)

display(Markdown(response.text))
```

----------------------------------------

TITLE: Define LangChain RAG Chain for Gemini LLM
DESCRIPTION: This Python snippet defines a Retrieval-Augmented Generation (RAG) chain using LangChain. It combines a retriever for context, a language model prompt, the Gemini LLM, and a string output parser to structure the model's response.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/examples/langchain/Gemini_LangChain_QA_Chroma_WebLoad.ipynb#_snippet_13

LANGUAGE: python
CODE:
```
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | llm_prompt
    | llm
    | StrOutputParser()
)
```

----------------------------------------

TITLE: Generate Content with Google Gemini and Multiple Files
DESCRIPTION: This Python snippet demonstrates how to use the Google Gemini API to generate content. It initializes a `GenerativeModel` with a specific model name and system instruction, then calls `generate_content` with a text prompt and multiple file objects (e.g., blog posts, audio). A timeout is set for the request, and the generated text response is then printed.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/examples/Voice_memos.ipynb#_snippet_9

LANGUAGE: python
CODE:
```
prompt = "Draft my next blog post based on my thoughts in this audio file and these two previous blog posts I wrote."

model = genai.GenerativeModel(model_name="models/gemini-2.5-flash", system_instruction=si)

response = model.generate_content([prompt, blog_file, blog_file2, audio_file],
                                  request_options={"timeout": 600})
print(response.text)
```

----------------------------------------

TITLE: Demonstrating Concurrent Asynchronous Operations with Gemini API in Python
DESCRIPTION: This comprehensive snippet showcases concurrent asynchronous operations using `asyncio` with the Gemini API. It defines two coroutines, one for streaming a Gemini response and another for a non-blocking task, demonstrating how they can run simultaneously without blocking the main execution flow.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/quickstarts/Streaming.ipynb#_snippet_5

LANGUAGE: python
CODE:
```
import asyncio


async def get_response():
    async for chunk in await client.aio.models.generate_content_stream(
        model='gemini-2.0-flash',
        contents='Tell me a story in 500 words.'
    ):
        if chunk.text:
            print(chunk.text)
        print("_" * 80)

async def something_else():
    for i in range(5):
        print("==========not blocked!==========")
        await asyncio.sleep(1)

async def async_demo():
    # Create tasks for concurrent execution
    task1 = asyncio.create_task(get_response())
    task2 = asyncio.create_task(something_else())
    # Wait for both tasks to complete
    await asyncio.gather(task1, task2)

# In IPython notebooks, you can await the coroutine directly:
await async_demo()
```

----------------------------------------

TITLE: Configure Google Gemini API Key in Colab
DESCRIPTION: This code block demonstrates how to securely retrieve the Google API key from Colab's user data secrets and initialize the `google.genai` client. This setup is essential for authenticating and making requests to the Gemini API, enabling access to its generative AI capabilities.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/examples/qdrant/Movie_Recommendation.ipynb#_snippet_2

LANGUAGE: python
CODE:
```
from google.colab import userdata
from google import genai

GOOGLE_API_KEY=userdata.get('GOOGLE_API_KEY')
client = genai.Client(api_key=GOOGLE_API_KEY)
```

----------------------------------------

TITLE: Configure Google Gemini API Key
DESCRIPTION: Retrieves the Google API key from Colab user data and sets it as an environment variable for authentication with the Gemini API, enabling access to Google's generative AI models.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/examples/langchain/Gemini_LangChain_QA_Pinecone_WebLoad.ipynb#_snippet_1

LANGUAGE: python
CODE:
```
import os
from google.colab import userdata
GOOGLE_API_KEY=userdata.get('GOOGLE_API_KEY')

os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
```

----------------------------------------

TITLE: Importing Google Generative AI Package
DESCRIPTION: Imports the `google.generativeai` package, aliased as `genai`, which provides the necessary classes and functions to interact with Google's generative AI models.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/quickstarts/New_in_002.ipynb#_snippet_2

LANGUAGE: python
CODE:
```
import google.generativeai as genai
```

----------------------------------------

TITLE: Extract and Organize Text from Videos with Gemini
DESCRIPTION: This Python snippet shows how to leverage Gemini's reasoning capabilities to transcribe and organize text visible in a video, such as sticky notes. It also prompts the model to generate new ideas based on the extracted information.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/quickstarts/Video_understanding.ipynb#_snippet_9

LANGUAGE: python
CODE:
```
prompt = "Transcribe the sticky notes, organize them and put it in a table. Can you come up with a few more ideas?" # @param ["Transcribe the sticky notes, organize them and put it in a table. Can you come up with a few more ideas?", "Which of those names who fit an AI product that can resolve complex questions using its thinking abilities?"] {"allow-input":true}

video = post_its_video # @param ["trailcam_video", "pottery_video", "post_its_video", "user_study_video"] {"type":"raw","allow-input":true}

response = client.models.generate_content(
    model=MODEL_ID,
    contents=[
        video,
        prompt,
    ]
)

Markdown(response.text)
```

----------------------------------------

TITLE: Batch Generating Text Embeddings with Curl and Gemini API
DESCRIPTION: This `curl` command demonstrates how to efficiently embed multiple text prompts in a single API call using the `batchEmbedContents` method. It sends a JSON array of requests, each specifying the model and content to be embedded.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/quickstarts/rest/Embeddings_REST.ipynb#_snippet_3

LANGUAGE: bash
CODE:
```
%%bash

curl "https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:batchEmbedContents?key=$GOOGLE_API_KEY" \
-H 'Content-Type: application/json' \
-d '{"requests": [{
      "model": "models/text-embedding-004",
      "content": {
      "parts":[{
        "text": "What is the meaning of life?"}]}, },
      {
      "model": "models/text-embedding-004",
      "content": {
      "parts":[{
        "text": "How much wood would a woodchuck chuck?"}]}, },
      {
      "model": "models/text-embedding-004",
      "content": {
      "parts":[{
        "text": "How does the brain work?"}]}, }, ]}' 2> /dev/null | grep -C 5 values
```

----------------------------------------

TITLE: Initialize Gemini API Client with API Key
DESCRIPTION: Initializes the `google.genai` client for interacting with the Gemini API. It retrieves the API key from Colab user data secrets or an environment variable, which is essential for authentication.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/examples/Agents_Function_Calling_Barista_Bot.ipynb#_snippet_2

LANGUAGE: python
CODE:
```
from google import genai
from google.colab import userdata

client = genai.Client(api_key=userdata.get("GOOGLE_API_KEY"))
```

----------------------------------------

TITLE: Retrieve Google API Key from Colab Secrets
DESCRIPTION: Retrieves the Google API key from Colab's user data secrets. This key is essential for authenticating API requests to Gemini models. Users must store their API key in a Colab Secret named `GOOGLE_API_KEY`.
SOURCE: https://github.com/google-gemini/cookbook/blob/main/quickstarts/Video_understanding.ipynb#_snippet_2

LANGUAGE: python
CODE:
```
from google.colab import userdata

GOOGLE_API_KEY=userdata.get('GOOGLE_API_KEY')
```