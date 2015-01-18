import os
import jinja2
import webapp2
import random
import csv

from helper_functions import *

from google.appengine.ext import db
from google.appengine.ext import ndb
from google.appengine.api import mail


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))



########################################3
##
##
## Databases
##
##
########################################3

#create users database:
class Account(ndb.Model):
	username = ndb.StringProperty()
	email = ndb.StringProperty()
	work_email = ndb.StringProperty()
	first_name = ndb.StringProperty()
	last_name = ndb.StringProperty()
	first_last = ndb.StringProperty()
	game_dict1v1 = ndb.TextProperty()
	game_id_list1v1 = ndb.TextProperty()
	game_dict2v2 = ndb.TextProperty()
	game_id_list2v2 = ndb.TextProperty()

	win_streak1v1 = ndb.IntegerProperty()
	total_points1v1 = ndb.IntegerProperty()
	ranking1v1 = ndb.FloatProperty()
	dict1v1_t0 = ndb.TextProperty()
	dict1v1_sum = ndb.TextProperty()

#######################
###
### Helper Functions
###
#######################

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


class Handler(webapp2.RequestHandler):
    def render(self, template, **kw):
        self.response.out.write(render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)


#######################
###
### Web classes
###
#######################




class Mail(Handler):
	def get(self):

		message = mail.EmailMessage(sender="Foos Master <eabfoosball@gmail.com>",
		                            subject="Your Weekly Update")

		message.to = "<jacob.rosch@gmail.com>"
		message.body = """
		Dear Albert:

		Your example.com account has been approved.  You can now visit
		http://www.example.com/ and sign in using your Google Account to
		access new features.

		Please let us know if you have any questions.

		The example.com Team
		"""

		message.send()

		data = 'hello'


		self.render('tester.html', data1 = data)

class Tester(Handler):
	def get(self):

		qry = Account.query()

		for row in qry:
			row.win_streak1v1 = 0
			row.total_points1v1 = 0
			row.ranking1v1 = 450
			row.dict1v1_sum = row.game_dict1v1
			row.dict1v1_t0 = row.game_dict1v1

			row.put()


		self.render('tester.html')


application = webapp2.WSGIApplication([('/_min/mail', Mail),
									   ('/_min/tester', Tester)],
									    debug=True)
