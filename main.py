from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.document_loaders import WebBaseLoader
from chains import Chain
from portfolio import Portfolio
from utils import clean_text

app = FastAPI()

# Configure CORS to allow specific origins (adjust as necessary for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change "*" to specific origins if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chain = Chain()
portfolio = Portfolio()


@app.get("/generate_email/")
async def generate_email(url: str):
    """Generate emails based on job postings from the provided URL."""
    try:
        # Load and clean data from the provided URL
        loader = WebBaseLoader([url])
        data = clean_text(loader.load().pop().page_content)

        # Load portfolio and extract job information
        portfolio.load_portfolio()
        jobs = chain.extract_jobs(data)

        emails = []
        for job in jobs:
            skills = job.get('skills', [])
            links = portfolio.query_links(skills)
            email = chain.write_mail(job, links)
            emails.append(email)

        return {"emails": emails}

    except Exception as e:
        # Raise HTTP 500 error with details if an exception occurs
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    # Run the application on host 0.0.0.0 and port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
