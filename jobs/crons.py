from authentication.models import User
from investment.models import Investment, Profit, Portfolio
from date_time_literal import date_time_diff, DateDiff
from django.utils import timezone
from authentication.utils import Util
from loan.models import Loan
from wallet.models import Wallet
from piggyvest.models import Piggy
from investment.models import percentage
import math
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
import locale
import string
from authentication.models import Chat

# This function handles the automatic payments of profits
def payProfit():
    all_users = User.objects.all()
    users = [user for user in all_users if user.investment_set.filter(disabled=False).count() >= 1]
    for user in users:
        for investment in user.investment_set.filter(disabled=False):
            lastProfitDate = investment.last_profit_date
            dateTimeNow = timezone.localtime().now()
            if investment.portfolio.profit_frequency == "Weekly":
                if date_time_diff(dateTimeNow, lastProfitDate, 'd') >= 7:
                    amount = investment.interest()
                    Profit.objects.create(user=user, investment=investment, amount=amount)
                    investment.last_profit_date = timezone.localtime().now()
                    investment.save(update_fields=['last_profit_date'])
                    ctx = {
                        'fullname': f'{user.first_name} {user.last_name}',
                        'amount': amount
                    }
                    message = get_template('investment.html').render(ctx)
                    plain_message = strip_tags(message)
                    msg = EmailMultiAlternatives(
                        'Your Profit',
                        plain_message,
                        'Trix Fx <noreply@trixfx.com>',
                        [user.email],
                    )
                    msg.attach_alternative(message, "text/html")  # Main content is now text/html
                    msg.send()

            elif investment.portfolio.profit_frequency == "Monthly":
                if date_time_diff(dateTimeNow, lastProfitDate, 'd') >= 30:
                    amount = investment.interest()
                    print(amount)
                    Profit.objects.create(user=user, investment=investment, amount=amount)
                    investment.last_profit_date = timezone.localtime().now()
                    investment.save(update_fields=['last_profit_date'])
                    ctx = {
                        'fullname': f'{user.first_name} {user.last_name}',
                        'amount': amount
                    }
                    message = get_template('investment.html').render(ctx)
                    plain_message = strip_tags(message)
                    msg = EmailMultiAlternatives(
                        'Your Profit',
                        plain_message,
                        'Trix Fx <noreply@trixfx.com>',
                        [user.email],
                    )
                    msg.attach_alternative(message, "text/html")  # Main content is now text/html
                    msg.send()

            elif investment.portfolio.profit_frequency == "90 Days":
                if date_time_diff(dateTimeNow, lastProfitDate, 'd') >= 90:
                    amount = investment.interest()
                    Profit.objects.create(user=user, investment=investment, amount=amount)
                    investment.last_profit_date = timezone.localtime().now()
                    investment.save(update_fields=['last_profit_date'])
                    ctx = {
                        'fullname': f'{user.first_name} {user.last_name}',
                        'amount': amount
                    }
                    message = get_template('investment.html').render(ctx)
                    plain_message = strip_tags(message)
                    msg = EmailMultiAlternatives(
                        'Your Profit',
                        plain_message,
                        'Trix Fx <noreply@trixfx.com>',
                        [user.email],
                    )
                    msg.attach_alternative(message, "text/html")  # Main content is now text/html
                    msg.send()

            elif investment.portfolio.profit_frequency == "180 Days":
                if date_time_diff(dateTimeNow, lastProfitDate, 'd') >= 180:
                    amount = investment.interest()
                    Profit.objects.create(user=user, investment=investment, amount=amount)
                    investment.last_profit_date = timezone.localtime().now()
                    investment.save(update_fields=['last_profit_date'])
                    ctx = {
                        'fullname': f'{user.first_name} {user.last_name}',
                        'amount': amount
                    }
                    message = get_template('investment.html').render(ctx)
                    plain_message = strip_tags(message)
                    msg = EmailMultiAlternatives(
                        'Your Profit',
                        plain_message,
                        'Trix Fx <noreply@trixfx.com>',
                        [user.email],
                    )
                    msg.attach_alternative(message, "text/html")  # Main content is now text/html
                    msg.send()

            elif investment.portfolio.profit_frequency == "365 Days":
                if date_time_diff(dateTimeNow, lastProfitDate, 'd') >= 365:
                    amount = investment.interest()
                    Profit.objects.create(user=user, investment=investment, amount=amount)
                    investment.last_profit_date = timezone.localtime().now()
                    investment.save(update_fields=['last_profit_date'])
                    ctx = {
                        'fullname': f'{user.first_name} {user.last_name}',
                        'amount': amount
                    }
                    message = get_template('investment.html').render(ctx)
                    plain_message = strip_tags(message)
                    msg = EmailMultiAlternatives(
                        'Your Profit',
                        plain_message,
                        'Trix Fx <noreply@trixfx.com>',
                        [user.email],
                    )
                    msg.attach_alternative(message, "text/html")  # Main content is now text/html
                    msg.send()


def saving():
    piggies = Piggy.objects.all()
    for piggy in piggies:
        lastPiggyDate = piggy.updatedDate
        dateTimeNow = timezone.localtime().now()
        wallet = Wallet.objects.get(user=piggy.user)
        if piggy.frequency == "Weekly":
            if math.ceil(date_time_diff(dateTimeNow, lastPiggyDate, 'd')) >= 7:
                if piggy.status < piggy.duration:
                    if wallet.balance >= piggy.save_amount:
                        wallet.balance -= piggy.save_amount
                        piggy.amount_saved += piggy.save_amount
                        wallet.save(update_fields=["balance"])
                        piggy.save(update_fields=["amount_saved"])
                        piggy.updatedDate = timezone.localtime().now()
                        piggy.retry = False
                        piggy.status += 1
                        piggy.save(update_fields=['updatedDate', 'retry', 'status'])
                        ctx = {
                            'fullname': f'{piggy.user.first_name} {piggy.user.last_name}',
                            'amount': piggy.save_amount,
                            'plan': piggy.frequency,
                            'total': piggy.amount_saved
                        }
                        message = get_template('saving.html').render(ctx)
                        plain_message = strip_tags(message)
                        msg = EmailMultiAlternatives(
                            'Savings',
                            plain_message,
                            'Trix Fx <noreply@trixfx.com>',
                            [piggy.user.email],
                        )
                        msg.attach_alternative(message, "text/html")  # Main content is now text/html
                        msg.send()
                    else:
                        if piggy.retry:
                            piggy.incomplete = True
                            piggy.retry = False
                            piggy.status += 1
                            piggy.save()
                        else:
                            piggy.retry = True
                            piggy.save()
                            email_body = f"Hi {piggy.user.username}, add to your wallet to enable the system save the" \
                                         f" required amount per your request. Missing one payment would mean you " \
                                         f"wouldn't be eligible for the 3% bonus on your savings. " \
                                         f"Thank you for saving with Trix Fx. " \
                                         f" Have a wonderful day. \n "
                            data = {'email_body': email_body, 'to_email': piggy.user.email,
                                    'email_subject': 'Your Trix Savings'}
                            Util.send_email(data)
                        # Need to work out how this would work
                    # email_body = f"Hi {piggy.user.username}, your savings of ${piggy.amount_saved} for the week has been " \
                    #              f"added for you. " \
                    #              f"Thank you for saving with Cighedge. " \
                    #              f" Have a wonderful day. \n "
                    # data = {'email_body': email_body, 'to_email': piggy.user.email,
                    #         'email_subject': 'Your Cighedge Savings'}
                    # Util.send_email(data)

                elif piggy.status >= piggy.duration:

                    if not piggy.incomplete:
                        perc = percentage(3, piggy.amount_saved)
                        wallet.balance += piggy.amount_saved + perc
                        wallet.save(update_fields=['balance'])
                        piggy.delete()
                        email_body = f"Hi {piggy.user.username}, your savings of ${piggy.amount_saved} is complete, and have been " \
                                     f"added to your wallet. An additional 3% was equally added for being consistent. " \
                                     f"Thank you for saving with Trix Fx. " \
                                     f" Have a wonderful day. \n "
                        data = {'email_body': email_body, 'to_email': piggy.user.email,
                                'email_subject': 'Your Trix Savings'}
                        Util.send_email(data)
                    else:
                        wallet.balance += piggy.amount_saved
                        wallet.save(update_fields=['balance'])
                        piggy.delete()
                        email_body = f"Hi {piggy.user.username}, your savings of ${piggy.amount_saved} is complete and have been " \
                                     f"added to your wallet." \
                                     f"Thank you for saving with Trix Fx. " \
                                     f" Have a wonderful day. \n "
                        data = {'email_body': email_body, 'to_email': piggy.user.email,
                                'email_subject': 'Your Trix Savings'}
                        Util.send_email(data)

        elif piggy.frequency == "Monthly":
            if math.ceil(date_time_diff(dateTimeNow, lastPiggyDate, 'd')) >= 30:
                if piggy.status < piggy.duration:
                    if wallet.balance >= piggy.save_amount:
                        wallet.balance -= piggy.save_amount
                        piggy.amount_saved += piggy.save_amount
                        wallet.save(update_fields=["balance"])
                        piggy.save(update_fields=["amount_saved"])
                        piggy.updatedDate = timezone.localtime().now()
                        piggy.retry = False
                        piggy.status += 1
                        piggy.save(update_fields=['updatedDate', 'retry', 'status'])
                        ctx = {
                            'fullname': f'{piggy.user.first_name} {piggy.user.last_name}',
                            'amount': piggy.save_amount,
                            'plan': piggy.frequency,
                            'total': piggy.amount_saved
                        }
                        message = get_template('saving.html').render(ctx)
                        plain_message = strip_tags(message)
                        msg = EmailMultiAlternatives(
                            'Savings',
                            plain_message,
                            'Trix Fx <noreply@trixfx.com>',
                            [piggy.user.email],
                        )
                        msg.attach_alternative(message, "text/html")  # Main content is now text/html
                        msg.send()
                    else:
                        if piggy.retry:
                            piggy.incomplete = True
                            piggy.retry = False
                            piggy.status += 1
                            piggy.save()
                        else:
                            piggy.retry = True
                            piggy.save()
                            email_body = f"Hi {piggy.user.username}, add to your wallet to enable the system save the" \
                                         f" required amount per your request. Missing one payment would mean you " \
                                         f"wouldn't be eligible for the 3% bonus on your savings. " \
                                         f"Thank you for saving with Trix Fx. " \
                                         f" Have a wonderful day. \n "
                            data = {'email_body': email_body, 'to_email': piggy.user.email,
                                    'email_subject': 'Your Trix Savings'}
                        # Need to work out how this would work
                    # email_body = f"Hi {piggy.user.username}, your savings of ${piggy.amount_saved} for the month has been " \
                    #              f"added for you. " \
                    #              f"Thank you for saving with Cighedge. " \
                    #              f" Have a wonderful day. \n "
                    # data = {'email_body': email_body, 'to_email': piggy.user.email,
                    #         'email_subject': 'Your Cighedge Savings'}
                    # Util.send_email(data)

                elif piggy.status >= piggy.duration:

                    if not piggy.incomplete:
                        perc = percentage(3, piggy.amount_saved)
                        wallet.balance += piggy.amount_saved + perc
                        wallet.save(update_fields=['balance'])
                        piggy.delete()
                        email_body = f"Hi {piggy.user.username}, your savings of ${piggy.amount_saved} is complete, and have been " \
                                     f"added to your wallet. An additional 3% was equally added for being consistent." \
                                     f" Thank you for saving with Trix Fx. " \
                                     f" Have a wonderful day. \n "
                        data = {'email_body': email_body, 'to_email': piggy.user.email,
                                'email_subject': 'Your Trix Savings'}
                        Util.send_email(data)
                    else:
                        wallet.balance += piggy.amount_saved
                        wallet.save(update_fields=['balance'])
                        piggy.delete()
                        email_body = f"Hi {piggy.user.username}, your savings of ${piggy.amount_saved} is complete and have been " \
                                     f"added to your wallet." \
                                     f"Thank you for saving with Trix Fx. " \
                                     f" Have a wonderful day. \n "
                        data = {'email_body': email_body, 'to_email': piggy.user.email,
                                'email_subject': 'Your Trix Savings'}
                        Util.send_email(data)


# Test to show how date-time-literal works.
# I use this module a lot to easily compare times. I created and maintain the package
def test():
    return "test"


def repayLoan():
    dateTimeNow = timezone.localtime().now()
    loans = Loan.objects.all()
    for loan in loans:
        if date_time_diff(dateTimeNow, loan.date, 'd') >= 183:
            wallet = Wallet.objects.get(user=loan.user)
            if wallet.balance >= loan.amount > 0:
                wallet.balance = wallet.balance - loan.amount
                wallet.save(update_fields=['balance'])
                loan.amount = 0
                loan.save(update_fields=['amount'])


def updateMessages():
    dateTimeNow = timezone.localtime().now()
    messages = Chat.objects.all()
    for message in messages:
        if date_time_diff(message.date, dateTimeNow, 'd') >= 1:
            message.delete()

# Write a cron job to save
