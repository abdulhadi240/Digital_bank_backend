from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from anthropic import Anthropic
import base64
import requests
from io import BytesIO
from PIL import Image

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Anthropic(
    api_key='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',  # Ensure the API key is correctly set here
)

class UserData(BaseModel):
    profile_pic: str
    cnic_pic: str
    full_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    cnic_number: Optional[str] = None

def fetch_and_convert_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        if image.format == 'PNG':
            buffer = BytesIO()
            image.convert('RGB').save(buffer, format='JPEG')
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
        return base64.b64encode(response.content).decode('utf-8')
    else:
        raise HTTPException(status_code=response.status_code, detail="Error fetching image from URL")

@app.post('/api/v1/kyc')
def check_images(data: UserData):
    base64_image_1 = fetch_and_convert_image(data.profile_pic)
    base64_image_2 = fetch_and_convert_image(data.cnic_pic)

    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""the first image is the profile image of a person . \nName = {data.full_name} , \nDate of birth = {data.date_of_birth}\ncnic = {data.cnic_number}"""
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": base64_image_1
                        }
                    },
                    {
                        "type": "text",
                        "text": "this is the image of identity card of the person . "
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": base64_image_2
                        }
                    },
                    {
                        "type": "text",
                        "text": "You have to check if the person's details are same as on the identity card as told above . plz write the reponse in yes or no only . Donot write anything else."
                    }
                ]
            }
        ]
    )

    return {"response": message.content}

@app.get('/')
def testing():
    return 'hello'
