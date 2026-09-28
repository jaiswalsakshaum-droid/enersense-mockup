import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


ML_ENGINE_URL = "http://127.0.0.1:8000"


def call_ml_engine(endpoint: str, payload: dict):
    """
    Send a request from the main backend to the ML engine.
    """

    url = f"{ML_ENGINE_URL}{endpoint}"

    data = json.dumps(payload).encode("utf-8")

    request = Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:

        with urlopen(request, timeout=30) as response:

            response_data = response.read().decode("utf-8")

            return json.loads(response_data)

    except HTTPError as error:

        try:
            error_body = error.read().decode("utf-8")
            detail = json.loads(error_body)
        except Exception:
            detail = str(error)

        raise RuntimeError(
            f"ML Engine returned HTTP {error.code}: {detail}"
        )

    except URLError as error:

        raise RuntimeError(
            f"ML Engine is unavailable: {error.reason}"
        )

    except Exception as error:

        raise RuntimeError(
            f"ML Engine request failed: {str(error)}"
        )


def analyze_with_ml(payload: dict):

    return call_ml_engine(
        "/analyze",
        payload
    )


def simulate_with_ml(payload: dict):

    return call_ml_engine(
        "/simulate",
        payload
    )


def counterfactual_with_ml(payload: dict):

    return call_ml_engine(
        "/counterfactual",
        payload
    )