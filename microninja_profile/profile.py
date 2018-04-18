import json
import urllib2
import os
from urllib import quote
from microninja.utils import get_user_unsudoed, run_cmd

class apiProfile:
    error = ""
    def __init__(self):
        self.profile = None
        home = os.path.expanduser("/home/"+get_user_unsudoed())
        if( os.path.isfile(home + '/.microninjaprofile/microninja_user_profile') ) :
            with open(home + '/.microninjaprofile/microninja_user_profile', 'r') as profile:
                data=profile.read().replace('\n', '')
                self.profile = json.loads(data)
    
    def _connection(self, url, data = None):
        #try:
        #    req = urllib2.Request(self.remote_path + "api/v1/" + url )
        #    if not data is None:
        #        req.add_header('Content-Type', 'application/json')
        #        return  json.load(urllib2.urlopen(req, json.dumps(data)))
        #    else:
        #        return  json.load(urllib2.urlopen(req))
        #except :
        #    return False
        
        if url == "user/store":
            ret_data = {
                "status": 200,
                "user": {
                "username": data["username"],
                "name": data["name"],
                "lastname": data["lastname"],
                "birthdate": data["birthdate"],
                "gender": data["gender"],
                "email": data["email"],
                "token": "go_58bd7defd0636",
                "id": 35
                }
            }
            return ret_data

        if url == "user/exists":
            out, err, _ = run_cmd('getent passwd '+  data["username"])
            userLine = out.strip('\n')
            if len(userLine) and userLine.split(':')[0] == data["username"]:
                return True
            else:
                return False
        
    def _saveprofileFile(self, password):
        try:
            from microninja.utils import run_cmd
            if not os.path.isdir("/home/" + self.profile['username']):
                username = self.profile['username']
                r,s,c = run_cmd("sudo /usr/bin/microninja-greeter-account " + username + " " + password + " " + quote(json.dumps(self.profile)))

        except Exception ,e :
            return str(e)
                
    def userExists(self, username):
        url = "user/exists"
        data = {"username" : username }
        response = self._connection(url, data)
        if response == False:
            return False
        if response['status'] == 200 and response['exist'] == True:
            return True
        
        return False
    
    def store(self, username, password, name, lastname, birthdate, gender, emailparent=None):
        data = {
            "username" : username ,
            "password" : password ,
            "name" : name ,
            "lastname" : lastname ,
            "birthdate" : birthdate ,
            "gender" : gender 
        }
        if not emailparent is None:
            data["email"] = emailparent
        else:
            data["email"] = 'not-provided'
        
        user = self._connection("user/store", data)
        if user == False :
            self.error = "{\"error\":\"Errore di connessione\"}"
            return False
        if user['status'] == 200 :
            self.profile = user['user']
            self._saveprofileFile(password)
            return True
        self.error = user['error']
        return False

    def storeCompany(self, username, password, name, lastname,  email, company, address, fiscalcode, type, meccanografico, phone) :
        data = {
            "username" : username ,
            "password" : password ,
            "name" : name ,
            "lastname" : lastname ,
            "company" : company ,
            "fiscalcode" : fiscalcode ,
            "type" : type ,
            "meccanografico" : meccanografico , 
            "phone" : phone  ,
            "email" : email ,
            "address" : address
        }
        user = self._connection("user/storecompany",data)
        if user == False :
            self.error = "{\"error\":\"Errore di connessione\"}"
            return False
        if user['status'] == 200 :
            self.profile = user['user']
            self._saveprofileFile(password)
            return True
        self.error = user['error']
        return False
    
    def login(self, user, password) :
        data = {
            "username" : user ,
            "password" : password 
        }
        
        response = self._connection("user/get", data)
        if response == False :
            self.error = "{\"errore\":\"Errore di connessione\"}"
            return False
        if response['status'] == 200:
            self.profile = response['user']
            self._saveprofileFile(password)
            return True
        self.error = response['error']
        return False

    def getError(self):
        try:
            if  isinstance(self.error,str):
                messages = json.loads(self.error)
            else:
                messages = self.error
            text = []
            for m in messages.keys():
                if isinstance(messages[m],list):
                    for t in messages[m]:
                        text.append(t)
                else:
                    text.append(messages[m])

            return "\n".join(text)
        except  Exception,e:
            print str(e)
            return self.error


    def getAllScore(self):
        data = {
            "token" : self.profile['token']
        }
        response = self._connection("level/get",data)
        if response == False :
            self.error = "{\"errore\":\"Errore di connessione\"}"
            return False
        if response['status'] == 200 :
            return response['score']
        return []
    
    def getApplications(self):
        response = self._connection("level/application")
        if response == False :
            self.error = "{\"errore\":\"Errore di connessione\"}"
            return False
        if response['status'] == 200 :
            return response['application']
        return []
    
    def setScore(self, application, score) :
        data = {
            application : application,
            token : self.profile['token'],
            score : score
        }
        
        response = self._connection("level/store" , data )
        if response == False :
            self.error = "{\"errore\":\"Errore di connessione\"}"
            return False
        if response['status'] == 200 :
            return response['score']
        self.error = response['error']
        return False

    def changePassword(self, newpassword):
        return True
     
   
if __name__ == '__main__':
    api = apiProfile()

        
        
