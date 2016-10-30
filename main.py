import StringIO
import json
import logging
import random
import urllib
import urllib2

# for sending images
from PIL import Image
import multipart

# standard app engine imports
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2

token = open('token.txt', 'r')
token = token.read()

BASE_URL = 'https://api.telegram.org/bot' + token + '/'


# ================================

class EnableStatus(ndb.Model):
    # key name: str(chat_id)
    enabled = ndb.BooleanProperty(indexed=False, default=False)


# ================================

def setEnabled(chat_id, yes):
    es = EnableStatus.get_or_insert(str(chat_id))
    es.enabled = yes
    es.put()

def getEnabled(chat_id):
    es = EnableStatus.get_by_id(str(chat_id))
    if es:
        return es.enabled
    return False


# ================================

class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))


class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates'))))


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))


class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        logging.info('request body:')
        logging.info(body)
        self.response.write(json.dumps(body))

        update_id = body['update_id']
        try:
            message = body['message']
        except:
            message = body['edited_message']
        message_id = message.get('message_id')
        date = message.get('date')
        text = message.get('text')
        fr = message.get('from')
        chat = message['chat']
        chat_id = chat['id']

        if not text:
            logging.info('no text')
            return

        text = text.lower()
        
        if '@braldtbot' in text:
            text = text.replace('@braldtbot', '')
        
        def reply(msg=None, img=None):
            if msg:
                resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
                    'chat_id': str(chat_id),
                    'text': msg.encode('utf-8'),
                    'disable_web_page_preview': 'true',
                    'reply_to_message_id': str(message_id),
                })).read()
            elif img:
                resp = multipart.post_multipart(BASE_URL + 'sendPhoto', [
                    ('chat_id', str(chat_id)),
                    ('reply_to_message_id', str(message_id)),
                ], [
                    ('photo', 'image.jpg', img),
                ])
            else:
                logging.error('no msg or img specified')
                resp = None

            logging.info('send response:')
            logging.info(resp)

        if '/s 'in text or ' /s' in text or text == '/s':
            reply('DIT IS DUIDELIJK SARCASME TRAP DR NIET IN')
        #Commandos		
        elif text.startswith('/'):
            if text == '/start':
                reply('Hallo! Ik ben BraldtBot. Ik ben net zoals Braldt niet heel erg nuttig.')
                setEnabled(chat_id, True)
            elif text == '/stop':
                reply('Dag hoor!')
                setEnabled(chat_id, False)
            elif text == '/hjb':
                reply('Luister, ik weet niet hoe ik dit het beste moet zeggen, dus ik doe het maar gewoon. Ik zou het erg waarderen als je nu heel snel je bek zou houden.')
            elif text == '/hjk':
                reply('Luister, ik weet niet hoe ik dit het beste moet zeggen, dus ik doe het maar gewoon. Ik zou het erg waarderen als je nu heel snel je kek zou houden.')
            elif text == '/test':
                reply('Niet stuk.')
            elif text == '/haltbraldt':
                reply('JE KUNT DE BRALDT NIET HALTEN')
            elif text == '/braldt':
                reply('Is heel erg knap, en niet te halten.')
            elif text == '/devs':
                reply ('Gemaakt door @braldt met hulp van @notinecrafter. Ik sta op GitHub: https://github.com/TheSociallyAwkwardKing/braldtbot')
            elif text == '/f':
                reply ('Druk op F om uw respect te betuigen')
            elif text == '/schouderophaal' or text == '/shrug':
                reply ('¯\\_(ツ)_/¯')

        # in text
        elif ' heineken'in text or 'heineken ' in text or text == 'heineken':
            reply('Heineken is paardenzeik.')
        elif ' bavaria'in text or 'bavaria ' in text or text == 'bavaria':
            reply('Bavaria is slootwater.')
        elif ' amstel'in text or 'amstel ' in text or text == 'amstel':
			reply('Amstel wordt letterlijk uit de Amstel gebotteld')
        elif (' brand' in text or 'brand ' in text or text == 'brand') and not ('hillebrand' in text):
			reply('Wat moet je doen als je Brand in de koelkast hebt? \n Brand eruit, Grolsch erin')

        else:
            if getEnabled(chat_id):
                reply('Lolwat')
            else:
                logging.info('not enabled for chat_id {}'.format(chat_id))

app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
], debug=True)
