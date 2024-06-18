# keep this in sync with https://docs.google.com/spreadsheets/d/18shhgdtzI6vHMJUNVPxkfVatAWoa31XTng-kzsvxwik
# benchmark CPU     FPGA    speedup
# ADDMUL	927.3	442.1	2.097
# AES	34.6	188.8	0.183
# SHA3	310.8	115.7	2.686
# GZIP	1.212	368.8	3.286
# NW	971.1	8.6	112.917
# HLS4ML	1150	181.2	5.359
# HLL	1296	224.9	5.763
# HCD	146.9	64.8	2.267
# MD5	11258	74.9	150.307
# FFT	14.5	9.1	1.593
# average	1611.0	167.9	28.6


def addmul():
    return {
        "label": "addmul",
        "mean_speedup": 2.097,
        "run_on_fpga": True,
        "fpga_ratio": 442.1 / (927.3 + 442.1),
        "characterization": {
            "avg_req_per_sec": 1,
            "avg_req_duration": 0.5,
        },
        "priority": True
    }


def aes():
    return {
        "label": "aes",
        "mean_speedup": 0.183,
        "run_on_fpga": True,
        "fpga_ratio": 188.8 / (34.6 + 188.8),
        "characterization": {
            "avg_req_per_sec": 1,
            "avg_req_duration": 0.5,
        },
        "priority": True
    }


def sha3():
    return {
        "label": "sha3",
        "mean_speedup": 2.686,
        "run_on_fpga": True,
        "fpga_ratio": 115.7 / (310.8 + 115.7),
        "characterization": {
            "avg_req_per_sec": 1,
            "avg_req_duration": 120,
        },
        "priority": False
    }


def gzip():
    return {
        "label": "gzip",
        "mean_speedup": 3.286,
        "run_on_fpga": True,
        "fpga_ratio": 368.8 / (1.212 + 368.8),
        "characterization": {
            "avg_req_per_sec": 1,
            "avg_req_duration": 8,
        },
        "priority": False
    }


def nw():
    return {
        "label": "nw",
        "mean_speedup": 112.917,
        "run_on_fpga": True,
        "fpga_ratio": 8.6 / (971.1 + 8.6),
        "characterization": {
            "avg_req_per_sec": 1,
            "avg_req_duration": 1000,
        },
        "priority": True
    }


def hls4ml():
    return {
        "label": "hls4ml",
        "mean_speedup": 5.359,
        "run_on_fpga": True,
        "fpga_ratio": 181.2 / (1150 + 181.2),
        "characterization": {
            "avg_req_per_sec": 1,
            "avg_req_duration": 0.7,
        },
        "priority": False
    }


def hll():
    return {
        "label": "hll",
        "mean_speedup": 5.763,
        "run_on_fpga": True,
        "fpga_ratio": 224.9 / (1296 + 224.9),
        "characterization": {
            "avg_req_per_sec": 1,
            "avg_req_duration": 2,
        },
        "priority": False
    }


def hcd():
    return {
        "label": "hcd",
        "mean_speedup": 2.267,
        "run_on_fpga": True,
        "fpga_ratio": 64.8 / (146.9 + 64.8),
        "characterization": {
            "avg_req_per_sec": 1,
            "avg_req_duration": 5,
        },
        "priority": False
    }


def md5():
    return {
        "label": "md5",
        "mean_speedup": 150.307,
        "run_on_fpga": True,
        "fpga_ratio": 74.9 / (11258 + 74.9),
        "characterization": {
            "avg_req_per_sec": 1,
            "avg_req_duration": 1400,
        },
        "priority": False
    }


def fft():
    return {
        "label": "fft",
        "mean_speedup": 1.593,
        "run_on_fpga": True,
        "fpga_ratio": 9.1 / (14.5 + 9.1),
        "characterization": {
            "avg_req_per_sec": 1,
            "avg_req_duration": 1400,
        },
        "priority": False
    }


def characterized_collection():
    return {
        1: addmul(),
        2: aes(),
        3: sha3(),
        4: gzip(),
        5: nw(),
        6: hls4ml(),
        7: hll(),
        8: hcd(),
        9: md5(),
        10: fft(),
    }
