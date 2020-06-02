import lambda_utils.lambda_utils as lambda_utils
from datetime import datetime
import json
import pytest
import os
import time
import binascii


class SampleError(Exception):
    pass

# =========================================
#                  event
# =========================================


DEFAULT_TIME = '2020-04-14 12:00:00'


@pytest.fixture()
def event():
    return {
        'version': '2.0',
        'routeKey': '$default',
        'rawPath': "/",
        'rawQueryString': '',
        'cookies': [],
        'headers': {},
        'queryStringParameters': {},
        'requestContext': {
            'accountId': '123456789012',
            'apiId': 'api-id',
            'authorizer': {
                'at_hash': 'IkV4T1lwp1QWDYgOYm_6eQ',
                'sub': 'c859b63c-fd43-42fa-9bdc-61652137c852',
                'email_verified': 'true',
                'session': '86965bbf-c769-4941-b5ad-85dd50ac12c2',
                'iss': 'https://cognito-idp.ap-northeast-1.amazonaws.com/ap-northeast-1_uVbjEAOBJ',
                'principalId': '',
                'cognito:username': '1234567',
                'integrationLatency': 181,
                'aud': '7cndi2ce05ssps0a6c1bjvavnl',
                'event_id': 'fca618e7-0a8a-40bb-9e50-05239d2f765a',
                'token_use': 'id',
                'auth_time': '1589551397',
                'exp': '1589554997',
                'iat': '1589551397',
                'email': 'nakayama@chara-web.co.jp'
            },
            'domainName': 'id.execute-api.us-east-1.amazonaws.com',
            'domainPrefix': 'id',
            'http': {
                'method': 'POST',
                'path': '/my/path',
                'protocol': 'HTTP/1.1',
                'sourceIp': 'IP',
                'userAgent': 'agent'
            },
            'requestId': 'id',
            'routeKey': '$default',
            'stage': '$default',
            'time': '12/Mar/2020:19:03:58 +0000',
            'timeEpoch': int(datetime.fromisoformat(DEFAULT_TIME).timestamp())
        },
        'pathParameters': {},
        'isBase64Encoded': False,
        'stageVariables': {}
    }

# =========================================
#             個別のmethodのmock
# =========================================


TEST_PARAMS = [
    {
        'description': '200 response',
        'payload': {
            "key": "value"
        }
    },
    {
        'description': '200 response with status',
        'payload': ({
            "key": "value"
        }, 200)
    },
    {
        'description': '201 response with status',
        'payload': ({
            "key": "value"
        }, 201)
    },
]


@pytest.fixture(params=TEST_PARAMS, ids=list(map(lambda x: x['description'], TEST_PARAMS)))
def request_params(request):
    return request.param


@pytest.fixture()
def lambda_handler_mock(mocker, request_params):
    handler_mock = mocker.Mock()
    if isinstance(request_params['payload'], Exception) is False:
        handler_mock.return_value = request_params['payload']

    return handler_mock


@pytest.fixture()
def urandom_mock(mocker, urandom_list):
    urandom_mock = mocker.Mock()
    urandom_mock.side_effect = urandom_list
    mocker.patch.object(lambda_utils, "urandom", urandom_mock)
    return urandom_mock


# @pytest.fixture()
# def random_mock(mocker, random_list):
#     random_mock = mocker.Mock()
#     random_mock.randint.side_effect = random_list
#     mocker.patch.object(manager, "random", random_mock)
#     return random_mock


# @pytest.fixture()
# def validate_parameter_mock(mocker):
#     validate_parameter_mock = mocker.Mock(
#         wraps=create.validate_parameter
#     )
#     mocker.patch.object(
#         create,
#         'validate_parameter',
#         validate_parameter_mock
#     )
#     return validate_parameter_mock


# # =========================================
# #             method test
# # =========================================

class Test_set_trace_id:

    def test_trace_id_with_X_AMZN_TRACE_ID(self, event, context):
        if 'trace_id' in os.environ:
            del os.environ['trace_id']
        os.environ['_X_AMZN_TRACE_ID'] = "Self=1-5eb5a279-3495486f1d3332fba1b67b30;Root=1-5eb5a279-87b966d0c206d010a3ddf0e8;Parent=79be71115925fdf5;Sampled=1"
        utils = lambda_utils.Utils()
        logger = utils.logger

        @utils.set_trace_id
        def handler(evt, con):
            return {"key", "value"}

        handler(event, context)

        assert 'trace_id' in logger.__dict__['log_keys']
        assert logger.__dict__[
            'log_keys']['trace_id'] == "1-5eb5a279-87b966d0c206d010a3ddf0e8"
        assert 'trace_id' in os.environ
        assert os.environ['trace_id'] == "1-5eb5a279-87b966d0c206d010a3ddf0e8"

    def test_trace_id_without_X_AMZN_TRACE_ID(self, event, context, urandom_mock, urandom_list):
        if 'trace_id' in os.environ:
            del os.environ['trace_id']
        os.environ['_X_AMZN_TRACE_ID'] = "1-5eb5a279-87b966d0c206d010a3ddf0e8"
        utils = lambda_utils.Utils()
        logger = utils.logger

        @utils.set_trace_id
        def handler(evt, con):
            return {"key", "value"}

        handler(event, context)

        START_TIME = time.time()
        HEX = hex(int(START_TIME))[2:]
        trace_id = "0-{}-{}".format(
            HEX, str(binascii.hexlify(urandom_list[0]), 'utf-8'))

        assert 'trace_id' in logger.__dict__['log_keys']
        assert logger.__dict__[
            'log_keys']['trace_id'] == trace_id
        assert 'trace_id' in os.environ
        assert os.environ['trace_id'] == trace_id

    def test_invalid_X_AMZN_TRACE_ID(self, event, context, urandom_mock, urandom_list):
        if 'trace_id' in os.environ:
            del os.environ['trace_id']
        if '_X_AMZN_TRACE_ID' in os.environ:
            del os.environ['_X_AMZN_TRACE_ID']
        utils = lambda_utils.Utils()
        logger = utils.logger

        @utils.set_trace_id
        def handler(evt, con):
            return {"key", "value"}

        handler(event, context)

        START_TIME = time.time()
        HEX = hex(int(START_TIME))[2:]
        trace_id = "0-{}-{}".format(
            HEX, str(binascii.hexlify(urandom_list[0]), 'utf-8'))

        assert 'trace_id' in logger.__dict__['log_keys']
        assert logger.__dict__[
            'log_keys']['trace_id'] == trace_id
        assert 'trace_id' in os.environ
        assert os.environ['trace_id'] == trace_id


class Test_api_gateway_response:

    def setup_method(self):
        os.environ['POWERTOOLS_TRACE_DISABLED'] = "true"

    def test_normal_200_response(self, event, context):

        utils = lambda_utils.Utils()

        @utils.api_gateway_response
        def handler(evt, ctx):
            return {"key": "value"}

        res = handler(event, context)

        assert res == {
            'isBase64Encoded': False,
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            'body': json.dumps({"key": "value"})
        }

    def test_normal_200_response_with_status(self, event, context):

        utils = lambda_utils.Utils()

        @utils.api_gateway_response
        def handler(evt, ctx):
            return ({"key": "value"}, 200)

        res = handler(event, context)

        assert res == {
            'isBase64Encoded': False,
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            'body': json.dumps({"key": "value"})
        }

    def test_normal_200_response_of_str(self, event, context):

        utils = lambda_utils.Utils()

        @utils.api_gateway_response
        def handler(evt, ctx):
            return json.dumps({"key": "value"})

        res = handler(event, context)

        assert res == {
            'isBase64Encoded': False,
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            'body': json.dumps({"key": "value"})
        }

    def test_normal_200_response_of_str_with_status(self, event, context):

        utils = lambda_utils.Utils()

        @utils.api_gateway_response
        def handler(evt, ctx):
            return (json.dumps({"key": "value"}), 200)

        res = handler(event, context)

        assert res == {
            'isBase64Encoded': False,
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            'body': json.dumps({"key": "value"})
        }

    def test_normal_201_response_with_status(self, event, context):

        utils = lambda_utils.Utils()

        @utils.api_gateway_response
        def handler(evt, ctx):
            return ({"key": "value"}, 201)

        res = handler(event, context)

        assert res == {
            'isBase64Encoded': False,
            'statusCode': 201,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            'body': json.dumps({"key": "value"})
        }

    def test_400_exception(self, event, context):
        os.environ['trace_id'] = "1-5eb5a279-87b966d0c206d010a3ddf0e8"

        utils = lambda_utils.Utils()

        @utils.api_gateway_response
        def handler(evt, ctx):
            try:
                raise SampleError("sample message")
            except SampleError as e:
                return e

        res = handler(event, context)

        assert res == {
            "isBase64Encoded": False,
            "statusCode": 400,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            'body': json.dumps({
                "Code": "SampleError",
                        "Message": "sample message",
                        "TraceId": "1-5eb5a279-87b966d0c206d010a3ddf0e8"
            })
        }

    def test_400_exception_with_status(self, event, context):
        os.environ['trace_id'] = "1-5eb5a279-87b966d0c206d010a3ddf0e8"

        utils = lambda_utils.Utils()

        @utils.api_gateway_response
        def handler(evt, ctx):
            try:
                raise SampleError("sample message")
            except SampleError as e:
                return (e, 400)

        res = handler(event, context)

        assert res == {
            "isBase64Encoded": False,
            "statusCode": 400,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            'body': json.dumps({
                "Code": "SampleError",
                        "Message": "sample message",
                        "TraceId": "1-5eb5a279-87b966d0c206d010a3ddf0e8"
            })
        }

    def test_404_exception_with_status(self, event, context):
        os.environ['trace_id'] = "1-5eb5a279-87b966d0c206d010a3ddf0e8"

        utils = lambda_utils.Utils()

        @utils.api_gateway_response
        def handler(evt, ctx):
            try:
                raise SampleError("sample message")
            except SampleError as e:
                return (e, 404)

        res = handler(event, context)

        assert res == {
            "isBase64Encoded": False,
            "statusCode": 404,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            'body': json.dumps({
                "Code": "SampleError",
                        "Message": "sample message",
                        "TraceId": "1-5eb5a279-87b966d0c206d010a3ddf0e8"
            })
        }
