from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from database_actions import Database
from ai_functionality import get_data_from_website, return_conclusion, convert_data_to_vector
from str_funcs import  convert_output_to_dict, add_br_to_text, replace_tabs_with_spaces

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

CONNECTION_STRING = 'mongodb+srv://vardandavtyan:claglavolox_88888@vcdataset.qnzmfqi.mongodb.net/?retryWrites=true&w=majority&appName=VCDataset'

async def get_similarity(url):

    data_from_website = await get_data_from_website(url)

    data_from_website_dict = convert_output_to_dict(data_from_website)


    db = Database(CONNECTION_STRING, 'VCDataset', 'db')
    db_data = await db.get_all_data()

    vectordb = Database(CONNECTION_STRING, 'VCDataset', 'vectordb')
    vectordb_data = await vectordb.get_all_data()
    vector_data = { "vc name": data_from_website_dict["vc name"] if "vc name" in data_from_website_dict else "Not provided" }
    vector_data["vector"] = await convert_data_to_vector(data_from_website_dict)


    conclusion = await return_conclusion(data_from_website_dict, db_data, vector_data, vectordb_data)

    #update data on database
    await db.add_one(data_from_website_dict)
    await vectordb.add_one(vector_data)

    return {
        "data": replace_tabs_with_spaces(add_br_to_text(data_from_website)),
        "conclusion": add_br_to_text(conclusion)
    }


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/response/")
async def submit_form(request: Request, text: str = Form(...)):

    response = await get_similarity(text)
    return templates.TemplateResponse("result.html", {"request": request, "text": response["data"], "conclusion": response["conclusion"]})
