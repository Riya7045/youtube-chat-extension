from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend_wrapped import generate_answer
import asyncio
import logging
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
logger = logging.getLogger(__name__)



# Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class VideoChatRequest(BaseModel):
    query: str
    vidDetails: str

class VideoChatResponse(BaseModel):
    answer: str




@app.get("/")
async def root():
    return {"message": "API is running"}


@app.post("/videochat", response_model=VideoChatResponse)
async def videochat_endpoint(request: VideoChatRequest) -> VideoChatResponse:
    try:
        # Direct call (synchronous)
        answer = generate_answer({
            "query": request.query,
            "vidDetails": request.vidDetails
        })
        return VideoChatResponse(answer=answer)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in /videochat: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# uvicorn server:app --reload
