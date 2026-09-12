from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/terms", response_class=HTMLResponse)
async def terms_of_service():
    return "<html><body><h1>Terms of Service</h1><p>Acceptable use guidelines.</p></body></html>"


@router.get("/privacy", response_class=HTMLResponse)
async def privacy_policy():
    return (
        "<html><body><h1>Privacy Policy</h1><p>Data protection rules.</p></body></html>"
    )


@router.get("/dpa", response_class=HTMLResponse)
async def data_processing_agreement():
    return "<html><body><h1>Data Processing Agreement</h1><p>Controller terms.</p></body></html>"
