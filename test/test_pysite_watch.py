import mock, redis, unittest
from pysite_watch import  ConfigParser, PysiteWatch

class TestConfigParser(unittest.TestCase):

    def test_parse_file(self):
        cp = ConfigParser("test/test_config_file")
        cp1 = ConfigParser("test/test_config_file1")
        self.assertTrue(cp.parse_config_file())
        with self.assertRaises(Exception) as exc:
           cp1.parse_config_file()
        self.assertTrue("Error opening the file - ensure that the configuration file exists" in exc.exception)

class TestPysiteWatch(unittest.TestCase):

    #Test for creating dict_item
    def test_create_dict_item(self):
        psw = self.create_pysite_watch_object()
        self.assertTrue(psw.create_dict_item())
        self.assertEquals(dict({0: {'url': 'www.bharatnc.com/about', 'frequency': 60, 'email': 'sample@gmail.com'}}),psw.create_dict_item())

    #Test for inserting into  Redis queue
    @mock.patch.object(PysiteWatch, 'get_time')
    def test_insert_data_into_queue(self, mock_method):
        r = redis.StrictRedis(host='localhost', port=6379, db=0)
        r.flushdb()
        sample_time = self.get_time_sec("8:40:00")
        mock_method.return_value = sample_time
        psw = self.create_pysite_watch_object()
        assert psw.get_time() == sample_time
        self.assertTrue(psw.insert_data_into_queue())

    #Test for monitoring entries while time < target time
    @mock.patch.object(PysiteWatch, 'get_time')
    def test_monitor_queue_helper(self, mock_method):
        r = redis.StrictRedis(host='localhost', port=6379, db=0)
        mock_method.return_value = self.get_time_sec("8:40:00")
        psw = self.create_pysite_watch_object()
        self.assertEquals("Still Monitoring",psw.monitor_queue_helper())

    #Test for monitoring entries while time > target time
    @mock.patch.object(PysiteWatch, 'get_time')
    def test_monitor_queue_helper(self, mock_method):
        r = redis.StrictRedis(host='localhost', port=6379, db=0)
        mock_method.return_value = self.get_time_sec("9:33:20")
        psw = self.create_pysite_watch_object()
        self.assertEquals("['www.bharatnc.com/about,sample@gmail.com,34460.0,60']",psw.monitor_queue_helper())

    #Test for extracting entries
    @mock.patch.object(PysiteWatch, 'extract_entry')
    def test_extract_entry(self, mock_method):
        r = redis.StrictRedis(host='localhost', port=6379, db=0)
        r.flushdb()
        e_mail, freq, target_time, target_url, top = self.helper_extract_entry()
        mock_method.return_value = e_mail, freq, target_time, target_url, top
        psw = self.create_pysite_watch_object()
        self.assertEquals (psw.extract_entry(),self.helper_extract_entry())

    #Test for get_status method
    def test_get_status(self):
        test_url = "www.google.com"
        test_email = "sample@gmail.com"
        with mock.patch.object(PysiteWatch, 'get_status', return_value=True) as mock_method:
            psw = self.create_pysite_watch_object()
            psw.get_status(test_url,test_email)
        mock_method.assert_called_once_with(test_url,test_email)

    #Test for send_alert_smtp method
    def test_send_alert_smtp(self):
        test_email_to = "sample@gmail.com"
        test_msg = "ip down"
        with mock.patch.object(PysiteWatch, 'send_alert_smtp', return_value = None) as mock_method:
            psw = self.create_pysite_watch_object()
            psw.send_alert_smtp(test_email_to, test_msg)
        mock_method.assert_called_once_with(test_email_to,test_msg)


    #Test for getting response time
    @mock.patch.object(PysiteWatch,'get_response_time')
    def test_get_response_time(self,mock_method):
        mock_method.return_value = 0.5
        psw = self.create_pysite_watch_object()
        assert psw.get_response_time() == 0.5

    #Test for checking status code
    @mock.patch.object(PysiteWatch,'check_status')
    def test_check_status(self,mock_method):
        mock_method.return_value = 200
        test_url = "http://www.bharatnc.com"
        psw = self.create_pysite_watch_object()
        assert psw.check_status(test_url) == 200

    #Helper method to create config file object
    def create_pysite_watch_object(self):
        cp = ConfigParser("test/test_config_file")
        py = PysiteWatch(cp.parse_config_file(),"smtp.gmail.com",587,"email_address_here", "password_here*", "localhost", 6379)
        return py

    #Helper method to generate sample time stamp for testing
    def get_time_sec(self,str_time):
        hours,minutes,seconds = str_time.split(':')
        return float(int(hours) * 3600 + int(minutes) * 60 + int(seconds))

    #Helper method to extract an entry from redis
    def helper_extract_entry(self):
        r = redis.StrictRedis(host='localhost', port=6379, db=0)
        r.flushdb
        psw = self.create_pysite_watch_object()
        psw.insert_data_into_queue()
        top = r.zrange("time_based_sort", 0, -1)[0]
        tmp = top.split(",")
        target_time = tmp[2]
        target_url = tmp[0]
        e_mail = tmp[1].strip()
        freq = tmp[3]
        return e_mail, freq, target_time, target_url, top