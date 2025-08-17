import os

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from fastapi.responses import PlainTextResponse, HTMLResponse, FileResponse

from summarizer.summarizer import get_summary, edit_summary_llm
from utils.helpers import delete_directory, save_raw, save_summary, read_summary, send_summary_email

app = FastAPI(
    title="Document Summarization API",
    description="An API to upload documents, generate summaries, and edit them."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class EditRequest(BaseModel):
    prompt: str

class EmailRequest(BaseModel):
    email: EmailStr



@app.post("/summary", summary="Generate summary from uploaded file")
async def generate_summary_from_file(file: UploadFile = File(...)):
    """
    Accepts a file (txt, pdf, docx), extracts its content, generates a summary,
    and saves it to `doc/summary.txt`.
    """
    allowed = {"text/plain", "application/pdf",
               "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400,
                            detail=f"File type '{file.content_type}' not supported. Allowed types: {allowed}")

    # Start fresh
    delete_directory()

    # Save uploaded file and get its content
    content = save_raw(file)

    # *** LOGIC FIX: Call the async summarizer, not the file saver ***
    summary = await get_summary(content)

    # Save the generated summary to disk
    save_summary(summary)

    return {"message": "Summary generated successfully", "summary": summary}


@app.post("/edit-summary", summary="Edit the existing summary with a prompt")
async def edit_summary(request: EditRequest):
    """
    Reads the current summary, applies an editing instruction from the user,
    saves the new version, and returns it.
    """
    try:
        existing_summary = read_summary()
    except FileNotFoundError:
        raise HTTPException(status_code=404,
                            detail="No summary found to edit. Please upload a file to generate one first.")

    new_summary = await edit_summary_llm(
        existing_summary=existing_summary,
        edit_prompt=request.prompt
    )

    # Overwrite the old summary with the new one
    save_summary(new_summary)

    return {"message": "Summary edited successfully", "summary": new_summary}


@app.get("/download-txt", summary="Download the current summary as a .txt file")
def download_txt():
    """
    Retrieves the `summary.txt` file and returns it for download.
    """
    try:
        summary_content = read_summary()
        # The header makes the browser treat this response as a file download
        headers = {'Content-Disposition': 'attachment; filename="summary.txt"'}
        return PlainTextResponse(content=summary_content, headers=headers)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/send-summary", summary="Send the summary to an email address")
async def send_email_endpoint(request: EmailRequest):
    """
    Takes a recipient's email address, reads the latest summary,
    and sends it as an email.
    """
    try:
        await send_summary_email(request.email)
        return {"message": f"Summary successfully sent to {request.email}"}
    except FileNotFoundError as e:
        # If read_summary() fails because the file isn't there
        raise HTTPException(status_code=404, detail=str(e))
    except (ValueError, ConnectionRefusedError, IOError) as e:
        # If email configuration is wrong or sending fails
        # Return a 500 error because it's a server-side issue
        raise HTTPException(status_code=500, detail=f"Email server error: {str(e)}")
    except Exception as e:
        # A final catch-all for any other unexpected errors
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@app.get("/", response_class=HTMLResponse, summary="Serve the main HTML frontend")
async def serve_homepage():
    """
    Serves the single-page HTML application from the /frontend directory.
    """
    return FileResponse( "index.html")