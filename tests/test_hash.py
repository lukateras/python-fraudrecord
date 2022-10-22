from fraudrecord.hash import hexdigest


def test_hexdigest():
    # Test vectors from <https://fraudrecord.com/security/>
    data = {
        "John Smith": "ac2c739924bf5d4d9bf5875dc70274fef0fe54cf",
        "john.smith@example.com": "34efd0a968b48cbf9a43ac3e73053e4f343234e4",
        "jsmith@example.net": "2a1ab4a6ed14713d0e26127c1920417e4b193924",
        "11.22.33.44": "f25c0306279af0bd9faf1caf0549daedb3472b7f",
        "+1 000 111 22 33": "3f09086d8d4e4019eb534ce28e6b64c8ef563ec9",
        "+1 555 123 45 67": "d542e4bad3dbb13bcf0e31f484394997cd969b18",
        "example.com": "ff07748b4d4b8f08f21499e078ef792fded46641",
    }

    for s, h in data.items():
        assert hexdigest(s) == h
