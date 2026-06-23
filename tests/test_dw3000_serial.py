import numpy as np

from uwb_cir.hardware.dw3000_serial import frames_to_matrix, parse_cir_line


def test_parse_json_cir_line():
    frame = parse_cir_line('{"timestamp":"2026-01-01T00:00:00.000Z","cir":[1,2,3],"rx_power":-70}')
    assert frame.timestamp == "2026-01-01T00:00:00.000Z"
    np.testing.assert_allclose(frame.cir, [1.0, 2.0, 3.0])
    assert frame.metadata["rx_power"] == -70


def test_parse_json_complex_pairs_as_magnitude():
    frame = parse_cir_line('{"cir":[[3,4],[5,12]]}')
    np.testing.assert_allclose(frame.cir, [5.0, 13.0])


def test_parse_json_complex_dicts_as_magnitude():
    frame = parse_cir_line('{"cir":[{"real":3,"imag":4},{"i":5,"q":12}]}')
    np.testing.assert_allclose(frame.cir, [5.0, 13.0])


def test_parse_actual_dw3000_cir_serial_rx_line():
    line = (
        '{"frame":5504,"fp_index":47248,"frame_len":12,'
        '"cir":[33,10,31,32,6,21,18,38,26,16,30,16,32,33,15,36,'
        '146,436,384,343,399,373,403,174,65,174,113,410,813,934,678,109]}'
    )
    frame = parse_cir_line(line)

    assert frame.metadata["frame"] == 5504
    assert frame.metadata["fp_index"] == 47248
    assert frame.metadata["frame_len"] == 12
    assert len(frame.cir) == 32
    np.testing.assert_allclose(frame.cir[:4], [33.0, 10.0, 31.0, 32.0])


def test_parse_csv_with_timestamp():
    frame = parse_cir_line("2026-01-01T00:00:00.000Z,1,2,3")
    assert frame.timestamp == "2026-01-01T00:00:00.000Z"
    np.testing.assert_allclose(frame.cir, [1.0, 2.0, 3.0])


def test_frames_to_matrix_pads_and_truncates_to_common_length():
    frames = [
        parse_cir_line("1,2,3"),
        parse_cir_line("4,5,6"),
        parse_cir_line("7,8"),
        parse_cir_line("9,10,11,12"),
    ]
    _, matrix = frames_to_matrix(frames)
    assert matrix.shape == (4, 3)
    np.testing.assert_allclose(matrix[2], [7.0, 8.0, 0.0])
    np.testing.assert_allclose(matrix[3], [9.0, 10.0, 11.0])
