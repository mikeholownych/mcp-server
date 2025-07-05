import unittest
from unittest.mock import patch
from mcp_server.observability import send_slack_notification, notify_test_failure, notify_deployment, notify_rollback

class ObservabilityTestCase(unittest.TestCase):
    
    @patch('mcp_server.observability.requests.post')
    @patch('mcp_server.observability.os.getenv')
    def test_send_slack_notification_success(self, mock_getenv, mock_post):
        mock_getenv.return_value = 'http://example.com/webhook'
        mock_post.return_value.status_code = 200
        
        try:
            send_slack_notification('Test message')
        except Exception as e:
            self.fail(f"send_slack_notification raised an exception {e}")
    
    @patch('mcp_server.observability.send_slack_notification')
    def test_notify_test_failure(self, mock_send):
        notify_test_failure("Unit Test 1")
        mock_send.assert_called_once_with(":x: Test Failed: Unit Test 1")
    
    @patch('mcp_server.observability.send_slack_notification')
    def test_notify_deployment(self, mock_send):
        notify_deployment("Production")
        mock_send.assert_called_once_with(":rocket: Deployment to Production succeeded.")
    
    @patch('mcp_server.observability.send_slack_notification')
    def test_notify_rollback(self, mock_send):
        notify_rollback("Production")
        mock_send.assert_called_once_with(":rewind: Rollback executed on Production.")

if __name__ == '__main__':
    unittest.main()
