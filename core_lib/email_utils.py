
from sendgrid import HtmlContent
import os
import traceback
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email
from python_http_client.exceptions import HTTPError
from core_lib.pronto_conf import *

def send_email(msg,from_,to_,subject):
    msg = HtmlContent(msg)
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        message = Mail(
            to_emails=to_,
            from_email=Email(from_, "Get-Pronto Team"),
            subject=subject,
            html_content=msg
            )
        #message.add_bcc(from_)
        response = sg.send(message)
        return f"email.status_code={response.status_code}"
    except HTTPError as e:
        raise e.message

def send_welcome_email(email,pw=None):
    from_ = WELCOME_EMAIL_SENDER
    pronto_website = WEBSITE_URL+WEBSITE_SIGNIN
    to_ = email
    subject = 'Welcome to Get-Pronto'
    if pw is not None:
        msg = f'Welcome to Get-Pronto, Your account is active. Your temporary password is {pw}. You can change your password after you login first time. <br>Start creating amazing videos<br><a href='+pronto_website+'>Click Here to Login</a> '
    else:
        msg = 'Welcome to Get-Pronto, Your account is active <br>Start creating amazing videos<br><a href='+pronto_website+'>Click Here to Login</a> '
    try:
        send_email(msg,from_,to_,subject)
        return 'success'
    except Exception as e:
        print(f'failed to send email with error {e}')
        print(traceback.format_exc())
        return 'failed'

def send_signup_notify_email(email):
    from_ = WELCOME_EMAIL_SENDER
    to_ = WELCOME_EMAIL_SENDER
    subject = 'Pronto Alert: New User Signup'
    msg = f'New User {email} signed up successfully to Pronto using Stripe'
    try:
        send_email(msg,from_,to_,subject)
        return 'success'
    except Exception as e:
        print(f'failed to send email with error {e}')
        print(traceback.format_exc())
        return 'failed'
    
def send_reset_password(email,pw):
    from_ = PASSWORD_RESET_EMAIL_SENDER
    pronto_website = WEBSITE_URL+WEBSITE_SIGNIN
    to_ = email
    subject = 'Your Password has been reset'
    msg = f'Your password has been reset by Pronto Administrator. Your New temporary password is {pw}. You can change your password after logging in with this password<br>Continue creating amazing videos<br><a href='+pronto_website+'>Click Here to Login</a> '
    try:
        send_email(msg,from_,to_,subject)
        return 'success'
    except Exception as e:
        print(f'failed to send email with error {e}')
        print(traceback.format_exc())
        return 'failed'


def send_payment_success_email(email):
    from_ = PAYMENT_EMAIL_SENDER
    pronto_website =  WEBSITE_URL+WEBSITE_SIGNIN
    to_ = email
    subject = 'Your payment has been received' 
    msg = 'Thank you for your Payment.<br>Keep creating amazing videos<br><a href='+pronto_website+'>Click Here to Login</a> '
    try:
        send_email(msg,from_,to_,subject)
        return 'success'
    except Exception as e:
        print(f'failed to send email with error {e}')
        print(traceback.format_exc())
        return 'failed'

def send_payment_failed_email(email,endpoint):
    from_ = PAYMENT_EMAIL_SENDER
    pronto_website = WEBSITE_URL+endpoint
    to_ = email
    subject = 'Payment Processing Failed'
    msg = 'There was a problem while processing your payment<br>Please go to our Website to change or update your payment method<br><a href='+pronto_website+'>Click Here to Login</a> '
    try:
        send_email(msg,from_,to_,subject)
        return 'success'
    except Exception as e:
        print(f'failed to send email with error {e}')
        print(traceback.format_exc())
        return 'failed'

def send_subscription_cancelled_email(email,endpoint):
    from_ = PAYMENT_EMAIL_SENDER
    pronto_website = WEBSITE_URL+endpoint
    to_ = email
    subject = 'Subscription Cancelled'
    msg = 'Your Subscription has been cancelled<br>Your can continue to use Pronto Services till the end of your subscription period<br>'
    try:
        send_email(msg,from_,to_,subject)
        return 'success'
    except Exception as e:
        print(f'failed to send email with error {e}')
        print(traceback.format_exc())
        return 'failed'

def send_subscription_paused_email(email,endpoint):
    from_ = PAYMENT_EMAIL_SENDER
    pronto_website = WEBSITE_URL+endpoint
    to_ = email
    subject = 'Subscription Suspended'
    msg = 'Your Subscription has been Suspended as per your request<br>Your can Resume Your subscription any time by logging in to <br><a href='+pronto_website+'>Pronto Signin</a>'
    try:
        send_email(msg,from_,to_,subject)
        return 'success'
    except Exception as e:
        print(f'failed to send email with error {e}')
        print(traceback.format_exc())
        return 'failed'

def send_subscription_resumed_email(email,endpoint):
    from_ = PAYMENT_EMAIL_SENDER
    pronto_website = WEBSITE_URL+endpoint
    to_ = email
    subject = 'Subscription Resumed'
    msg = 'Your Subscription has been Resumed<br>Enjoy From where you left off any time by logging in to <br><a href='+pronto_website+'>Pronto Signin</a>'
    try:
        send_email(msg,from_,to_,subject)
        return 'success'
    except Exception as e:
        print(f'failed to send email with error {e}')
        print(traceback.format_exc())
        return 'failed'
    

def send_subscription_deletion_email(email,endpoint):
    from_ = PAYMENT_EMAIL_SENDER
    pronto_website = WEBSITE_URL+endpoint
    to_ = email
    subject = 'Subscription Cancellation Complete'
    msg = 'Your subscription has been deleted<br>You can re-join Pronto any time. Your current data will not be available after 30 calendar days<br>'
    try:
        send_email(msg,from_,to_,subject)
        return 'success'
    except Exception as e:
        print(f'failed to send email with error {e}')
        print(traceback.format_exc())
        return 'failed'
    
def send_subscription_trial_start_email(email,trial_end_date,endpoint):
    from_ = SUPPORT_EMAIL_SENDER
    pronto_website = WEBSITE_URL+endpoint
    to_ = email
    subject = 'GET-PRONTO: Trial Period Started'
    msg = f'Hello: Your 30-Day Trial Period has Started. This Trial will end on {trial_end_date}. Start making amazing Videos by logging in to <br><a href='+pronto_website+'>Pronto Signin</a>'
    try:
        send_email(msg,from_,to_,subject)
        return 'success'
    except Exception as e:
        print(f'failed to send email with error {e}')
        print(traceback.format_exc())
        return 'failed'
    
    
    
def send_pw_code_email(email,code):
    from_ = SUPPORT_EMAIL_SENDER
    to_ = email
    subject = 'GET-PRONTO: password reset code'
    msg = f'Hello: Your Password reset Code is {code}'
    try:
        send_email(msg,from_,to_,subject)
        return 'success'
    except Exception as e:
        print(f'failed to send email with error {e}')
        print(traceback.format_exc())
        return 'failed'

def send_confirm_code_email(email,code):
    from_ = SUPPORT_EMAIL_SENDER
    to_ = email
    subject = 'GET-PRONTO: Email Confirmation code'
    msg = f'Hello: Your Email Confirmation Code is {code}'
    try:
        send_email(msg,from_,to_,subject)
        return 'success'
    except Exception as e:
        print(f'failed to send email with error {e}')
        print(traceback.format_exc())
        return 'failed'
        

