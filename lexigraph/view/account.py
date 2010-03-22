from google.appengine.api import mail

from lexigraph.view import add_route
from lexigraph.handler import AccountHandler, SessionHandler, InteractiveHandler
from lexigraph import model
from lexigraph.model import maybe_one
from lexigraph import config
import lexigraph.mail

class NewAccount(AccountHandler):

    requires_login = True

    def post(self):
        account_name = self.request.get('account_name')
        if not account_name:
            self.redirect('/new/account')
        else:
            account = model.Account.create(account_name, self.user)
            model.ActiveAccount.set_active_account(self.user, account)
            try:
                self.send_welcome_email(account)
                self.session['info_message'] = 'Welcome to Lexigraph! A confirmation email will arrive shortly.'
            except:
                self.log.exception('Failed to send welcome email to account: %s' % (account.encode(),))
            self.redirect('/dashboard')

    def send_welcome_email(self):
        sender_address = 'support@lexigraph.appspot.com'
        subject = 'Welcome to Lexigraph'
        body = """
Thank you creating an account at Lexigraph!

For future reference, your account id is: %(account_id)s.  If you experience
any problems with your account, you can help us by including your account id
in the support request email.

Thanks!

-- The Lexigraph Team
""" % {'account_id': account.encode()}
        mail.send_mail(sender=lexigraph.mail.support_address,
                       to=account.owner.email(),
                       bcc=lexigraph.mail.support_address,
                       subject='Welcome to Lexigraph!',
                       body=body.strip())

class ChooseAccount(SessionHandler):

    requires_login = True

    def post(self):
        # XXX: no security here!
        name = self.form_required('account')
        account = maybe_one(model.Account.all().filter('name =', name))
        if account:
            model.ActiveAccount.set_active_account(self.user, account)
            self.redirect('/dashboard')
        else:
            self.session['error_message'] = 'invalid choice'
            self.redirect('/choose/account')

class UpdateAccount(InteractiveHandler):

    requires_login = True

    def get(self):
        mail = self.user.email()
        if config.whitelisted_emails and mail not in config.whitelisted_emails:
            self.session['error_message'] = 'Sorry, your email (%s) hasn\'t been whitelisted. Ask Evan if you need access.' % (mail,)
            self.redirect('/')
        self.env['accounts'] = list(model.Account.all().filter('owner =', self.user))
        self.env['support_address'] = lexigraph.mail.support_address
        self.render_template('account.html')


add_route(NewAccount, '/new/account')
add_route(ChooseAccount, '/choose/account')
add_route(UpdateAccount, '/account')
