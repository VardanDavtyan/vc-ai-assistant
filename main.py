from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from database_actions import Database
from ai_functionality import get_data_from_website, return_conclusion

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

CONNECTION_STRING = 'mongodb+srv://vardandavtyan:claglavolox_88888@vcdataset.qnzmfqi.mongodb.net/?retryWrites=true&w=majority&appName=VCDataset'

db = None
db_data = None


async def get_similarity(url):

    #db = Database(CONNECTION_STRING, 'VCDataset', 'db')

    data_from_website = await get_data_from_website(url)

    #db_data = await db.get_all_data()


    conclusion = await return_conclusion(data_from_website, db_data)

    print(data_from_website)
    #print(data_from_website, conclusion)

    #NO LONGER WORKING, PLEASE IMPLEMENT THE AI FUNCTIONALITY
    #db.add_one(data_from_website)
    return {
        "data": data_from_website,
        "conclusion": conclusion
    }


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    global db, db_data
    db = Database(CONNECTION_STRING, 'VCDataset', 'db')
    #db_data = await db.get_all_data()
    print(db_data)
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/submit/")
async def submit_form(request: Request, text: str = Form(...)):

    response = await get_similarity(text)
    return templates.TemplateResponse("result.html", {"request": request, "text": response["data"], "conclusion": response["conclusion"]})
