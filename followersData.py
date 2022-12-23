import requests
bearer_token = ""


def create_url(id):
    user_id = id
    return "https://api.twitter.com/2/users/{}/".format(user_id)

def get_params():
    return {"user.fields": "created_at,public_metrics"}


def bearer_oauth(r):
    global bearer_token
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2UserTweetsPython"
    return r


def connect_to_endpoint(url, params):
    response = requests.request("GET", url, auth=bearer_oauth, params=params)
    print(response.status_code)
    if response.status_code != 200: 
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()


def main(id,bearerToken):
    global bearer_token 
    bearer_token = bearerToken
    url = create_url(id)
    params = get_params()
    json_response = connect_to_endpoint(url, params)
    return json_response['data']['public_metrics']['followers_count']