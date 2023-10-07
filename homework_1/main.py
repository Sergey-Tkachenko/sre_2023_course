import datetime
import json

import yaml
from requests import Session

HOST = "http://localhost:8080"
DEFAULT_HEADERS = {"Content-Type": "application/json; charset=utf-8"}


def get_token(session: Session):
    url = f"{HOST}/login"

    response = session.post(url=url, headers=DEFAULT_HEADERS, data={"username": "root", "password": "123"})

    assert response.status_code == 200

    return response.json()["csrf_token"]


def create_team(session: Session, name: str, scheduling_timezone: str, email: str, slack_channel: str, **kwargs):
    url = f"{HOST}/api/v0/teams"

    data = {"name": name, "scheduling_timezone": scheduling_timezone, "email": email, "slack_channel": slack_channel}

    return session.post(url=url, data=json.dumps(data))


def create_user(session: Session, name: str):
    url = f"{HOST}/api/v0/users"

    data = {"name": name}

    response = session.post(url, headers=DEFAULT_HEADERS, data=json.dumps(data))

    return response


def update_user(session: Session, name: str, full_name: str, phone_number: str, email: str, **kwargs):
    url = f"{HOST}/api/v0/users"

    data = {
        "contacts": {"call": phone_number, "email": email},
        "full_name": full_name,
    }

    response = session.put(f"{url}/{name}", headers=DEFAULT_HEADERS, data=json.dumps(data))

    return response


def pin_user_to_team(session: Session, user_name: str, team_name: str):
    url = f"{HOST}/api/v0/teams/{team_name}/users"

    data = {"name": user_name}

    return session.post(url, headers=DEFAULT_HEADERS, data=json.dumps(data))


def create_event(session: Session, name: str, team: str, role: str, date_str: str):
    url = f"{HOST}/api/v0/events"

    start_dt = datetime.datetime.strptime(date_str, "%d/%m/%Y")
    end_dt = start_dt + datetime.timedelta(hours=24)

    data = {
        "start": int(start_dt.timestamp()),
        "end": int(end_dt.timestamp()),
        "user": name,
        "team": team,
        "role": role,
    }

    return session.post(url, headers=DEFAULT_HEADERS, data=json.dumps(data))


if __name__ == "__main__":
    with open("homework_1/schema.yaml", "r") as file:
        content = yaml.safe_load(file)["teams"]

    with Session() as session:
        token = get_token(session)

        session.headers["x-csrf-token"] = token

        for team_data in content:
            create_team(session, **team_data).content

            for user_data in team_data["users"]:
                create_user(session, name=user_data["name"])
                update_user(session, **user_data).status_code
                pin_user_to_team(session, user_data["name"], team_data["name"]).content

                for event_data in user_data["duty"]:
                    create_event(session, user_data["name"], team_data["name"], event_data["role"], event_data["date"])
