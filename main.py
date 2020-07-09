import json
import sys
import traceback

from opc_scanner import OPCScanner


def prove_connectivity(inp_cfg, use_alt_host=False):
    """Use some known paths to validate that retrieval of values is functioning properly"""
    if use_alt_host:
        opc = OPCScanner(opc_host=inp_cfg["OPC_HOST_ALT"])
    else:
        opc = OPCScanner(opc_host=inp_cfg["OPC_HOST"])
    try:
        opc.connect()
        result_4 = opc.get_value("LIC_572989/AO1/BLOCK_ERR.CV")
        print(result_4)

    except Exception as e:
        print("Exception encountered: " + str(e))
        traceback.print_exc()

    finally:
        opc.close()


if __name__ == "__main__":
    with open('cfg.json', 'r') as fp:
        cfg = json.load(fp)

    if not cfg:
        print("Could not load configuration from 'cfg.json'. Exiting.")
        sys.exit()

    prove_connectivity(cfg, use_alt_host=True)