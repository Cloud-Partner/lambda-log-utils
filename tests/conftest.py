import pytest
from datetime import datetime
import uuid
import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(
    os.path.abspath(__file__)) + "/../lambda_utils/"))


@pytest.fixture()
def context():
    stream = str(uuid.uuid4()).replace("-", "")
    func_name = "test_function"
    account = "999999999999"
    yyyymmdd = datetime.now().strftime("%Y/%m/%d")

    class context():
        def __init__(self):
            self.aws_request_id = str(uuid.uuid4())
            self.log_group_name = '/aws/lambda/' + func_name
            self.log_stream_name = yyyymmdd + '/[$LATEST]' + stream
            self.function_name = 'print_context'
            self.memory_limit_in_mb = '128'
            self.function_version = '$LATEST'
            self.invoked_function_arn = 'arn:aws:lambda:ap-northeast-1:' + \
                account + ':function:' + func_name
            self.client_context = None
            self.identity = "9999999"
    return context()


@pytest.fixture()
def urandom_list():
    urandom_list = []
    for i in range(9):
        id = os.urandom(12)
        urandom_list.append(id)
    return tuple(urandom_list)


@pytest.fixture(autouse=True)
@pytest.mark.freeze_time
def set_time(freezer):
    DEFAULT_TIME = '2020-04-14 12:00:00'
    freezer.move_to(DEFAULT_TIME)
