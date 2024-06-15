def addmul():
    return {
        # an average function that benefits somewhat from being on the FPGA
        "label": "addmul-1024",
        "mean_speedup": 0.06,
        "run_on_fpga": True,
        "fpga_ratio": 0.5,
        "characterization": {
            "avg_req_per_sec": 1,
            "avg_req_duration": 0.5,
        },
        "priority": 3
    }


def aes128ecb4k():
    return {
        # an average function that benefits somewhat from being on the FPGA
        "label": "aes128ecb-1024kb",
        "mean_speedup": 0.13,
        "run_on_fpga": True,
        "fpga_ratio": 0.5,
        "characterization": {
            "avg_req_per_sec": 1,
            "avg_req_duration": 0.5,
        },
        "priority": 2
    }


def corner():
    return {
        # an average function that benefits somewhat from being on the FPGA
        "label": "corner-2025kb",
        "mean_speedup": 10.41,
        "run_on_fpga": True,
        "fpga_ratio": 0.5,
        "characterization": {
            "avg_req_per_sec": 1,
            "avg_req_duration": 120,
        },
        "priority": 1
    }


def gzip():
    return {
        # an average function that benefits somewhat from being on the FPGA
        "label": "gzip-148kb",
        "mean_speedup": 7.79,
        "run_on_fpga": True,
        "fpga_ratio": 0.5,
        "characterization": {
            "avg_req_per_sec": 1,
            "avg_req_duration": 8,
        },
        "priority": 1
    }


def hls4ml():
    return {
        # an average function that benefits somewhat from being on the FPGA
        "label": "hls4ml-3000kb",
        "mean_speedup": 33.22,
        "run_on_fpga": True,
        "fpga_ratio": 0.5,
        "characterization": {
            "avg_req_per_sec": 1,
            "avg_req_duration": 1000,
        },
        "priority": 3
    }


def hyperloglog():
    return {
        # an average function that benefits somewhat from being on the FPGA
        "label": "hyperloglog-4kb",
        "mean_speedup": 1.94,
        "run_on_fpga": True,
        "fpga_ratio": 0.5,
        "characterization": {
            "avg_req_per_sec": 1,
            "avg_req_duration": 0.7,
        },
        "priority": 1
    }


def sha256():
    return {
        # an average function that benefits somewhat from being on the FPGA
        "label": "sha256-1024kb",
        "mean_speedup": 0.42,
        "run_on_fpga": True,
        "fpga_ratio": 0.5,
        "characterization": {
            "avg_req_per_sec": 1,
            "avg_req_duration": 2,
        },
        "priority": 1
    }


def sha3():
    return {
        # an average function that benefits somewhat from being on the FPGA
        "label": "sha3-1024",
        "mean_speedup": 1.15,
        "run_on_fpga": True,
        "fpga_ratio": 0.5,
        "characterization": {
            "avg_req_per_sec": 1,
            "avg_req_duration": 5,
        },
        "priority": 1
    }


def nw():
    return {
        # an average function that benefits somewhat from being on the FPGA
        "label": "nw-8kb",
        "mean_speedup": 1822.22,
        "run_on_fpga": True,
        "fpga_ratio": 0.5,
        "characterization": {
            "avg_req_per_sec": 1,
            "avg_req_duration": 1400,
        },
        "priority": 1
    }


def characterized_collection():
    return {
        1: addmul(),
        2: aes128ecb4k(),
        3: corner(),
        4: gzip(),
        5: hls4ml(),
        6: hyperloglog(),
        7: sha256(),
        8: sha3(),
        9: nw(),
    }


def percentage_acceleration(percentage: float):
    # scales mean_speedup by percentage

    values = characterized_collection()
    for key in values:
        if values[key]["mean_speedup"] >= 1:
            values[key]["mean_speedup"] = values[key]["mean_speedup"] * percentage
            if values[key]["mean_speedup"] < 1:
                values[key]["mean_speedup"] = 1
        else:
            values[key]["mean_speedup"] = values[key]["mean_speedup"]

    return values
