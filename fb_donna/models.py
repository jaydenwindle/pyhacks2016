import apiai
import json
from django.db import models
from pymessenger.bot import Bot

fb_bot = Bot('EAASgZByvZAU4IBAByrTx2LtwvubcHF6wffMS0sBZAHbm1G5Pfu7LmC5eqyYqaqZBZB7TBqmZAQC8Cf1PF8plikSYVZCLoC55mqGbFWMEdqYAn8vDb7V9hba1Cy1H8A381GqOWwVdZCxjbhzZBc0TeZAVH40ZC09HAls83oK5EBCuP3BswZDZD')
ai = apiai.ApiAI('9a343a102ba24f4dbf0fe5292b94d8bb')

class User(models.Model):
    """docstring for User"""
    id          = models.IntegerField(primary_key = True)    
    first_name  = models.CharField(max_length = 50)
    last_name   = models.CharField(max_length = 50)
    gender      = models.CharField(max_length = 50)

    def save(self, *args, **kwargs):
        self.get_fb_info()
        super(User, self).save(*args, **kwargs)

    def send_text(self, message):
        """sends a fb message to the user"""
        print("sending text!")
        fb_bot.send_text_message(self.id, message)
    
    def get_fb_info(self):
        """docstring for get_fb_info"""
        info = fb_bot.get_user_info(self.id)
        self.first_name = info['first_name']
        self.last_name = info['last_name']
        self.gender = info['gender']

    def ai_req(self, message, reqType="text", returnDict=False):
        """docstring for get_ai_resp"""
        if reqType == 'text':
            req = ai.text_request()
            req.session_id = self.id
            req.query = message
            resp = json.loads(req.getresponse().read().decode('utf-8'))
            if returnDict:
                return resp
            else:
                return resp['result']['fulfillment']['speech']

class ScheduleItem(models.Model):
    """docstring for ScheduleItem"""
    user = models.ForeignKey(User)
    date = models.DateTimeField()
    name = models.CharField(max_length=100)
