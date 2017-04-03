#!/usr/bin/env python
import os
import jinja2
import webapp2
import cgi

from google.appengine.api import users

from models import Opinion

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}

        user = users.get_current_user()
        params["user"] = user

        if user:
            logged_in = True
            logout_url = users.create_logout_url('/')
            params["logout_url"] = logout_url
        else:
            logged_in = False
            login_url = users.create_login_url('/')
            params["login_url"] = login_url

        params["logged_in"] = logged_in

        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        return self.render_template("index.html")

class LogInHadnler(BaseHandler):
    def get(self):
        return self.render_template("login.html")

class BlogHandler(BaseHandler):
    def get(self):
        return self.render_template("blog.html")

class ContactHandler(BaseHandler):
    def get(self):
        return self.render_template("contact.html")

class GuestBookHandler(BaseHandler):
    def get(self):
        return self.render_template("guestbook.html")

class SaveHandler(BaseHandler):
    def post(self):
        user = users.get_current_user()
        if user:
            name = user.nickname()
            email = user.email()
            opinion = cgi.escape(self.request.get("opinion"))
            save_opinion = Opinion(first_last_name=name, email=email, opinion=opinion)
            save_opinion.put()
            return self.render_template("saved.html")

class AllOpinionsHandler(BaseHandler):
    def get(self):
        opinions = Opinion.query(Opinion.deleted == False).fetch()
        params = {"opinions": opinions}
        return self.render_template("opinions.html", params)

class EachOpinionHandler(BaseHandler):
    def get(self, opinion_id):
        opinion = Opinion.get_by_id(int(opinion_id))
        params = {"opinion": opinion}
        return self.render_template("opinions-details.html", params)

class EditOpinionHandler(BaseHandler):
    def get(self, opinion_id):
        opinion = Opinion.get_by_id(int(opinion_id))
        params = {"opinion": opinion}
        return self.render_template("edit-opinion.html", params)

    def post(self, opinion_id):
        opinion = Opinion.get_by_id(int(opinion_id))
        opinion.name = self.request.get("name")
        opinion.email = self.request.get("email")
        opinion.opinion = self.request.get("opinion")
        opinion.put()
        return self.redirect("/opinions")

class DeleteOpinionHandler(BaseHandler):
    def get(self, opinion_id):
        opinion = Opinion.get_by_id(int(opinion_id))
        params = {"opinion": opinion}
        return self.render_template("delete-opinion.html", params)

    def post(self, opinion_id):
        opinion = Opinion.get_by_id(int(opinion_id))
        opinion.deleted = True
        opinion.put()
        return self.redirect("/opinions")

class DeletedOpinionsHandler(BaseHandler):
    def get(self):
        if not users.is_current_user_admin():
            return self.write("You are not admin!")
        del_opins = Opinion.query(Opinion.deleted == True).fetch()
        params = {"del_opins": del_opins}
        return self.render_template("deleted-opinions.html", params)

class RestoreOpinionHandler(BaseHandler):
    def get(self, opinion_id):
        if not users.is_current_user_admin():
            return self.write("You are not admin!")
        opinion = Opinion.get_by_id(int(opinion_id))
        params = {"opinion": opinion}
        return self.render_template("restore-opinion.html", params)

    def post(self, opinion_id):
        opinion = Opinion.get_by_id(int(opinion_id))
        opinion.deleted = False
        opinion.put()
        return self.redirect("/opinions")

class CompleteDeleteOpinionHandler(BaseHandler):
    def get(self, opinion_id):
        if not users.is_current_user_admin():
            return self.write("You are not admin!")
        opinion = Opinion.get_by_id(int(opinion_id))
        params = {"opinion": opinion}
        return self.render_template("complete-delete.html", params)

    def post(self, opinion_id):
        opinion = Opinion.get_by_id(int(opinion_id))
        opinion.key.delete()
        return self.redirect("/deleted")

app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/saved', SaveHandler),
    webapp2.Route('/login', LogInHadnler),
    webapp2.Route('/blog', BlogHandler),
    webapp2.Route('/contact', ContactHandler),
    webapp2.Route('/guestbook', GuestBookHandler),
    webapp2.Route('/opinions', AllOpinionsHandler),
    webapp2.Route('/opinions-details/<opinion_id:\d+>', EachOpinionHandler),
    webapp2.Route('/opinions-details/<opinion_id:\d+>/edit', EditOpinionHandler),
    webapp2.Route('/opinions-details/<opinion_id:\d+>/delete', DeleteOpinionHandler),
    webapp2.Route('/deleted', DeletedOpinionsHandler),
    webapp2.Route('/opinions-details/<opinion_id:\d+>/restore', RestoreOpinionHandler),
    webapp2.Route('/opinions-details/<opinion_id:\d+>/complete', CompleteDeleteOpinionHandler),
], debug=True)
