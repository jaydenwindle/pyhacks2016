from django.shortcuts import render
from django.views import generic
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
import pprint
import apiai
from pymessenger.bot import Bot
from dateutil import parser 

from .models import User, ScheduleItem

ai = apiai.ApiAI('9a343a102ba24f4dbf0fe5292b94d8bb')
pp = pprint.PrettyPrinter(indent=2)
fb_bot = Bot('EAASgZByvZAU4IBAByrTx2LtwvubcHF6wffMS0sBZAHbm1G5Pfu7LmC5eqyYqaqZBZB7TBqmZAQC8Cf1PF8plikSYVZCLoC55mqGbFWMEdqYAn8vDb7V9hba1Cy1H8A381GqOWwVdZCxjbhzZBc0TeZAVH40ZC09HAls83oK5EBCuP3BswZDZD')

class DonnaBot(generic.View):
    """docstring for DonnaBot"""
    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == '2318934571':
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('hello world')

    # disable csrf cookies for bot
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    # handle all post requests
    def post(self, request, *args, **kwargs):
        # parse body to json
        incoming_message = json.loads(self.request.body.decode('utf-8'))

        pp.pprint(incoming_message)

        if 'entry' in incoming_message:
            for entry in incoming_message['entry']:
                for message in entry['messaging']:
                    self.handleMessage(message)
        return HttpResponse() 

    def handleMessage(self, message):
        """docstring for handleMessage"""
        # set up req
        if 'message' in message:
            user_id = int(message['sender']['id'])
            message = message['message']['text']
            # query db
            current_user = User.objects.filter(id__exact=user_id)
            # else send ai response
            current_user = current_user[0]
            resp = current_user.ai_req(message)

            pp.pprint(resp)

            current_user.send_text(resp)
        elif 'postback' in message:
            user_id = int(message['sender']['id'])
            if message['postback']['payload'] == 'GREETING':
                new_user = User(id=user_id)
                new_user.save()
                resp = new_user.ai_req('new user')
                new_user.send_text(resp)
            

class AITasks(generic.View):
    """docstring for AIResponse"""

    def get(self, request):
        """docstring for get"""
        pass

    # disable csrf cookies for bot
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        ret = {
            "speech": "",
            "displayText": "",
            "data": {},
            "contextOut": [],
            "source": ""
        }
        ai_req = json.loads(self.request.body.decode('utf-8'))
        user = User.objects.filter(id=int(ai_req['sessionId']))[0]
        pp.pprint(ai_req)
        intent = ai_req['result']['action']
        if intent == "get_schedule_for_day":
            date = ai_req['result']['parameters']['date']
            schedule = ScheduleItem.objects.all()
            if schedule:
                ret['speech'] = "Your schedule is: "
                for item in schedule:
                    ret['speech'] += item.name
                    ret['speech'] += " at "
                    ret['speech'] += item.date.strftime("%B %d, %Y at %I:%M%P") 
                    ret['speech'] += ", "
            else:
                ret['speech'] = "your schedule is empty on " + date

            pp.pprint(schedule)
        if intent == "get_schedule_for_duration":
            date = ai_req['result']['parameters']['date-period']
            ret['speech'] = "Getting your schedule for " + date
        if intent == "add_to_schedule":
            eventDate = ai_req['result']['parameters']['date-time']
            print(eventDate)
            event = ai_req['result']['parameters']['event']
            print(event)
            item = ScheduleItem(user=user, date=eventDate, name=event)
            item.save()
            ret['speech'] = "Added " + event + " at " + eventDate
        return HttpResponse(json.dumps(ret), content_type="application/json") 
