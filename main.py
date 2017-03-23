# -*- coding: utf-8 -*-
import StringIO
import json
import logging
import random
import urllib
import urllib2
import re

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
        #Commandos				
        if text.startswith('/'):
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
			    reply ('@braldt')
            elif text == '/devs':
                reply ('Gemaakt door @braldt met hulp van @notinecrafter. Regex toegevoegd door @pingiun, maar geef hem niet de schuld als het mis gaat. Ik sta op GitHub: https://github.com/TheSociallyAwkwardKing/braldtbot')
            elif text == '/f':
                reply ('Druk op F om uw respect te betuigen')
<<<<<<< HEAD
=======
		    elif text == '/bots':
                reply('BOTS KUNNEN BOTS NIET ZIEN')
            elif text == '/senable':
                reply('/S aan!')
                setEnabled(sarcasm, True)
            elif text == '/sdisable':
                reply('/S uit!')
                setEnabled(sarcasm, False)
>>>>>>> origin/master
				
        # in text
        if re.search(r'\bheineken\b)', text):
            reply('Heineken is paardenzeik.')
        elif re.search(r'\bbavaria\b', text):
            reply('Bavaria is slootwater.')
        elif re.search(r'\bamstel\b', text):
			reply('Amstel wordt letterlijk uit de Amstel gebotteld')
        elif re.search(r'\bbrand\b', text):
			reply ('Wat moet je doen als je Brand in de koelkast hebt?\nBrand eruit, Grolsch erin')
        elif re.search(r'\b(\/schouderophaal|\/shrug)\b', text):
            reply (u'¯\_(ツ)_/¯')
<<<<<<< HEAD
        elif re.search(r'(^|[^\w])\/bots([^\w]|$)', text):
            reply('BOTS KUNNEN BOTS NIET ZIEN')
        elif re.search(r'(^|[^\w])\/s([^\w]|$)', text):
=======
        elif getEnabled(sarcasm) and re.search(r'\b\/s\b', text):
>>>>>>> origin/master
			reply('DIT IS DUIDELIJK SARCASME TRAP DR NIET IN')
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
