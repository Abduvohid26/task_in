import requests
from json.decoder import JSONDecodeError
from json import decoder, dumps
from phonenumbers import parse, region_code_for_country_code
import pycountry
from urllib.parse import quote_plus


def get_user_id(username, session_id):
    headers = {
        "User-Agent": "Instagram 123.0.0.26.121 Android",
        "x-ig-app-id": "936619743392459"
    }
    cookies = {"sessionid": session_id}
    url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"

    try:
        response = requests.get(url, headers=headers, cookies=cookies)
        response.raise_for_status()
        user_data = response.json()
        user_id = user_data["data"]["user"]["id"]
        return {"id": user_id, "error": None}
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            return {"id": None, "error": "User not found"}
        elif response.status_code == 429:
            return {"id": None, "error": "Rate limit exceeded"}
        return {"id": None, "error": str(http_err)}
    except JSONDecodeError:
        return {"id": None, "error": "Invalid response from server"}
    except Exception as e:
        return {"id": None, "error": str(e)}

def get_user_info(user_id, session_id):
    headers = {
        "User-Agent": "Instagram 123.0.0.26.121 Android",
    }
    cookies = {"sessionid": session_id}
    url = f"https://i.instagram.com/api/v1/users/{user_id}/info/"

    try:
        response = requests.get(url, headers=headers, cookies=cookies)
        response.raise_for_status()
        user_data = response.json()
        user_info = user_data.get("user")
        if not user_info:
            return {"user": None, "error": "User not found"}
        return {"user": user_info, "error": None}
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 429:
            return {"user": None, "error": "Rate limit exceeded"}
        return {"user": None, "error": str(http_err)}
    except JSONDecodeError:
        return {"user": None, "error": "Invalid response from server"}
    except Exception as e:
        return {"user": None, "error": str(e)}

def advanced_lookup(username):
    """
    Post to get obfuscated login information from Instagram.
    Args:
        username (str): The Instagram username for the search.
    Returns:
        dict: Contains 'user' data or error message.
    """
    data = "signed_body=SIGNATURE." + quote_plus(dumps(
        {"q": username, "skip_recovery": "1"},
        separators=(",", ":")
    ))

    try:
        api = requests.post(
            'https://i.instagram.com/api/v1/users/lookup/',
            headers={
                "Accept-Language": "en-US",
                "User-Agent": "Instagram 101.0.0.15.120",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-IG-App-ID": "124024574287414",
                "Accept-Encoding": "gzip, deflate",
                "Host": "i.instagram.com",
                "Connection": "keep-alive",
                "Content-Length": str(len(data))
            },
            data=data
        )        
        return {"user": api.json(), "error": None}
    
    except decoder.JSONDecodeError:
        return {"user": None, "error": "rate limit"}

    except Exception as e:
        return {"user": None, "error": str(e)}

def display_user_info(infos):
    print(f"Informations about     : {infos['username']}")
    print(f"userID                 : {infos['id']}")
    print(f"Full Name              : {infos['full_name']}")
    print(f"Verified               : {infos['is_verified']} | Is business Account : {infos['is_business']}")
    print(f"Is private Account     : {infos['is_private']}")
    print(f"Follower               : {infos['follower_count']} | Following : {infos['following_count']}")
    print(f"Number of posts        : {infos['media_count']}")
    print(f"External url           : {infos['external_url']}")    
    print(f"IGTV posts             : {infos['total_igtv_videos']}")
    print(f"Biography              : {(f'''\n{' ' * 25}''').join(infos.get('biography', '').split('\n'))}")
    
    if infos.get("public_email"):
        print(f"Public Email           : {infos['public_email']}")
    else:
        print("Public Email           : None")
    
    if infos.get("public_phone_number"):
        phonenr = f"+{infos['public_phone_country_code']} {infos['public_phone_number']}"
        try:
            pn = parse(phonenr)
            countrycode = region_code_for_country_code(pn.country_code)
            country = pycountry.countries.get(alpha_2=countrycode)
            phonenr += f" ({country.name})"
        except Exception:
            pass
        print(f"Public Phone number    : {phonenr}")
    else:
        print("Public Phone number    : None")
    
    other_infos = advanced_lookup(infos["username"])
    if other_infos["error"] == "rate limit":
        print("Rate limit, please wait a few minutes before you try again")
    elif "message" in other_infos["user"].keys():
        if other_infos["user"]["message"] == "No users found":
            print("The lookup did not work on this account")
        else:
            print(other_infos["user"]["message"])
    else:
        if other_infos["user"].get("obfuscated_email"):
            print(f"Obfuscated email       : {other_infos['user']['obfuscated_email']}")
        else:
            print("Obfuscated email       : None")
        
        if other_infos["user"].get("obfuscated_phone"): 
            print(f"Obfuscated phone       : {other_infos['user']['obfuscated_phone']}" )
        else:
            print("Obfuscated phone       : None")
    
    print("-" * 24)
    print(f"Profile Picture        : {infos['hd_profile_pic_url_info']['url']}")

def main():
    username = input("Enter the username: ")
    session_id = input("Enter your Instagram session ID: ")

    user_data = get_user_id(username, session_id)
    if user_data["error"]:
        print("Error:", user_data["error"])
        return

    user_id = user_data["id"]
    print("User ID:", user_id)

    user_info = get_user_info(user_id, session_id)
    if user_info["error"]:
        print("Error:", user_info["error"])
        return

    infos = user_info["user"]
    display_user_info(infos)

if __name__ == "__main__":
    main()
