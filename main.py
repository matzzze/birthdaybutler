#!/usr/bin/python3 -u

import yaml
from pathlib import Path
from urllib.request import urlretrieve
import requests
import vobject
import io
import re
from datetime import datetime, date, timedelta

'''general helper functions'''
def becomes_age(byear):
    now = datetime.now()
    return now.year - int(byear)

def helpprettyprint_pre(hitlist, futdate):
    print('Name Date becomeAge')
    for hit in hitlist:
        if hit['age']:
            print(hit['name'], futdate, hit['age'])
        else:
            print(hit['name'], futdate, '--')
        
'''classes'''
class Configuration:
    def __init__(self):
        #define constants
        self.conffile = 'butlerconf.yaml'
        self.cachefile = 'cachefile.vcf'
        #read yaml globally
        self.global_configdict = self.parse_conf()
        #decide sourcetype
        self.source_configdict = self.global_configdict['source']
        for key,subdict in self.source_configdict.items():
            if subdict['active']:
                self.source_type = key
                if 'path' in subdict:
                    self.source_arg = subdict['path']
                else:
                    self.source_arg = subdict['url']
                break
        #create cachefile from source
        self.delete_old_cachefile()
        if self.source_type == 'carddav':
            self.download_cachefile()
        if self.source_type == 'filedav':
            pass
        # check reminder settings
        self.reminders_configdict = self.global_configdict['reminders']
        self.reminder_pre1 = self.reminders_configdict['prereminder1']
        self.reminder_pre2 = self.reminders_configdict['prereminder2']
        # check notifier settings
        self.notifier_configdict = self.global_configdict['notifier']
        if self.notifier_configdict['ntfy_active']:
            self.ntfy_url = self.notifier_configdict['ntfy_url']


    # additional methods
    # read yaml
    def parse_conf(self):
        with open(self.conffile) as stream:
            try:
                global_configdict = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        return global_configdict
    # delete cachefile
    def delete_old_cachefile(self):
        my_file = Path(self.cachefile) 
        if my_file.is_file():
            my_file.unlink()
    #download cachefile for carddav
    def download_cachefile(self):
        url = self.source_arg
        filename = self.cachefile
        urlretrieve(url, filename)


class Birthday:
    def __init__(self, sourcefile, prereminder1=False, prereminder2=False, ntfy_url=False):
        self.sourcefile = sourcefile
        self.ntfy_url = ntfy_url
        self.all_bdays = self.betterparse()
        self.hits_today = self.hits_x_day()
        self.hits_pre1 = self.hits_x_day(prereminder1)
        self.hits_pre2 = self.hits_x_day(prereminder2)
        self.prereminder1 = prereminder1
        self.prereminder2 = prereminder2
        if self.ntfy_url:
            self.notify(self.ntfy_url, self.hits_today)
        if self.prereminder1:
            self.notify(self.ntfy_url, self.hits_x_day(self.prereminder1))
        if self.prereminder2:
            self.notify(self.ntfy_url, self.hits_x_day(self.prereminder2))

    def notify(self, ntfy_url, inputlist):
        for bday in inputlist:
            print('Send notification for xx')
            name = bday['name']
            age = bday['age']
            bdate = '' 
            notifystring = str(name) + 'has birthday' + str(date)
            requests.post(self.ntfy_url, data = notifystring.encode(encoding='utf-8'))

    def prettyprint_bdays(self):
        print('This is all retrieved birthdates:')
        print('Name Month Day Year becomeAge')
        for contact in self.all_bdays:
            if contact['byear']:
                print(contact['contact_name'], contact['bmon'], contact['bday'], contact['byear'], becomes_age(contact['byear']))
            else:
                print(contact['contact_name'], contact['bmon'], contact['bday'], contact['byear'], '--')

    def prettyprint_hitstoday(self):
        print('These are the extracted birthdays today ' + str(date.today()))
        print('Name Date becomeAge')
        for hit in self.hits_today:
            if hit['age']:
                print(hit['name'], date.today(), hit['age'])
            else:
                print(hit['name'], date.today(), '--')

    def prettyprint_hitspre1(self):
        if self.prereminder1:
            xday = date.today() + timedelta(days=self.prereminder1)
            print('Prereminder1 is active and set to ' + str(self.prereminder1) + ' aiming at ' + str(xday))
            helpprettyprint_pre(self.hits_pre1, xday)
        else:
            print('Preminder1 is not active')

    def prettyprint_hitspre2(self):
        if self.prereminder2:
            xday = date.today() + timedelta(days=self.prereminder2)
            print('Prereminder2 is active and set to ' + str(self.prereminder1) + ' aiming at ' + str(xday))
            helpprettyprint_pre(self.hits_pre2, xday)
        else:
            print('Preminder2 is not active')

    #create a list of dictionaries consisting of birthdates & name
    def betterparse(self):
        bdaylist = []
        stream = io.open(self.sourcefile, "r", encoding="utf-8")
        vcardlist = vobject.readComponents(stream, ignoreUnreadable=True)
        for contact in vcardlist:
            contact_name = contact.fn.value
            contact_keys = contact.contents.keys()
            if 'bday' in contact_keys:
                contact_byear = self.extract_year(contact.contents['bday'])
                contact_bmon = self.extract_date(contact.contents['bday'], 'month')
                contact_bday = self.extract_date(contact.contents['bday'], 'day')
                #print(contact_name,contact_byear, contact_bmon, contact_bday)
                if contact_bmon and contact_bday:
                    bdict = {'bmon': int(contact_bmon), 'bday': int(contact_bday), 'contact_name': contact_name, 'byear': contact_byear}
                    #print(bdict)
                    bdaylist.append(bdict)
        stream.close()
        return bdaylist
    #store birthdays in a list for main & prereminders
    def hits_x_day(self,x=0):
        if x is False:
            pass
        hits_x =[]
        xday = date.today() + timedelta(days=x)
        curryear = date.today().year
        for item in self.all_bdays:
            itembday = date(curryear, item['bmon'], item['bday'])
            if itembday == xday:
                bdict = {'name': item['contact_name'], 'age': None}
                if item['byear']: 
                    bdict['age'] = becomes_age(item['byear'])
                hits_x.append(bdict)
        return hits_x

    def extract_date(self, fuckedbd, infotype):
        myregexp = re.compile(r'(\d\d-?\d\d)\W$')
        reggroup = myregexp.search(str(fuckedbd[0]))
        if reggroup:
            date = reggroup.group(1).replace('-','')
            if infotype == 'day': 
                return date[2:4]
            return date[0:2]
            
    def extract_year(self,fuckedbd):
        myregx = re.compile(r'19\d\d')
        resgroup = myregx.search(str(fuckedbd))
        if resgroup != None:
            return resgroup.group()

if __name__ == "__main__":
    my_config = Configuration()
    bday = Birthday(my_config.cachefile, my_config.reminder_pre1, my_config.reminder_pre2, my_config.ntfy_url)
    bday.prettyprint_bdays()
    bday.prettyprint_hitstoday()
    bday.prettyprint_hitspre1()
    bday.prettyprint_hitspre2()
