class Syslog:

    def __init__(self, class_object):
        self.class_object = class_object
        self.log_history = []
        self.enable_sequence_number = False # TODO:!!!
        self.log_severity = {
            0: 'Emergency',
            1: 'Alert',
            2: 'Critical',
            3: 'Error',
            4: 'Warning',
            5: 'Notification',
            6: 'Informational',
            7: 'Debug',
        }

    def generate_log(self, facility, severity:int, mnemonic, description):
        next_sequence_number = str(len(self.log_history))
        # self.log_history.append([next_sequence_number, internal_clock.now(), facility, str(severity), mnemonic, description])
        log_entry = [next_sequence_number, '123465', facility, str(severity), mnemonic, description]
        self.log_history.append(log_entry)
        return self.log_as_str(log_entry)  # Returned to show in console
    
    def log_as_str(self, log):
        return log[0] + ':' + log[1] + ': %' + log[2] + '-' + log[3] + '-' + log[4] + ': ' + log[5]

    def show_logging(self):
        log_buffer = ''
        for log in self.log_history:
            log_buffer += ('*' + self.log_as_str(log))
        return log_buffer

s = Syslog(None)

s.generate_log('LINK', 3, 'UPDOWN', 'Interface Port-channel1, changed state to up')

print(s.show_logging())