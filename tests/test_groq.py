from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

# Get the key and model
api_key = os.getenv("GROQ_API_KEY")
model_name = os.getenv("GROQ_MODEL")

if not api_key:
    raise ValueError("❌ GROQ_API_KEY not found! Please check your .env file.")

# Initialize the LLM
llm = ChatGroq(
    api_key=api_key,
    model=model_name,
    temperature=0.7,max_tokens=3000 # creativity level (0=precise, 1=creative)
)

# Send a sample prompt
prompt = "Summarize this paragraph: Bypassing SSRF filters via open redirection It is sometimes possible to bypass filter-based defenses by exploiting an open redirection vulnerability. In the previous example, imagine the user-submitted URL is strictly validated to prevent malicious exploitation of the SSRF behavior. However, the application whose URLs are allowed contains an open redirection vulnerability. Provided the API used to make the back-end HTTP request supports redirections, you can construct a URL that satisfies the filter and results in a redirected request to the desired back-end target. For example, the application contains an open redirection vulnerability in which the following URL: /product/nextProduct?currentProductId=6&path=http://evil-user.net returns a redirection to: http://evil-user.net You can leverage the open redirection vulnerability to bypass the URL filter, and exploit the SSRF vulnerability as follows: "

response = llm.invoke(prompt)

# Print the output
print("\n=== ✅ Groq Model Test ===")
print(f"Prompt: {prompt}\n")
print("Response:")
print(response.content)
print("\n===========================")
