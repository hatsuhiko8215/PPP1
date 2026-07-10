import requests
import time
import json
import os
import uuid

class SunoAutoGenerator:
    def __init__(self, auth_token, browser_token, device_id):
        self.api_url = "https://studio-api-prod.suno.com"
        self.headers = {
            "Authorization": f"Bearer {auth_token}",
            "Browser-Token": browser_token,
            "Device-Id": device_id,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "Origin": "https://suno.com",
            "Referer": "https://suno.com/",
        }

    def _make_request(self, method, endpoint, data=None, params=None, max_retries=5):
        url = f"{self.api_url}{endpoint}"
        last_error = None
        for i in range(max_retries):
            try:
                if method == "GET":
                    response = requests.get(url, headers=self.headers, params=params, timeout=30)
                elif method == "POST":
                    response = requests.post(url, headers=self.headers, json=data, timeout=60)

                print(f"[DEBUG] Status: {response.status_code}, Body: {response.text[:500]}")
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError:
                last_error = f"HTTP {response.status_code}: {response.text[:500]}"
                print(f"[DEBUG] Attempt {i+1} failed: {last_error}")
            except Exception as e:
                last_error = str(e)
                print(f"[DEBUG] Attempt {i+1} failed: {last_error}")
            time.sleep(2 ** i)
        raise Exception(f"Failed to make request to {url}: {last_error}")

    def generate_song(self, prompt_tags, title, instrumental=True):
        data = {
            "token": None,
            "generation_type": "TEXT",
            "artist_clip_id": None,
            "artist_end_s": None,
            "artist_start_s": None,
            "continue_at": None,
            "continue_clip_id": None,
            "continued_aligned_prompt": None,
            "cover_clip_id": None,
            "cover_end_s": None,
            "cover_start_s": None,
            "make_instrumental": instrumental,
            "metadata": {
                "web_client_pathname": "/create",
                "is_max_mode": False,
                "is_mumble": False,
                "create_mode": "custom"
            },
            "mv": "chirp-fenix",
            "negative_tags": "",
            "override_fields": [],
            "persona_id": None,
            "prompt": "",
            "tags": prompt_tags,
            "title": title,
            "token_provider": None,
            "transaction_uuid": str(uuid.uuid4()),
            "user_uploaded_images_b64": None
        }
        response_data = self._make_request("POST", "/api/generate/v2-web/", data=data)
        clips = response_data.get("clips", [])
        return [item["id"] for item in clips if "id" in item]

    def get_song_info(self, song_id):
        response_data = self._make_request("GET", f"/api/feed/v2?ids={song_id}")
        clips = response_data.get("clips", [])
        if clips:
            return clips[0]
        return None

    def download_song(self, song_url, output_path):
        response = requests.get(song_url, stream=True, timeout=120)
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return output_path

    def wait_for_song_completion(self, generate_ids, timeout=300):
        start_time = time.time()
        completed_songs = []
        while time.time() - start_time < timeout and len(completed_songs) < len(generate_ids):
            for song_id in generate_ids:
                if song_id in [s["id"] for s in completed_songs]:
                    continue
                song_info = self.get_song_info(song_id)
                if song_info and song_info.get("status") in ("complete", "streaming"):
                    completed_songs.append(song_info)
            time.sleep(10)
        return completed_songs
