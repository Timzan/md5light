import hashlib
import smtplib
import uuid
from email.mime.text import MIMEText

import yaml
import requests_async
import uvicorn
from fastapi import FastAPI, BackgroundTasks
from starlette.responses import Response
from starlette.status import HTTP_200_OK, HTTP_201_CREATED, \
    HTTP_202_ACCEPTED, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR

import models
from database import database, checksums

app = FastAPI()
with open("data.yml", "r") as stream:
    data = yaml.load(stream, Loader=yaml.FullLoader)

FROM_EMAIL = data['user']['email']
PASSWORD = data['user']['password']
SERVER = "smtp.gmail.com"
PORT = 587
BUFF_SIZE = 131072


def email_sender(server, port, sender, password,  receiver, msg):
    with smtplib.SMTP(server, port) as server:
        server.ehlo()
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receiver, msg)


async def md5_checker(url, status_id, email=None):
    hash_md5 = hashlib.md5()
    try:
        r = await requests_async.get(url)
        async for data in r.iter_content(BUFF_SIZE):
            hash_md5.update(data)
        md5_checksum = hash_md5.hexdigest()
        if email:
            email_body = "{}, {}".format(url, md5_checksum)
            msg = MIMEText(email_body, 'plain')
            msg['Subject'] = 'md5'
            msg['From'] = FROM_EMAIL
            msg['To'] = email
            email_sender(SERVER, PORT, FROM_EMAIL, PASSWORD, email, msg.as_string())
        checksum_query = checksums.update().where(checksums.c.status_id == status_id).values(checksum=md5_checksum,
                                                                                             status="done")
        await database.execute(checksum_query)
    except Exception as e:
        print(e)
        query = checksums.update().where(checksums.c.status_id == status_id).values(status="failed")
        await database.execute(query)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.post("/submit", response_model=models.StatusResponse, status_code=HTTP_201_CREATED)
async def create_status(checksum: models.ChecksumIn, tasks: BackgroundTasks):
    status_id = str(uuid.uuid4())
    status_id_query = checksums.insert().values(url=checksum.url, email=checksum.email,
                                                status_id=status_id, status="running")
    await database.execute(status_id_query)
    tasks.add_task(md5_checker, url=checksum.url, status_id=status_id, email=checksum.email)
    return {"status_id": status_id}


@app.get("/check/{status_id}", status_code=HTTP_200_OK)
async def get_status(status_id, response: Response):
    query_status_id = "SELECT status_id FROM checksums WHERE status_id = :status_id"
    result_status_id = await database.fetch_one(query=query_status_id, values={"status_id": status_id})
    if not result_status_id:
        response.status_code = HTTP_404_NOT_FOUND
        return {"status": "Not found"}
    else:
        query = "SELECT url, checksum, status FROM checksums WHERE status_id = :status_id"
        selection = await database.fetch_one(query=query, values={"status_id": status_id})
        if selection[2] == "done":
            result = {"md5_checksum": selection[1], "status": selection[2], "url": selection[0]}
            return result
        elif selection[2] == "running":
            response.status_code = HTTP_202_ACCEPTED
            result = {"status": selection[2]}
            return result
        elif selection[2] == "failed":
            response.status_code = HTTP_500_INTERNAL_SERVER_ERROR
            result = {"status": selection[2]}
            return result


if __name__ == "__main__":
    uvicorn.run(app)

