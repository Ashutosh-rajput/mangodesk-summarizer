import asyncio
import os
import getpass
from typing import List, TypedDict, Literal

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableConfig
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langgraph.graph import StateGraph, START, END

from langchain.chat_models import init_chat_model


def get_documents(content: str) -> List[Document]:
    # This function splits the input content into smaller Document objects.
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=200)
    docs = [Document(page_content=chunk) for chunk in text_splitter.split_text(content)]
    return docs



async def get_summary(content: str, custom_prompt: str = None) -> str:
    print("Check point 1: Starting summary generation.")

    if not os.environ.get("GOOGLE_API_KEY"):
        os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter API key for Google Gemini: ")

    # Initialize the LLM (replace with your actual function if different)
    llm = init_chat_model("gemini-2.0-flash", model_provider="google_genai")
    print("Check point 2: LLM Initialized.")

    # Split the content into manageable documents
    documents = get_documents(content)
    print(f"Check point 3: Content split into {len(documents)} document(s).")

    if not documents:
        return "Content was empty, no summary could be generated."

    # --- ### MODIFICATION 1: Create prompts dynamically ### ---
    # Define a default prompt if no custom one is given
    DEFAULT_SUMMARY_PROMPT = "Write a concise summary of the following"

    # Use the user's custom prompt or fall back to the default
    instruction = custom_prompt if custom_prompt else DEFAULT_SUMMARY_PROMPT

    print(f"Check point 4: Using instruction: '{instruction}'")

    # The prompt for the first document uses the chosen instruction
    summarize_prompt_template = f"{instruction}:\n\n{{context}}"
    initial_summary_prompt = ChatPromptTemplate.from_messages(
        [("human", summarize_prompt_template)]
    )
    initial_summary_chain = initial_summary_prompt | llm | StrOutputParser()

    # The prompt for refining the summary now includes the original instruction
    # to keep the model on track.
    refine_template = """
    Your original instruction was: {instruction}

    You have an existing summary up to a certain point:
    {existing_answer}

    You have the opportunity to refine the existing summary
    (only if needed) with some more context below.
    ------------
    {context}
    ------------

    Given the new context, refine the original summary to incorporate the new information,
    while still following the original instruction: "{instruction}".
    If the context isn't useful, return the original summary.
    Produce the final, refined summary.
    """
    refine_prompt = ChatPromptTemplate.from_template(refine_template)
    refine_summary_chain = refine_prompt | llm | StrOutputParser()

    # --- LangGraph State and Nodes ---
    class State(TypedDict):
        contents: List[str]
        index: int
        summary: str

    async def generate_initial_summary(state: State, config: RunnableConfig):
        print("-> Generating initial summary...")
        summary = await initial_summary_chain.ainvoke(
            {"context": state["contents"][0]},
            config,
        )
        return {"summary": summary, "index": 1}

    async def refine_summary(state: State, config: RunnableConfig):
        print(f"-> Refining summary with document {state['index'] + 1}...")
        content = state["contents"][state["index"]]
        # --- ### MODIFICATION 2: Pass instruction to the refinement chain ### ---
        summary = await refine_summary_chain.ainvoke(
            {
                "existing_answer": state["summary"],
                "context": content,
                "instruction": instruction  # Ensure the model remembers the goal
            },
            config,
        )
        return {"summary": summary, "index": state["index"] + 1}

    def should_refine(state: State) -> Literal["refine_summary", END]:
        if state["index"] >= len(state["contents"]):
            print("-> All documents processed. Ending.")
            return END
        else:
            return "refine_summary"

    # --- Compile and Run the Graph ---
    graph = StateGraph(State)
    graph.add_node("generate_initial_summary", generate_initial_summary)
    graph.add_node("refine_summary", refine_summary)

    graph.add_edge(START, "generate_initial_summary")
    graph.add_conditional_edges("generate_initial_summary", should_refine)
    graph.add_conditional_edges("refine_summary", should_refine)

    app = graph.compile()
    print("Check point 5: Graph compiled.")

    # --- ### MODIFICATION 3: Capture and return the final result ### ---
    final_summary = "Error: Summary generation failed."  # Default value

    async for step in app.astream(
            {"contents": [doc.page_content for doc in documents]},
            stream_mode="values",
    ):
        if "summary" in step:
            final_summary = step["summary"]
            # You can still print intermediate steps for debugging if you want
            # print(f"Intermediate summary received: {final_summary[:150]}...")

    print("Check point 6: Summary generation complete.")
    return final_summary


async def edit_summary_llm(existing_summary: str, edit_prompt: str) -> str:
    if not os.environ.get("GOOGLE_API_KEY"):
        os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter API key for Google Gemini: ")

    # Initialize the LLM (replace with your actual function if different)
    llm = init_chat_model("gemini-2.0-flash", model_provider="google_genai")
    print("Invoking LLM for direct summary editing...")

    # A simple but effective prompt for editing tasks
    template = """
    You are an expert text editor. Your task is to refine an existing text based on a specific instruction.

    **Instruction:** {instruction}

    **Existing Text to Edit:**
    ---
    {existing_text}
    ---

    Produce the new, edited text that follows the instruction. Output only the final text.
    """

    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()

    new_summary = await chain.ainvoke({
        "instruction": edit_prompt,
        "existing_text": existing_summary
    })

    return new_summary


if __name__ == "__main__":
    print("Check point 1")
    content="""Jerry, there is some bad in the best of people and some good in the worst of people. Look for the good!” ~George Chaky, my grandfather
               I was seven when he said that to me. It would later become a guiding principle in my life.
               My grandfather was twenty-one when he came to the US with his older brother, Andrew. Shortly afterward, he married Maria, my grandmother, and they had five children. William, the second youngest, died at the age of seven from an illness.
               One year later they lost all of their savings during the Great Depression of 1929 when many banks closed. Two years afterward, my grandmother died from a stroke at the age of thirty-six.
               As I grew older and learned about the many hardships my grandfather and family of origin had endured, his encouragement to look for the good in people would have a profound impact on me. It fueled a keen interest in trying to understand why people acted the way they did. In retrospect, it also had a lot to do with my becoming a therapist and author."""
    # Make sure you have python-dotenv
    asyncio.run(get_summary(content))
