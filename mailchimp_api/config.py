class Config:
    def __init__(self, dc: str, api_key: str):
        self.base_url = f"https://{dc}.api.mailchimp.com/3.0"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
        }
