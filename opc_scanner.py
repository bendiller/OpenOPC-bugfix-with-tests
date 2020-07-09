import OpenOPC


class OPCScanner:
    def __init__(self, opc_host):
        self.client = OpenOPC.client(client_name="PyOPC")
        # self.client = CustomOpenOPC.client(client_name="PyOPC")
        self.opc_host = opc_host

    def connect(self):
        try:
            self.client.connect(opc_server='OPC.DeltaV.1', opc_host=self.opc_host)
            print("Achieved successful connection to DeltaV OPC server")
            print(self.client.info())

        except OpenOPC.OPCError as e:
            print("Could not connect: " + str(e))
            raise e

    def close(self):
        try:
            self.client.close()
        except NameError:
            pass  # No need to attempt to close if opc object never created.

    def get_value(self, path, max_retries=500):
        """Retrieve a single value for an OPC path."""
        retries = max_retries
        exc_for_return = None
        while retries > 0:
            try:
                properties = self.client.properties(path)
                good = False
                for prop in properties:
                    # SCAN PROPERTIES, LOOKING FOR ITEM QUALITY == GOOD
                    if str(prop[1]) == 'Item Quality':
                        if str(prop[2]) == 'Good':
                            good = True
                        else:
                            retries -= 1  # Should not occur, but had to include.
                if good:
                    for prop in properties:
                        if str(prop[1]) == 'Item Value':
                            return str(prop[2])
                    retries -= 1  # NEVER FOUND 'Item Value'
                    exc_for_return = "Didn't find 'Item Value' on final pass"
                else:  # 'Item Quality' EITHER NEVER FOUND, OR FOUND TO BE BAD
                    retries -= 1
                    exc_for_return = "Item quality not good on final pass"

            except Exception as exc:
                retries -= 1
                exc_for_return = exc

        if "OLE error 0xc0040007" in str(exc_for_return):
            exc_for_return = "DoesNotExist"
        return exc_for_return  # DEPLETED ALL RETRIES - UNSUCCESSFUL SCAN
