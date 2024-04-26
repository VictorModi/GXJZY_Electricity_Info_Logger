# # Ignore the IDE warning "Parameter 'request' value is not used". Do not modify!
import csv
import io
from datetime import timedelta
from enum import IntEnum
from urllib.request import Request

import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from starlette.responses import JSONResponse, StreamingResponse

from electricity import *
from electricity import ElectricityInfo
from student import *

app = FastAPI()
scheduler = BackgroundScheduler()
logging.basicConfig(format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)


class LogType(IntEnum):
    JSON = 0,
    CSV = 1


class ResponseJson(BaseModel):
    status_code: int
    message: str
    data: object

    def __init__(self, status_code, message, data):
        super().__init__(status_code=status_code, message=message, data=data)

    def to_dict(self):
        result = {
            "status_code": self.status_code,
            "message": self.message,
            "data": self.data
        }
        return result


class AccessDenied(Exception):
    def __init__(self, status_code: int = 400, message: str = "", data: dict = None):
        self.status_code = status_code
        self.message = message
        self.data = data or {}
        super().__init__(self.message)


@app.exception_handler(AccessDenied)
async def access_denied_exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content=ResponseJson(exc.status_code, exc.message, exc.data)
                        .to_dict())


@app.exception_handler(HTTPException)
async def exception_handler(request, exc):
    return JSONResponse(status_code=exc.status_code, content=ResponseJson(exc.status_code, exc.detail, {}).to_dict())


@app.exception_handler(status.HTTP_404_NOT_FOUND)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=ResponseJson(
            status_code=status.HTTP_404_NOT_FOUND,
            message="Not Found",
            data={}
        ).dict()
    )


def verify_token(access_token: str = None):
    if access_token != ACCESS_TOKEN:
        raise AccessDenied(status_code=400, message="Invalid access_token", data={})
    return access_token


def get_electricity(cust_id=None) -> ElectricityInfo | None:
    global login_session
    if cust_id is None:
        data = {
            'method': 'getelstudorbandinfo',
            'stuid': 1
        }
        result = json.loads(login_session.send_post("interface/index", data).text)
        cust_id = result["data"][0]["CustId"]
    data = {
        'method': 'geteldorbaseinfo',
        'stuid': 1,
        'xq': 4,
        'custId': cust_id
    }
    try:
        response = login_session.send_post("interface/index", data)
    except (requests.exceptions.ConnectionError, LoginFailedException) as err:
        raise err
    if response is None or response.text == "":
        return
    result = json.loads(response.text)
    if result["state"] != 200:
        logging.error(json.loads(response.text))
        return
    return ElectricityInfo(json.loads(response.text))


def scheduler_job():
    global login_session
    next_run = datetime.now().replace(second=0, microsecond=0) + TIME_INTERVAL
    logging.info("Next run will be at {}.".format(next_run.strftime("%Y-%m-%d %H:%M:%S")))
    scheduler.add_job(scheduler_job, 'date', run_date=next_run)
    try:
        ei = get_electricity(CUST_ID)
    except requests.exceptions.ConnectionError:
        logging.error(f"Failed to connect to {BASE_URL}, this task is discarded.")
        return
    except LoginFailedException:
        logging.error(f"Failed to login to {BASE_URL}, this task is discarded.")
        return
    #  logging.info(ei.to_dict())
    if ei.insert2db() is not None:
        logging.info(f"Data inserted successfully: {ei.to_dict()}")
    else:
        logging.info(f"Same data exists in the database, skipping")


@app.get("/")
# access_token: str = Depends(verify_token)
async def root_endpoint() -> ResponseJson:
    try:
        last_log = get_logs()[0]
        return ResponseJson(200, "", last_log)
    except IndexError:
        return ResponseJson(404, "No logs found", {})


@app.get("/get")
async def get_endpoint(access_token: str = Depends(verify_token), cust_id: int = CUST_ID) -> ResponseJson:
    global login_session
    try:
        response: ElectricityInfo = get_electricity(cust_id)
    except requests.exceptions.ConnectionError as err:
        return ResponseJson(500, f"Failed to connect to {BASE_URL}, this task is discarded.", vars(err))

    if cust_id != CUST_ID:
        result = response.to_dict()
        result["is_inserted"] = False
        return ResponseJson(200, "", result)

    is_inserted = response.insert2db() is not None
    if is_inserted:
        logging.info(f"Data inserted successfully: {response.to_dict()}")
    else:
        logging.info(f"Same data exists in the database, skipping")
    result = response.to_dict()
    result["is_inserted"] = is_inserted
    return ResponseJson(200, "", result)


@app.get("/logs", response_model=None)
async def logs_endpoint(limit: int = 1, reverse: bool = True, file_type: LogType = LogType.JSON,
                        access_token: str = Depends(verify_token)) -> StreamingResponse | ResponseJson:
    logs = get_logs(limit=limit, ascending_order=not reverse)
    if file_type == LogType.CSV:
        csv_content = list_dict_to_csv(logs)
        filename = f"logs_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
        return StreamingResponse(iter([csv_content]), media_type='text/csv',
                                 headers={'Content-Disposition': f'attachment; filename="{filename}"'})
    return ResponseJson(200, "", logs)


@app.post("logs_by_filter")
async def logs_by_filter_endpoint(reverse: bool = True, access_token: str = Depends(verify_token)) -> ResponseJson:
    pass


# @app.get("/set_cookie")
# async def set_cookie_endpoint(cookie: str, access_token: str = Depends(verify_token)) -> ResponseJson:
#     global login_session
#     login_session.cookies["ASP.NET_SessionId"] = cookie
#     login_session.session.cookies["ASP.NET_SessionId"] = cookie
#     return ResponseJson(200, "", login_session.session.cookies.get_dict())
#
#
# @app.get("/get_cookie")
# async def get_cookie_endpoint(access_token: str = Depends(verify_token)) -> ResponseJson:
#     global login_session
#     return ResponseJson(200, "", login_session.session.cookies.get_dict())
#
#
# @app.get("/get_student")
# async def get_student_endpoint(access_token: str = Depends(verify_token)) -> ResponseJson:
#     global login_session
#     return ResponseJson(200, "", login_session.student_user.to)


@app.get("/logout")
async def get_cookie_endpoint(access_token: str = Depends(verify_token)) -> ResponseJson:
    global login_session
    try:
        login_session.logout()
        return ResponseJson(200, "", {})
    except requests.exceptions.ConnectionError as err:
        return ResponseJson(500, f"Failed to connect to {BASE_URL}, this task is discarded.", vars(err))


def list_dict_to_csv(data: list) -> str:
    if data is None or len(data) == 0:
        return ""
    fields = set()
    for row in data:
        fields.update(row.keys())
    fields = sorted(set.union(*[set(row.keys()) for row in data]), key=lambda x: (x != "time", x))
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator='\n')
    writer.writeheader()
    for row in data:
        if isinstance(row["time"], datetime):
            row["time"] = row["time"].strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow(row)
    return output.getvalue()


if __name__ == "__main__":
    try:
        login_session: StudentRequest = StudentRequest(BASE_URL, StudentLoginMethod(SID, PASSWORD))
    except ModuleNotFoundError:
        logging.error("config.py is not configured properly.")
        exit(1)
    scheduler.add_job(scheduler_job)
    scheduler.start()
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_config=LOGGING_CONFIG)
