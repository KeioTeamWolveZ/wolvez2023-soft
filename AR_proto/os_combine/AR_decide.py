class AR_ID_decider():
    def __init__(self):
        self.aprc_AR = False
        self.omote_ura = None

    def AR_decide(self, ar_info, connecting_state):
        if connecting_state == 0:
            if "1" in ar_info.keys() and "2" in ar_info.keys():
                self.aprc_AR = True
            else: 
                self.aprc_AR = False

        elif connecting_state == 1:
            if "3" in ar_info.keys() or "4" in ar_info.keys():
                self.aprc_AR = True
                self.omote_ura = 0
            elif "5" in ar_info.keys() or "6" in ar_info.keys():
                self.aprc_AR = True
                self.omote_ura = 1
            else: 
                self.aprc_AR = False
        return {"AR":self.aprc_AR, "side":self.omote_ura}