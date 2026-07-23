from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from recommender import TrekRecommender

app = FastAPI(title="IndiaHikes Trek API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # We'll tighten this later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize recommender once when the server starts
recommender = TrekRecommender()


class RecommendationRequest(BaseModel):
    budget: int
    days: int
    month: str
    experience: str


@app.get("/")
def root():
    return {"status": "API is running"}


@app.post("/recommend")
def recommend(request: RecommendationRequest):

    recommendations = recommender.recommend(
        budget=request.budget,
        days=request.days,
        month=request.month,
        experience=request.experience,
    )

    return recommendations.to_dict(orient="records")