from fastapi import APIRouter
from model.article import ClaimInput, ClaimVerdictOut
from services.fake_news_service import handle_claim_verification

router = APIRouter()

@router.post("/claim-verdict", response_model=ClaimVerdictOut)
async def claim_verdict(input: ClaimInput):
    verdict, explanation = await handle_claim_verification(input.claim)
    return ClaimVerdictOut(verdict=verdict, explanation=explanation) 