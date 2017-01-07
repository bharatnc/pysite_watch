import argparse, redis, requests, smtplib, sys,time, yaml
from email.mime.text import MIMEText

class ConfigParser:

    def __init__(self, config_file):
        self.config_file = config_file

    def parse_config_file(self):
        try:
            f = open(self.config_file, "r")
            data = yaml.load(f)
        except:
            raise Exception("Error opening the file - ensure that the configuration file exists")
        return data

class PysiteWatch():

    def __init__(self, entry_val,smtp_server,smtp_port, smtp_email,smtp_pwd, address, port):
        self.entry = entry_val
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_email = smtp_email
        self.smtp_pwd = smtp_pwd
        self.address = address
        self.port = port

    def __str__(self):
        return str(self.entry)

    def create_dict_item(self):
        i = 0
        dict_item = {}
        try:
            for every_item in self.entry:
                dict_item[i] = every_item
                i += 1
        except:
            print ("Not able to iter through the dict or __setitem__")
        return dict_item

    def insert_data_into_queue(self):
        r = self.connect_to_redis()
        rd = self.create_dict_item()
        for index_item, key_item in rd.iteritems():
            final_time = self.get_time()
            record = rd[index_item]["url"] + "," + rd[index_item]["email"] + "," + str(final_time).strip() + "," + str(
                rd[index_item]["frequency"]).strip()
            r.zadd("time_based_sort", final_time, record)
        return True

    def connect_to_redis(self):
        try:
            r = redis.StrictRedis(host= str(self.address), port=int(self.port), db=0)
        except:
            raise Exception("Cannot connect to Redis. Please check your connection")
        return r

    def monitor(self):
        print self.insert_data_into_queue()
        while (True):
            time.sleep(1)
            self.monitor_queue_helper()

    def monitor_queue_helper(self):
        e_mail, freq, target_time, target_url, top = self.extract_entry()
        r=self.connect_to_redis()
        if self.get_time() > float(target_time):
            self.get_status(e_mail, target_url)
            print time.time()
            r.zrem("time_based_sort", top)
            final_time = self.get_time() + int(freq)
            url = target_url + "," + e_mail + "," + str(final_time) + "," + str(freq)
            r.zadd("time_based_sort", str(final_time), url)
            top = r.zrange("time_based_sort", 0, -1)[0]
            val = str(r.zrange("time_based_sort", 0, -1))

        else:
            val =  "Still Monitoring"
        return val

    def extract_entry(self):
        r = self.connect_to_redis()
        top = r.zrange("time_based_sort", 0, -1)[0]
        tmp = top.split(",")
        target_time = tmp[2]
        target_url = tmp[0]
        e_mail = tmp[1].strip()
        freq = tmp[3]
        return e_mail, freq, target_time, target_url, top

    def get_status(self, e_mail, target_url):
        stat = ""
        try:
            req = requests.get(str(target_url))
            rcode = req.status_code
            if rcode != 200:
                self.send_alert_smtp(e_mail, target_url)
            else:
                stat = True
        except:
            self.send_alert_smtp(e_mail, target_url)
        return stat

    def get_time(self):
        return time.time()

    def send_alert_smtp(self, to_email, url):
        mailTo = to_email
        mailFrom = self.smtp_email
        msg = MIMEText("Alert: IP down")
        msg['Subject'] = "IP down" +  " " + str(url)
        msg['From'] = mailFrom
        msg['To'] = mailTo
        s = smtplib.SMTP(str(self.smtp_server), int(self.smtp_port))
        s.starttls()
        s.login(mailFrom, self.smtp_pwd)
        s.sendmail(mailFrom, mailTo, msg.as_string())

    def check_status(self, url):
        req = requests.get(url)
        code = req.status_code
        return code

    def get_response_time(self, url):
        before = self.get_time()
        try:
            req = requests.get("http://" + str(url))
            after = self.get_time()
            response_time = after - before
            print response_time
        except:
            raise Exception("Error Landing URL")
        return response_time

if __name__ == "__main__":
    
    def main():
        parser = argparse.ArgumentParser()
        parser.add_argument("smtp_server")
        parser.add_argument("smtp_port")
        parser.add_argument("email")
        parser.add_argument("pwd")
        parser.add_argument("address")
        parser.add_argument("port")
        args = parser.parse_args()
        smtp_server = args.smtp_server
        smtp_port = args.smtp_port
        smtp_email = args.email
        smtp_pwd = args.pwd
        address = args.address
        port = args.port
        p = ConfigParser("pysite_watch_config")
        r = PysiteWatch(p.parse_config_file(),smtp_server,smtp_port,smtp_email,smtp_pwd, address, port)
        r.create_dict_item()
        r.monitor()
    main()

