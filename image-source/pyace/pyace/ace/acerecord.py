import base64
import json


class ACERecord:
    """Class to hold the dictionary-equivalent of an ACE test record. Properties en methods are available to return
    specific fields, or the entire root as base64 json or complete xml string"""
    def __init__(self, record: dict):
        """Constructor to create the ACERecord instance.

        :param record: ACE record object
        :type record: dictionary
        :returns: instance of ACERecord"""
        self.data = record

    @property
    def integration_server(self):
        """Property to return the integration server name attribute of a record"""
        return self.data["checkpoint"]["messageFlowData"]["integrationServer"]

    @property
    def application(self) -> str:
        """Property to return the project name attribute of a record"""
        return self.data["checkpoint"]["messageFlowData"]["application"]

    @property
    def message_flow(self) -> str:
        """Property to return the message flow attribute of a record"""
        return self.data["checkpoint"]["messageFlowData"]["messageFlow"]

    @property
    def thread_id(self) -> int:
        """Property to return the thread id attribute of a record"""
        return self.data["checkpoint"]["messageFlowData"]["threadId"]

    @property
    def source_node(self) -> str:
        """Property to return the source node attribute of a record"""
        return self.data["checkpoint"]["messageFlowData"]["nodes"]["source"]["name"]

    @property
    def source_terminal(self) -> str:
        """Property to return the source terminal attribute of a record"""
        return self.data["checkpoint"]["messageFlowData"]["nodes"]["source"]["terminal"]

    @property
    def target_node(self) -> str:
        """Property to return the target node attribute of a record"""
        return self.data["checkpoint"]["messageFlowData"]["nodes"]["target"]["name"]

    @property
    def target_terminal(self) -> str:
        """Property to return the target terminal attribute of a record"""
        return self.data["checkpoint"]["messageFlowData"]["nodes"]["target"]["terminal"]

    @property
    def inputmessage_uuid(self) -> str:
        """Property to return the input message UUD attribute of a record"""
        return self.data["checkpoint"]["correlationData"]["inputMessageUUID"]

    @property
    def invocation_uuid(self) -> str:
        """Property to return the invocation UUD attribute of a record"""
        return self.data["checkpoint"]["correlationData"]["invocationUUID"]

    @property
    def flow_sequence_number(self) -> str:
        """Property to return the flow sequence number attribute of a record"""
        return self.data["checkpoint"]["sequenceData"]["flowSequenceNumber"]

    @property
    def is_input_node(self) -> bool:
        """Property to return a boolean indicating whether this record come from an input node"""
        return self.data["checkpoint"]["messageFlowData"]["nodes"]["source"]["inputNode"]

    @property
    def is_first_message(self):
        """"Property to return a boolean indicating whether this was the first message tree recorded in the flow.
        This is true if and only if invocationUUD equals the inputMessageUUID"""
        return self.inputmessage_uuid == self.invocation_uuid

    @property
    def timestamp(self):
        """Property to return the timestamp of the record from when it was in transit in the message flow."""
        return self.data["checkpoint"]["sequenceData"]["timestamp"]

    def test_data(self):
        """Function to return the four bit-streamed root trees as a base64-valued dictionary."""
        return self.data["testData"]

    def test_data_json(self):
        """Function to return the four bit-streamed root trees as a base64-valued JSON string."""
        return json.dumps(self.data["testData"])

    def test_data_xml(self):
        """Function to return the entire root tree as xml string."""
        test_data = self.test_data()
        byte_result = bytearray(b'')
        byte_result += b"<testData>"
        for byte_subtree in list(map(lambda x: base64.b64decode(x), test_data.values())):
            byte_result += byte_subtree
        byte_result += b"</testData>"
        return byte_result.decode('utf-8')
