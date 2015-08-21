from datetime import datetime


class RateLimited(Exception):
    def __init__(self, response):
        self.response = response
        message = getattr(response, "content", response)
        try:
            content = response.json()["message"]
            if "message" in content:  # GitHub-style
                message = content["message"]
            else:
                errors = content.get("errors")
                if errors and isinstance(errors, list):  # Twitter-style
                    message = "; ".join(err.get("message") for err in errors)
        except Exception:
            pass
        Exception.__init__(self, message)

    @property
    def reset(self):
        """
        If set, a datetime that indicates when the rate limit will
        be reset. If not set, the reset time is unknown.
        """
        if self.response is None:
            return None
        reset_epoch_str = (
            self.response.headers.get("X-RateLimit-Reset") or
            self.response.headers.get("X-Rate-Limit-Reset")
        )
        if not reset_epoch_str:
            return None
        try:
            reset_epoch = int(reset_epoch_str)
        except Exception:
            return None
        return datetime.fromtimestamp(reset_epoch)
