from thumbor.ext.filters import _round_corner


def test_transparent_round_corner_edge_is_not_darkened():
    width, height = 100, 100
    data = bytes([255, 255, 255, 255]) * (width * height)

    result = _round_corner.apply(
        1, "RGBA", 30, 30, 255, 255, 255, width, height, data, 1
    )

    pixels = [result[i : i + 4] for i in range(0, len(result), 4)]
    dark_opaque = [
        p for p in pixels if p[3] == 255 and (p[0] < 255 or p[1] < 255 or p[2] < 255)
    ]
    assert dark_opaque == [], (
        f"{len(dark_opaque)} opaque edge pixels were darkened, e.g. {dark_opaque[:3]}"
    )
