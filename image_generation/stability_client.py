def _post_v2beta_core(prompt: str, seed: int) -> Optional[bytes]:
    """
    v2beta/core требует multipart/form-data и Accept: image/*
    Отправляем поля как files={(name): (None, value)}.
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "image/*",
    }
    fields = {
        "prompt": prompt,
        "output_format": "png",
        "width": str(WIDTH),
        "height": str(HEIGHT),
        "seed": str(seed),
        "steps": str(STEPS),
        "cfg_scale": str(CFG),
    }
    files = {k: (None, v) for k, v in fields.items()}

    r = requests.post(STAB_URL_V2BETA, headers=headers, files=files, timeout=TIMEOUT)

    if r.status_code == 200 and "image" in r.headers.get("Content-Type","").lower():
        return r.content

    # иногда JSON с base64
    try:
        j = r.json()
        b64 = j.get("image")
        if not b64 and isinstance(j.get("artifacts"), list) and j["artifacts"]:
            b64 = j["artifacts"][0].get("base64")
        if b64:
            import base64
            return base64.b64decode(b64)
    except Exception:
        pass

    # print("v2beta/core debug:", r.status_code, r.text[:200])
    return None
