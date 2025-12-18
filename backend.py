# """
# FastAPI Backend – Reddit Content Generator
# Complete Updated Version with Enhanced Logging
# Version: 5.0.0
# """

# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from typing import Optional
# import requests
# import logging
# import time
# import json

# # --------------------------------------------------
# # Logging Configuration
# # --------------------------------------------------
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(levelname)s:%(name)s:%(message)s'
# )
# logger = logging.getLogger("reddit-api")

# # --------------------------------------------------
# # FastAPI App
# # --------------------------------------------------
# app = FastAPI(
#     title="Reddit Content Generator API",
#     description="AI-powered Reddit content generation with n8n integration",
#     version="5.0.0"
# )

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # --------------------------------------------------
# # n8n Webhook URL Configuration
# # --------------------------------------------------
# # PRODUCTION URL (use this after activation):
# N8N_WEBHOOK_URL = "https://holaprime.app.n8n.cloud/webhook/fe81f232-2bbf-43fb-8dcb-3e31b7cc46a9"

# # TEST URL (fallback for debugging):
# # N8N_WEBHOOK_URL = "# Try test URL instead
# # N8N_WEBHOOK_URL = "https://holaprime.app.n8n.cloud/webhook-test/fe81f232-2bbf-43fb-8dcb-3e31b7cc46a9"

# logger.info(f"=" * 80)
# logger.info(f"Reddit Content Generator API Starting...")
# logger.info(f"Using n8n webhook: {N8N_WEBHOOK_URL}")
# logger.info(f"=" * 80)

# # --------------------------------------------------
# # Request Model
# # --------------------------------------------------
# class AnalysisRequest(BaseModel):
#     """Request model for content generation"""
#     subreddit: str
#     content_type: str          # post | comment
#     style: str                 # auto | casual | technical | formal
#     tone: int                  # 1-5
#     length: str                # Short | Medium | Long
#     context: Optional[str] = ""
#     input_mode: str            # text | image
    
#     # Persona (optional)
#     persona: Optional[str] = "auto"

#     # Text mode fields
#     text_content: Optional[str] = None

#     # Image mode fields
#     image_base64: Optional[str] = None
#     image_name: Optional[str] = None

# # --------------------------------------------------
# # Health Check Endpoint
# # --------------------------------------------------
# @app.get("/")
# def health_check():
#     """Health check endpoint"""
#     return {
#         "service": "Reddit Content Generator API",
#         "status": "running",
#         "version": "5.0.0",
#         "webhook": N8N_WEBHOOK_URL,
#         "features": {
#             "text_input": True,
#             "image_input": True,
#             "rag_enabled": True
#         }
#     }

# # --------------------------------------------------
# # Main Content Generation Endpoint
# # --------------------------------------------------
# @app.post("/analyze-and-generate")
# def analyze_and_generate(req: AnalysisRequest):
#     """
#     Main endpoint for generating Reddit content
#     Supports both text and image inputs
#     """
    
#     start_time = time.time()
    
#     # Log request start
#     logger.info("=" * 80)
#     logger.info(f"NEW REQUEST RECEIVED")
#     logger.info(f"Input Mode: {req.input_mode}")
#     logger.info(f"Subreddit: {req.subreddit}")
#     logger.info(f"Content Type: {req.content_type}")
#     logger.info(f"Style: {req.style} | Tone: {req.tone}/5 | Length: {req.length}")
#     logger.info(f"Persona: {req.persona}")
    
#     # --------------------------------------------------
#     # Validate Input
#     # --------------------------------------------------
#     if req.input_mode not in {"text", "image"}:
#         logger.error(f"Invalid input_mode: {req.input_mode}")
#         raise HTTPException(
#             status_code=400,
#             detail="input_mode must be 'text' or 'image'"
#         )

#     if req.input_mode == "text":
#         if not req.text_content:
#             logger.error("Text mode selected but no text_content provided")
#             raise HTTPException(
#                 status_code=400,
#                 detail="text_content is required for text mode"
#             )
#         logger.info(f"Text content length: {len(req.text_content)} characters")
#         logger.info(f"Text preview: {req.text_content[:100]}...")
    
#     if req.input_mode == "image":
#         if not req.image_base64:
#             logger.error("Image mode selected but no image_base64 provided")
#             raise HTTPException(
#                 status_code=400,
#                 detail="image_base64 is required for image mode"
#             )
#         logger.info(f"Image name: {req.image_name}")
#         logger.info(f"Image base64 length: {len(req.image_base64)} characters")

#     # --------------------------------------------------
#     # Build Payload for n8n
#     # --------------------------------------------------
#     payload = {
#         "subreddit": req.subreddit,
#         "content_type": req.content_type,
#         "style": req.style,
#         "tone": req.tone,
#         "length": req.length,
#         "context": req.context,
#         "input_mode": req.input_mode,
#         "persona": req.persona,
#     }

#     if req.input_mode == "text":
#         payload["text_content"] = req.text_content
#     else:
#         payload["image_base64"] = req.image_base64
#         payload["image_name"] = req.image_name

#     # --------------------------------------------------
#     # Call n8n Webhook
#     # --------------------------------------------------
#     logger.info("-" * 80)
#     logger.info(f"Calling n8n webhook: {N8N_WEBHOOK_URL}")
#     logger.info(f"Payload size: {len(json.dumps(payload))} bytes")
    
#     try:
#         response = requests.post(
#             N8N_WEBHOOK_URL,
#             json=payload,
#             timeout=120,
#             headers={
#                 "Content-Type": "application/json"
#             }
#         )
        
#         # Log response details
#         logger.info("-" * 80)
#         logger.info(f"n8n Response Received")
#         logger.info(f"Status Code: {response.status_code}")
#         logger.info(f"Response Time: {response.elapsed.total_seconds():.2f}s")
#         logger.info(f"Content Type: {response.headers.get('Content-Type', 'N/A')}")
#         logger.info(f"Content Length: {len(response.text)} bytes")
        
#         # Log response body preview
#         response_preview = response.text[:1000] if response.text else "[EMPTY RESPONSE]"
#         logger.info(f"Response Preview (first 1000 chars):")
#         logger.info(response_preview)
        
#         # Check status code
#         if response.status_code != 200:
#             logger.error(f"n8n returned non-200 status code: {response.status_code}")
#             logger.error(f"Full response body: {response.text}")
            
#             raise HTTPException(
#                 status_code=502,
#                 detail={
#                     "error": "n8n workflow error",
#                     "status_code": response.status_code,
#                     "response_body": response.text,
#                     "webhook_url": N8N_WEBHOOK_URL
#                 }
#             )
        
#     except requests.Timeout:
#         logger.error("Request to n8n timed out after 120 seconds")
#         raise HTTPException(
#             status_code=504,
#             detail="n8n workflow timeout - processing took too long"
#         )
    
#     except requests.ConnectionError as e:
#         logger.error(f"Connection error to n8n: {str(e)}")
#         raise HTTPException(
#             status_code=503,
#             detail=f"Cannot connect to n8n: {str(e)}"
#         )
    
#     except requests.RequestException as e:
#         logger.error(f"Request to n8n failed: {str(e)}")
#         raise HTTPException(
#             status_code=503,
#             detail=f"n8n request failed: {str(e)}"
#         )

#     # --------------------------------------------------
#     # Parse n8n Response
#     # --------------------------------------------------
#     logger.info("-" * 80)
#     logger.info("Parsing n8n response...")
    
#     try:
#         n8n_json = response.json()
#         logger.info(f"✓ JSON parsed successfully")
#         logger.info(f"Response keys: {list(n8n_json.keys())}")
#         logger.info(f"Full parsed JSON: {json.dumps(n8n_json, indent=2)[:500]}...")
        
#     except ValueError as e:
#         logger.error(f"Failed to parse JSON from n8n response")
#         logger.error(f"Parse error: {str(e)}")
#         logger.error(f"Raw response text: {response.text[:500]}")
        
#         raise HTTPException(
#             status_code=502,
#             detail={
#                 "error": "Invalid JSON response from n8n",
#                 "parse_error": str(e),
#                 "raw_response": response.text[:500]
#             }
#         )

#     # --------------------------------------------------
#     # Extract Generated Content
#     # --------------------------------------------------
#     logger.info("-" * 80)
#     logger.info("Extracting generated content...")
    
#     if "generated_content" not in n8n_json:
#         logger.error("Response is missing 'generated_content' field")
#         logger.error(f"Available fields: {list(n8n_json.keys())}")
#         logger.error(f"Full response: {json.dumps(n8n_json, indent=2)}")
        
#         raise HTTPException(
#             status_code=502,
#             detail={
#                 "error": "n8n response missing 'generated_content' field",
#                 "available_fields": list(n8n_json.keys()),
#                 "full_response": n8n_json
#             }
#         )

#     generated_content = n8n_json["generated_content"]
    
#     # Validate content
#     if not isinstance(generated_content, str):
#         logger.error(f"generated_content is not a string: {type(generated_content)}")
#         raise HTTPException(
#             status_code=502,
#             detail=f"Invalid generated_content type: {type(generated_content)}"
#         )
    
#     if not generated_content.strip():
#         logger.error("generated_content is empty or whitespace only")
#         raise HTTPException(
#             status_code=502,
#             detail="Empty generated_content from n8n"
#         )

#     logger.info(f"✓ Generated content extracted successfully")
#     logger.info(f"Content length: {len(generated_content)} characters")
#     logger.info(f"Word count: {len(generated_content.split())} words")
#     logger.info(f"Content preview: {generated_content[:200]}...")

#     # --------------------------------------------------
#     # Build Success Response
#     # --------------------------------------------------
#     processing_time = round(time.time() - start_time, 2)
    
#     response_data = {
#         "generated_content": generated_content,
#         "metadata": {
#             "subreddit": req.subreddit,
#             "content_type": req.content_type,
#             "input_mode": req.input_mode,
#             "persona": req.persona,
#             "style": req.style,
#             "tone": req.tone,
#             "length": req.length,
#             "word_count": len(generated_content.split()),
#             "character_count": len(generated_content),
#             "processing_time_sec": processing_time,
#             **n8n_json.get("metadata", {})
#         },
#     }
    
#     # Log success
#     logger.info("-" * 80)
#     logger.info(f"✓ REQUEST COMPLETED SUCCESSFULLY")
#     logger.info(f"Total processing time: {processing_time}s")
#     logger.info(f"Generated {len(generated_content)} chars, {len(generated_content.split())} words")
#     logger.info("=" * 80)
    
#     return response_data

# # --------------------------------------------------
# # Global Exception Handler
# # --------------------------------------------------
# @app.exception_handler(Exception)
# async def global_exception_handler(request, exc):
#     """Catch-all exception handler"""
#     logger.error("=" * 80)
#     logger.error(f"UNCAUGHT EXCEPTION: {type(exc).__name__}")
#     logger.error(f"Error message: {str(exc)}")
#     logger.error("=" * 80, exc_info=True)
    
#     return {
#         "error": "Internal server error",
#         "type": type(exc).__name__,
#         "detail": str(exc)
#     }

# # --------------------------------------------------
# # Startup Event
# # --------------------------------------------------
# @app.on_event("startup")
# async def startup_event():
#     """Log startup information"""
#     logger.info("=" * 80)
#     logger.info("✓ Reddit Content Generator API Started")
#     logger.info(f"✓ Version: 5.0.0")
#     logger.info(f"✓ Webhook URL: {N8N_WEBHOOK_URL}")
#     logger.info(f"✓ Server: http://0.0.0.0:8000")
#     logger.info(f"✓ Docs: http://0.0.0.0:8000/docs")
#     logger.info("=" * 80)

# # --------------------------------------------------
# # Run Server
# # --------------------------------------------------
# if __name__ == "__main__":
#     import uvicorn
    
#     logger.info("Starting server...")
#     uvicorn.run(
#         app, 
#         host="0.0.0.0", 
#         port=8000,
#         log_level="info"
#     )
# ======above is for local==================
# ===below is for gcp=======================
"""
FastAPI Backend – Reddit Content Generator
Cloud Run Ready Version with Enhanced Logging
Version: 5.0.0
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import requests
import logging
import time
import json
import os

# --------------------------------------------------
# Logging Configuration
# --------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger("reddit-api")

# --------------------------------------------------
# FastAPI App
# --------------------------------------------------
app = FastAPI(
    title="Reddit Content Generator API",
    description="AI-powered Reddit content generation with n8n integration",
    version="5.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# n8n Webhook URL Configuration
# --------------------------------------------------
N8N_WEBHOOK_URL = os.environ.get(
    "N8N_WEBHOOK_URL",
    "https://holaprime.app.n8n.cloud/webhook/fe81f232-2bbf-43fb-8dcb-3e31b7cc46a9"
)

logger.info(f"=" * 80)
logger.info(f"Reddit Content Generator API Starting...")
logger.info(f"Using n8n webhook: {N8N_WEBHOOK_URL}")
logger.info(f"=" * 80)

# --------------------------------------------------
# Request Model
# --------------------------------------------------
class AnalysisRequest(BaseModel):
    """Request model for content generation"""
    subreddit: str
    content_type: str          # post | comment
    style: str                 # auto | casual | technical | formal
    tone: int                  # 1-5
    length: str                # Short | Medium | Long
    context: Optional[str] = ""
    input_mode: str            # text | image
    
    # Persona (optional)
    persona: Optional[str] = "auto"

    # Text mode fields
    text_content: Optional[str] = None

    # Image mode fields
    image_base64: Optional[str] = None
    image_name: Optional[str] = None

# --------------------------------------------------
# Health Check Endpoint
# --------------------------------------------------
@app.get("/")
def health_check():
    """Health check endpoint"""
    return {
        "service": "Reddit Content Generator API",
        "status": "running",
        "version": "5.0.0",
        "webhook": N8N_WEBHOOK_URL,
        "features": {
            "text_input": True,
            "image_input": True,
            "rag_enabled": True
        }
    }

# --------------------------------------------------
# Main Content Generation Endpoint
# --------------------------------------------------
@app.post("/analyze-and-generate")
def analyze_and_generate(req: AnalysisRequest):
    """
    Main endpoint for generating Reddit content
    Supports both text and image inputs
    """
    
    start_time = time.time()
    
    # Log request start
    logger.info("=" * 80)
    logger.info(f"NEW REQUEST RECEIVED")
    logger.info(f"Input Mode: {req.input_mode}")
    logger.info(f"Subreddit: {req.subreddit}")
    logger.info(f"Content Type: {req.content_type}")
    logger.info(f"Style: {req.style} | Tone: {req.tone}/5 | Length: {req.length}")
    logger.info(f"Persona: {req.persona}")
    
    # --------------------------------------------------
    # Validate Input
    # --------------------------------------------------
    if req.input_mode not in {"text", "image"}:
        logger.error(f"Invalid input_mode: {req.input_mode}")
        raise HTTPException(
            status_code=400,
            detail="input_mode must be 'text' or 'image'"
        )

    if req.input_mode == "text":
        if not req.text_content:
            logger.error("Text mode selected but no text_content provided")
            raise HTTPException(
                status_code=400,
                detail="text_content is required for text mode"
            )
        logger.info(f"Text content length: {len(req.text_content)} characters")
        logger.info(f"Text preview: {req.text_content[:100]}...")
    
    if req.input_mode == "image":
        if not req.image_base64:
            logger.error("Image mode selected but no image_base64 provided")
            raise HTTPException(
                status_code=400,
                detail="image_base64 is required for image mode"
            )
        logger.info(f"Image name: {req.image_name}")
        logger.info(f"Image base64 length: {len(req.image_base64)} characters")

    # --------------------------------------------------
    # Build Payload for n8n
    # --------------------------------------------------
    payload = {
        "subreddit": req.subreddit,
        "content_type": req.content_type,
        "style": req.style,
        "tone": req.tone,
        "length": req.length,
        "context": req.context,
        "input_mode": req.input_mode,
        "persona": req.persona,
    }

    if req.input_mode == "text":
        payload["text_content"] = req.text_content
    else:
        payload["image_base64"] = req.image_base64
        payload["image_name"] = req.image_name

    # --------------------------------------------------
    # Call n8n Webhook
    # --------------------------------------------------
    logger.info("-" * 80)
    logger.info(f"Calling n8n webhook: {N8N_WEBHOOK_URL}")
    logger.info(f"Payload size: {len(json.dumps(payload))} bytes")
    
    try:
        response = requests.post(
            N8N_WEBHOOK_URL,
            json=payload,
            timeout=120,
            headers={
                "Content-Type": "application/json"
            }
        )
        
        # Log response details
        logger.info("-" * 80)
        logger.info(f"n8n Response Received")
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Response Time: {response.elapsed.total_seconds():.2f}s")
        logger.info(f"Content Type: {response.headers.get('Content-Type', 'N/A')}")
        logger.info(f"Content Length: {len(response.text)} bytes")
        
        # Log response body preview
        response_preview = response.text[:1000] if response.text else "[EMPTY RESPONSE]"
        logger.info(f"Response Preview (first 1000 chars):")
        logger.info(response_preview)
        
        # Check status code
        if response.status_code != 200:
            logger.error(f"n8n returned non-200 status code: {response.status_code}")
            logger.error(f"Full response body: {response.text}")
            
            raise HTTPException(
                status_code=502,
                detail={
                    "error": "n8n workflow error",
                    "status_code": response.status_code,
                    "response_body": response.text,
                    "webhook_url": N8N_WEBHOOK_URL
                }
            )
        
    except requests.Timeout:
        logger.error("Request to n8n timed out after 120 seconds")
        raise HTTPException(
            status_code=504,
            detail="n8n workflow timeout - processing took too long"
        )
    
    except requests.ConnectionError as e:
        logger.error(f"Connection error to n8n: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Cannot connect to n8n: {str(e)}"
        )
    
    except requests.RequestException as e:
        logger.error(f"Request to n8n failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"n8n request failed: {str(e)}"
        )

    # --------------------------------------------------
    # Parse n8n Response
    # --------------------------------------------------
    logger.info("-" * 80)
    logger.info("Parsing n8n response...")
    
    try:
        n8n_json = response.json()
        logger.info(f"✓ JSON parsed successfully")
        logger.info(f"Response keys: {list(n8n_json.keys())}")
        logger.info(f"Full parsed JSON: {json.dumps(n8n_json, indent=2)[:500]}...")
        
    except ValueError as e:
        logger.error(f"Failed to parse JSON from n8n response")
        logger.error(f"Parse error: {str(e)}")
        logger.error(f"Raw response text: {response.text[:500]}")
        
        raise HTTPException(
            status_code=502,
            detail={
                "error": "Invalid JSON response from n8n",
                "parse_error": str(e),
                "raw_response": response.text[:500]
            }
        )

    # --------------------------------------------------
    # Extract Generated Content
    # --------------------------------------------------
    logger.info("-" * 80)
    logger.info("Extracting generated content...")
    
    if "generated_content" not in n8n_json:
        logger.error("Response is missing 'generated_content' field")
        logger.error(f"Available fields: {list(n8n_json.keys())}")
        logger.error(f"Full response: {json.dumps(n8n_json, indent=2)}")
        
        raise HTTPException(
            status_code=502,
            detail={
                "error": "n8n response missing 'generated_content' field",
                "available_fields": list(n8n_json.keys()),
                "full_response": n8n_json
            }
        )

    generated_content = n8n_json["generated_content"]
    
    # Validate content
    if not isinstance(generated_content, str):
        logger.error(f"generated_content is not a string: {type(generated_content)}")
        raise HTTPException(
            status_code=502,
            detail=f"Invalid generated_content type: {type(generated_content)}"
        )
    
    if not generated_content.strip():
        logger.error("generated_content is empty or whitespace only")
        raise HTTPException(
            status_code=502,
            detail="Empty generated_content from n8n"
        )

    logger.info(f"✓ Generated content extracted successfully")
    logger.info(f"Content length: {len(generated_content)} characters")
    logger.info(f"Word count: {len(generated_content.split())} words")
    logger.info(f"Content preview: {generated_content[:200]}...")

    # --------------------------------------------------
    # Build Success Response
    # --------------------------------------------------
    processing_time = round(time.time() - start_time, 2)
    
    response_data = {
        "generated_content": generated_content,
        "metadata": {
            "subreddit": req.subreddit,
            "content_type": req.content_type,
            "input_mode": req.input_mode,
            "persona": req.persona,
            "style": req.style,
            "tone": req.tone,
            "length": req.length,
            "word_count": len(generated_content.split()),
            "character_count": len(generated_content),
            "processing_time_sec": processing_time,
            **n8n_json.get("metadata", {})
        },
    }
    
    # Log success
    logger.info("-" * 80)
    logger.info(f"✓ REQUEST COMPLETED SUCCESSFULLY")
    logger.info(f"Total processing time: {processing_time}s")
    logger.info(f"Generated {len(generated_content)} chars, {len(generated_content.split())} words")
    logger.info("=" * 80)
    
    return response_data

# --------------------------------------------------
# Global Exception Handler
# --------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Catch-all exception handler"""
    logger.error("=" * 80)
    logger.error(f"UNCAUGHT EXCEPTION: {type(exc).__name__}")
    logger.error(f"Error message: {str(exc)}")
    logger.error("=" * 80, exc_info=True)
    
    return {
        "error": "Internal server error",
        "type": type(exc).__name__,
        "detail": str(exc)
    }

# --------------------------------------------------
# Run Server (Cloud Run Compatible)
# --------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment variable (Cloud Run uses PORT)
    port = int(os.environ.get("PORT", 8080))
    
    logger.info(f"Starting server on port {port}...")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level="info"
    )
    