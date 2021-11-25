import stripe
import os
from core_lib.pronto_conf import *
from core_lib.platform_utils import *
from core_lib.mongo_utils import *
from core_lib.email_utils import *
import datetime
from dateutil.relativedelta import relativedelta

def get_customer_and_subscription(response_obj,logger):
    stripe_customer_id = str(response_obj.get('customer',None))
    stripe_subscription_id = str(response_obj.get('subscription',''))
    if len(stripe_subscription_id) == 0:
        logger.debug('SUBCRIPTION ID is NONE')
        stripe_subscription_id = str(response_obj.get('id',''))
        logger.debug(f'SUBCRIPTION ID AFTER = {stripe_subscription_id}')
    return stripe_customer_id, stripe_subscription_id    

def get_error_response(e,logger):
    logger.error(f'Error Type = {e.type}')
    logger.error(f'HTTP error status = {e.http_status}')
    
    if e.user_message:
          logger.error(f'user_message = {e.user_message}')
          errorMessage = e.user_message
    elif e.message:
          logger.error(f'message = {e.message}')
          errorMessage = e.message
    else:
        if e.param:
           errorMessage = 'Bad Request with parameter {e.param}'
        elif e.type == stripe.error.RateLimitError:
              errorMessage = 'Too many requests made to the Stripe API too quickly. Please Try Again after a while'
    if e.param:
       logger.error(f'error param = {e.param}')
    if e.code:
       logger.error(f'error code = {e.code}')
    return {
                  
                    'status': 'failed',
                    'errorType': str(e.type),
                    'errorMessage': errorMessage
           }    
    
def stripe_cancel_subscription(subscription_id,logger):
    stripe.api_key = STRIPE_SECRET_KEY
    #return stripe.Subscription.delete(subscription_id)
    try:
      # Use Stripe's library to make requests...
      res = stripe.Subscription.modify(subscription_id,cancel_at_period_end=True)
      return {
                'status': 'success'
             }   
    except Exception as e:
       return  get_error_response(e,logger)
    
    
def stripe_get_payment_method(setup_id):
    api_key = STRIPE_SECRET_KEY
    if api_key is None:
        print('stripe_get_payment_method: api key not found in environment')
        return None
    stripe.api_key = api_key
    try:
        intent = stripe.SetupIntent.retrieve(setup_id)
        return intent['data']['object']['payment_method']
    except Exception as e:
        return  get_error_response(e,logger)
        
    
def stripe_create_customer(email,name,address,phone,payment_method_id=None):
    address_dict = {}
    address_dict['line1'] = address.line1
    address_dict['line2'] = address.line2
    address_dict['city'] = address.city
    address_dict['state'] = address.state
    address_dict['country'] = address.country
    address_dict['postal_code'] = address.postal_code
    
    api_key = STRIPE_SECRET_KEY
    if api_key is None:
        print('stripe_create_customer: api key not found in environment')
        return None
    
    stripe.api_key = api_key
    try:
        if payment_method_id is not None:
            invoice_settings = {}
            invoice_settings.default_payment_method = payment_method_id
            resp = stripe.Customer.create(
                                        email=email,
                                        name=name,
                                        address=address_dict,
                                        phone=phone,
                                        invoice_settings=invoice_settings,
                                        payment_method=payment_method_id)
        else:
            resp = stripe.Customer.create(
                                        email=email,
                                        name=name,
                                        address=address,
                                        phone=phone
                                        )
        return resp
    except Exception as e:
        return  get_error_response(e,logger)
        
    
    
def handle_subscription_success(checkout_obj,logger):
    email = checkout_obj.get('customer_email',None)
    stripe_customer_id,stripe_subscription_id = get_customer_and_subscription(response_obj,logger)
    logger.debug(f'$$$$$$$$$ CUSTOMER ID = {stripe_customer_id}, SUBSCRIPTION ID = {stripe_subscription_id}')
    logger.debug('STRIPE HANDLE SUBSCRIPTION SUCCESS--CHECKOUT OBJECT')
    logger.debug(checkout_obj)
    if email is None:
        logger.error('HANDLE SUBSCRIPTION RESULT: NO EMAIL FOUND')
        logger.error("email id not found when completing subscription")
        return
    #setup_id = checkout_obj["setup_intent"]
    user = get_user_profile(email)
    if user is None:
        logger.error("error getting user profile when handling Stripe Webhook")
        return
    
    #stripe_pm_id = stripe_get_payment_method(setup_id)
    
    #name = user.business_info.company_name
    #address = user.business_info.address
    #phone = user.business_info.phone
    
    #stripe_cust = stripe_create_customer(email,name,address,phone,payment_method_id=stripe_pm_id)
    #cust_id = stripe_cust['id']
    user.status = 'active'
    user.last_billing_date = datetime.datetime.utcnow() 
    
    #user.subscription_plan_id = stripe_price_id
    user.subscription_customer_id = stripe_customer_id
    user.subscription_id = stripe_subscription_id
    email = user.email
    user.save()
    ret = send_signup_notify_email(email)
    return send_welcome_email(email)
        
def handle_monthly_payment_success(response_obj,logger):
    stripe_customer_id,stripe_subscription_id = get_customer_and_subscription(response_obj,logger)
       
    if stripe_customer_id is None:
        logger.error('NO CUSTOMER ID FOUND')
        return
    if stripe_subscription_id is None:
       stripe_subscription_id = str(response_obj.get('id',None))
    
    logger.debug(f'$$$$$$$$$ CUSTOMER ID = {stripe_customer_id}, SUBSCRIPTION ID = {stripe_subscription_id}')
    user = get_user_profile_by_subscription(stripe_customer_id,stripe_subscription_id)
    if user is None:
        logger.error(f"status:error")
        logger.error("error getting user profile when handling Stripe Webhook for monthly payment success")
        return
    if user.status != 'active':
        user.status = 'active'
    user.last_billing_date = datetime.datetime.utcnow()    
    #user.subscription_plan_id = stripe_price_id
    email = user.email
    user.save()
    return send_payment_success_email(email)

def handle_monthly_payment_failed(response_obj,logger):
    stripe_customer_id,stripe_subscription_id = get_customer_and_subscription(response_obj,logger)
    if stripe_customer_id is None:
        logger.error('NO CUSTOMER ID FOUND')
        return
    if stripe_subscription_id is None:
        logger.error('NO SUBSCRIPTION ID FOUND')
        return
    logger.debug(f'$$$$$$$$$ CUSTOMER ID = {stripe_customer_id}, SUBSCRIPTION ID = {stripe_subscription_id}')
    user = get_user_profile_by_subscription(stripe_customer_id,stripe_subscription_id)
    if user is None:
        logger.error("error getting user profile when handling Stripe Webhook for monthly payment failed")
        return
    if user.status == 'active':
        endpoint = WEBSITE_SIGNIN
    else:
        endpoint = WEBSITE_SIGNUP
    if BLOCK_USER_ON_PAYMENT_FAILED:
        user.status = 'blocked'
        user.blocking_date = datetime.datetime.now()
    #user.subscription_plan_id = stripe_price_id
    email = user.email
    
    user.save()
    return send_payment_failed_email(email,endpoint)
        
def handle_subscription_cancelled(response_obj,logger):
    stripe_customer_id,stripe_subscription_id = get_customer_and_subscription(response_obj,logger)
    if stripe_customer_id is None:
        logger.error('NO CUSTOMER ID FOUND')
        return
    if stripe_subscription_id is None:
        logger.error('NO SUBSCRIPTION ID FOUND')
        return
    logger.debug(f'$$$$$$$$$ CUSTOMER ID = {stripe_customer_id}, SUBSCRIPTION ID = {stripe_subscription_id}')
    user = get_user_profile_by_subscription(stripe_customer_id,stripe_subscription_id)
    if user is None:
        logger.error("error getting user profile when handling Stripe Webhook for subscription cancelled")
        return
    email = user.email
    user.status = 'cancelled'
    user.cancellation_date = datetime.datetime.now()
    user.save()
    return send_subscription_cancelled_email(email,WEBSITE_SIGNIN)    

def handle_subscription_renewed(response_obj,logger):
    stripe_customer_id,stripe_subscription_id = get_customer_and_subscription(response_obj,logger)
    if stripe_customer_id is None:
        logger.error('NO CUSTOMER ID FOUND')
        return
    if stripe_subscription_id is None:
        logger.error('NO SUBSCRIPTION ID FOUND')
        return
    logger.debug(f'$$$$$$$$$ CUSTOMER ID = {stripe_customer_id}, SUBSCRIPTION ID = {stripe_subscription_id}')
    user = get_user_profile_by_subscription(stripe_customer_id,stripe_subscription_id)
    if user is None:
        logger.error("error getting user profile when handling Stripe Webhook for subscription renewed")
        return
    email = user.email
    user.status = 'active'
    user.resumed_date = datetime.datetime.now()
    user.save()
    return send_subscription_resumed_email(email,WEBSITE_SIGNIN)    

def handle_subscription_deleted(response_obj,logger):
    stripe_customer_id,stripe_subscription_id = get_customer_and_subscription(response_obj,logger)
    if stripe_customer_id is None:
        logger.error('NO CUSTOMER ID FOUND')
        return
    if stripe_subscription_id is None:
        logger.error('NO SUBSCRIPTION ID FOUND')
        return
    
    user = get_user_profile_by_subscription(stripe_customer_id,stripe_subscription_id)
    if user is None:
        logger.error("error getting user profile when handling Stripe Webhook for subscription deleted")
        return
    email = user.email
    
    set_user_delete_status(user)
    
    return send_subscription_deletion_email(email,WEBSITE_SIGNUP)    

def handle_subscription_paused(response_obj,logger):
    stripe_customer_id,stripe_subscription_id = get_customer_and_subscription(response_obj,logger)
   
    if stripe_customer_id is None:
        logger.error('NO CUSTOMER ID FOUND')
        return
    if stripe_subscription_id is None:
        logger.error('NO SUBSCRIPTION ID FOUND')
        return
    logger.debug(f'$$$$$$$$$ CUSTOMER ID = {stripe_customer_id}, SUBSCRIPTION ID = {stripe_subscription_id}')
    user = get_user_profile_by_subscription(stripe_customer_id,stripe_subscription_id)
    if user is None:
        logger.error(f"status:error")
        logger.error("error getting user profile when handling Stripe Webhook for subscription paused")
        return
    email = user.email
    user.status = 'paused'
    user.paused_date = datetime.datetime.now()
    user.save()
    return send_subscription_paused_email(email,WEBSITE_SIGNIN)    
    
def handle_subscription_resumed(response_obj,logger):
    stripe_customer_id,stripe_subscription_id = get_customer_and_subscription(response_obj,logger)
    if stripe_customer_id is None:
        logger.error('NO CUSTOMER ID FOUND')
        return
    if stripe_subscription_id is None:
        logger.error('NO SUBSCRIPTION ID FOUND')
        return
    logger.debug(f'$$$$$$$$$ CUSTOMER ID = {stripe_customer_id}, SUBSCRIPTION ID = {stripe_subscription_id}')
    user = get_user_profile_by_subscription(stripe_customer_id,stripe_subscription_id)
    if user is None:
        logger.error("error getting user profile when handling Stripe Webhook for subscription resumed")
        return
    email = user.email
    user.status = 'active'
    user.resumed_date = datetime.datetime.now()
    user.save()
    return send_subscription_resumed_email(email,WEBSITE_SIGNIN)    
    
def handle_subscription_trial_period_start(response_obj,logger):
    stripe_customer_id,stripe_subscription_id = get_customer_and_subscription(response_obj,logger)
    if stripe_customer_id is None:
        logger.error('NO CUSTOMER ID FOUND')
        return
    if stripe_subscription_id is None:
        logger.error('NO SUBSCRIPTION ID FOUND')
        return
    logger.debug(f'$$$$$$$$$ CUSTOMER ID = {stripe_customer_id}, SUBSCRIPTION ID = {stripe_subscription_id}')
    user = get_user_profile_by_subscription(stripe_customer_id,stripe_subscription_id)
    if user is None:
        logger.error("error getting user profile when handling Stripe Webhook for subscription trial period starts")
        return
    email = user.email
    user.status = 'active'
    current_time = datetime.datetime.now()
    current_timestamp = int(datetime.datetime.timestamp(current_time))
    period_start_timestamp = response_obj.get('period_start',current_timestamp)
    period_start_time = datetime.datetime.fromtimestamp(period_start_timestamp)
    period_end_time = period_start_time + relativedelta(months=+1)
    user.trial_start_date = period_start_time
    user.trial_end_date = period_end_time
    user.last_billing_date = period_start_time
    user.save()
    return send_subscription_trial_start_email(email,str(period_end_time.date()),WEBSITE_SIGNIN)    

    
def stripe_attach_payment_method():
    pass

def stripe_charge_customer():
    pass

def stripe_delete_customer():
    pass

    