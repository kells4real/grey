import datetime
from date_time_literal import date_time_diff, date_diff
from authentication.models import Student, AcademicSession, CurrentSession, School
from django.utils import timezone
from settings.models import CurrentTerm, SchoolSettings
from school_calendar.models import Event
from fees.models import Fees, StudentWallet, ClassFees
from .utils import Util
# import cronitor
# cronitor.api_key = 'a67d302a577b4edaa089fae652f8469e'
from django.core.cache import cache


def can_delete():
    students = Student.objects.filter(can_delete=True)
    _students = [student for student in students if
                 date_time_diff(timezone.now(), student.date_joined, 'h') > 48]
    for student in _students:
        student.can_delete = False
        student.save()


# @cronitor.job('important-background-job')
def sub():
    schools = School.objects.filter(subscribed=True)
    for school in schools:
        if date_diff(school.expire_date(), timezone.localtime().now().date()) <= 0:
            school.subscribed = False
            school.save(update_fields=['subscribed'])
    # email_body = 'Hi Kells, this is just your daily cron-job check. Job for subscription ran successfully. \n'
    # data = {'email_body': email_body, 'to_email': "kelvinsajere@gmail.com",
    #         'email_subject': 'Cron Job Status'}
    # Util.send_email(data)


def set_current():
    current_term = CurrentTerm.objects.all()[0]
    year = str(timezone.now().date()).split('-')[0]
    students = Student.objects.all()
    date = f'{year}-01-01'

    if 1 < date_diff(timezone.localtime().now().date(), date, 'd') <= 104:
        if current_term.term != "2nd":

            for student in students:
                wallet = StudentWallet.objects.get(student=student)
                class_fee = ClassFees.objects.filter(school=student.school, _class=student.student_class)
                fees = Fees.objects.filter(student=student, school=student.school,
                                           academic_session=CurrentSession.objects.all()[0].session,
                                           _class=student.student_class,
                                           term=SchoolSettings.objects.get(school=student.school).current_term)
                if fees and class_fee[0].fee > 0:
                    fee = Fees.objects.filter(student=student, school=student.school,
                                              academic_session=CurrentSession.objects.all()[0].session,
                                              _class=student.student_class,
                                              term=SchoolSettings.objects.get(school=student.school).current_term)[
                        0]
                    if fee.remaining_fee() > 0 and wallet.amount > 0:
                        if wallet.amount - fee.remaining_fee() > 0:
                            amount = wallet.amount - fee.remaining_fee()
                            Fees.objects.create(student=student, school=student.school,
                                                academic_session=CurrentSession.objects.all()[0].session,
                                                fees_paid=fee.remaining_fee(),
                                                _class=student.student_class,
                                                payment_method="Wallet",
                                                term=SchoolSettings.objects.get(
                                                    school=student.school).current_term)

                            wallet.amount = amount
                            wallet.save(update_fields=['amount'])
                        elif wallet.amount - fee.remaining_fee() < 0:
                            amount = fee.remaining_fee() - wallet.amount
                            Fees.objects.create(student=student, school=student.school,
                                                academic_session=CurrentSession.objects.all()[0].session,
                                                fees_paid=wallet.amount,
                                                _class=student.student_class,
                                                payment_method="Wallet",
                                                term=SchoolSettings.objects.get(
                                                    school=student.school).current_term)

                            student.owes += amount
                            student.save(update_fields=['owes'])
                            wallet.amount = 0
                            wallet.save(update_fields=['amount'])
                    elif fee.remaining_fee() > 0 and wallet.amount <= 0:
                        student.owes += fee.remaining_fee()
                        student.save(update_fields=['owes'])

                else:
                    if class_fee and class_fee[0].fee > 0:
                        if wallet.amount <= 0:
                            student.owes += class_fee[0].fee
                            student.save(update_fields=['owes'])
                        else:
                            if wallet.amount > class_fee[0].fee:
                                newWallet = wallet.amount - class_fee[0].fee
                                Fees.objects.create(student=student, school=student.school,
                                                    academic_session=CurrentSession.objects.all()[0].session,
                                                    fees_paid=class_fee[0].fee,
                                                    _class=student.student_class,
                                                    payment_method="Wallet",
                                                    term=SchoolSettings.objects.get(
                                                        school=student.school).current_term)
                                wallet.amount = newWallet
                                wallet.save(update_fields=['amount'])
                            elif wallet.amount < class_fee[0].fee:
                                Fees.objects.create(student=student, school=student.school,
                                                    academic_session=CurrentSession.objects.all()[0].session,
                                                    fees_paid=wallet.amount,
                                                    _class=student.student_class,
                                                    payment_method="Wallet",
                                                    term=SchoolSettings.objects.get(
                                                        school=student.school).current_term)
                                student.owes += class_fee[0].fee - wallet.amount
                                student.save(update_fields=["owes"])
                                wallet.amount = 0
                                wallet.save(update_fields=['amount'])

                cached = cache.get(f"{student.slug}detail")
                if cached is not None:
                    cache.delete(f"{student.slug}detail")
            current_term.term = "2nd"
            current_term.save()

            for setting in SchoolSettings.objects.all():
                if setting.auto and setting.current_term != "2nd":
                    setting.current_term = "2nd"
                    setting.save()

    elif 110 < date_diff(timezone.localtime().now().date(), date, 'd') <= 243:
        if current_term.term != "3rd":

            for student in students:
                wallet = StudentWallet.objects.get(student=student)
                class_fee = ClassFees.objects.filter(school=student.school, _class=student.student_class)
                fees = Fees.objects.filter(student=student, school=student.school,
                                           academic_session=CurrentSession.objects.all()[0].session,
                                           _class=student.student_class,
                                           term=SchoolSettings.objects.get(school=student.school).current_term)
                if fees and class_fee[0].fee > 0:
                    fee = Fees.objects.filter(student=student, school=student.school,
                                              academic_session=CurrentSession.objects.all()[0].session,
                                              _class=student.student_class,
                                              term=SchoolSettings.objects.get(school=student.school).current_term)[
                        0]
                    if fee.remaining_fee() > 0 and wallet.amount > 0:
                        if wallet.amount - fee.remaining_fee() > 0:
                            amount = wallet.amount - fee.remaining_fee()
                            Fees.objects.create(student=student, school=student.school,
                                                academic_session=CurrentSession.objects.all()[0].session,
                                                fees_paid=fee.remaining_fee(),
                                                _class=student.student_class,
                                                payment_method="Wallet",
                                                term=SchoolSettings.objects.get(
                                                    school=student.school).current_term)

                            wallet.amount = amount
                            wallet.save(update_fields=['amount'])
                        elif wallet.amount - fee.remaining_fee() < 0:
                            amount = fee.remaining_fee() - wallet.amount
                            Fees.objects.create(student=student, school=student.school,
                                                academic_session=CurrentSession.objects.all()[0].session,
                                                fees_paid=wallet.amount,
                                                _class=student.student_class,
                                                payment_method="Wallet",
                                                term=SchoolSettings.objects.get(
                                                    school=student.school).current_term)

                            student.owes += amount
                            student.save(update_fields=['owes'])
                            wallet.amount = 0
                            wallet.save(update_fields=['amount'])
                    elif fee.remaining_fee() > 0 and wallet.amount <= 0:
                        student.owes += fee.remaining_fee()
                        student.save(update_fields=['owes'])
                else:
                    if class_fee and class_fee[0].fee > 0:
                        if wallet.amount <= 0:
                            student.owes += class_fee[0].fee
                            student.save(update_fields=['owes'])
                        else:
                            if wallet.amount > class_fee[0].fee:
                                newWallet = wallet.amount - class_fee[0].fee
                                Fees.objects.create(student=student, school=student.school,
                                                    academic_session=CurrentSession.objects.all()[0].session,
                                                    fees_paid=class_fee[0].fee,
                                                    _class=student.student_class,
                                                    payment_method="Wallet",
                                                    term=SchoolSettings.objects.get(
                                                        school=student.school).current_term)
                                wallet.amount = newWallet
                                wallet.save(update_fields=['amount'])
                            elif wallet.amount < class_fee[0].fee:
                                Fees.objects.create(student=student, school=student.school,
                                                    academic_session=CurrentSession.objects.all()[0].session,
                                                    fees_paid=wallet.amount,
                                                    _class=student.student_class,
                                                    payment_method="Wallet",
                                                    term=SchoolSettings.objects.get(
                                                        school=student.school).current_term)
                                student.owes += class_fee[0].fee - wallet.amount
                                student.save(update_fields=["owes"])
                                wallet.amount = 0
                                wallet.save(update_fields=['amount'])
                cached = cache.get(f"{student.slug}detail")
                if cached is not None:
                    cache.delete(f"{student.slug}detail")
            current_term.term = "3rd"
            current_term.save()
            for setting in SchoolSettings.objects.all():
                if setting.auto and setting.current_term != "3rd":
                    setting.current_term = "3rd"
                    setting.save()

    elif 244 < date_diff(timezone.localtime().now().date(), date, 'd') <= 365:
        current_session = CurrentSession.objects.all()[0]
        currentYear = int(datetime.datetime.now().date().year)
        nextYear = currentYear + 1
        session = AcademicSession.objects.filter(session=f"{currentYear}/{nextYear}")

        if current_term.term != "1st":

            for student in students:
                wallet = StudentWallet.objects.get(student=student)
                class_fee = ClassFees.objects.filter(school=student.school, _class=student.student_class)
                fees = Fees.objects.filter(student=student, school=student.school,
                                           academic_session=CurrentSession.objects.all()[0].session,
                                           _class=student.student_class,
                                           term=SchoolSettings.objects.get(school=student.school).current_term)
                if fees and class_fee[0].fee > 0:
                    fee = Fees.objects.filter(student=student, school=student.school,
                                              academic_session=CurrentSession.objects.all()[0].session,
                                              _class=student.student_class,
                                              term=SchoolSettings.objects.get(school=student.school).current_term)[0]
                    if fee.remaining_fee() > 0 and wallet.amount > 0:
                        if wallet.amount - fee.remaining_fee() > 0:
                            amount = wallet.amount - fee.remaining_fee()
                            Fees.objects.create(student=student, school=student.school,
                                                academic_session=CurrentSession.objects.all()[0].session,
                                                fees_paid=fee.remaining_fee(),
                                                _class=student.student_class,
                                                payment_method="Wallet",
                                                term=SchoolSettings.objects.get(
                                                    school=student.school).current_term)

                            wallet.amount = amount
                            wallet.save(update_fields=['amount'])
                        elif wallet.amount - fee.remaining_fee() < 0:
                            amount = fee.remaining_fee() - wallet.amount
                            Fees.objects.create(student=student, school=student.school,
                                                academic_session=CurrentSession.objects.all()[0].session,
                                                fees_paid=wallet.amount,
                                                _class=student.student_class,
                                                payment_method="Wallet",
                                                term=SchoolSettings.objects.get(
                                                    school=student.school).current_term)

                            student.owes += amount
                            student.save(update_fields=['owes'])
                            wallet.amount = 0
                            wallet.save(update_fields=['amount'])
                    elif fee.remaining_fee() > 0 and wallet.amount <= 0:
                        student.owes += fee.remaining_fee()
                        student.save(update_fields=['owes'])
                else:
                    if class_fee and class_fee[0].fee > 0:
                        if wallet.amount <= 0:
                            student.owes += class_fee[0].fee
                            student.save(update_fields=['owes'])
                        else:
                            if wallet.amount > class_fee[0].fee:
                                newWallet = wallet.amount - class_fee[0].fee
                                Fees.objects.create(student=student, school=student.school,
                                                    academic_session=CurrentSession.objects.all()[0].session,
                                                    fees_paid=class_fee[0].fee,
                                                    _class=student.student_class,
                                                    payment_method="Wallet",
                                                    term=SchoolSettings.objects.get(
                                                        school=student.school).current_term)
                                wallet.amount = newWallet
                                wallet.save(update_fields=['amount'])
                            elif wallet.amount < class_fee[0].fee:
                                Fees.objects.create(student=student, school=student.school,
                                                    academic_session=CurrentSession.objects.all()[0].session,
                                                    fees_paid=wallet.amount,
                                                    _class=student.student_class,
                                                    payment_method="Wallet",
                                                    term=SchoolSettings.objects.get(
                                                        school=student.school).current_term)
                                student.owes += class_fee[0].fee - wallet.amount
                                student.save(update_fields=["owes"])
                                wallet.amount = 0
                                wallet.save(update_fields=['amount'])
                cached = cache.get(f"{student.slug}detail")
                if cached is not None:
                    cache.delete(f"{student.slug}detail")
            if session:
                current_session.session = session[0]
                current_session.save()
            else:
                AcademicSession.objects.create(session=f"{currentYear}/{nextYear}")
                new_session = AcademicSession.objects.filter(session=f"{currentYear}/{nextYear}")
                current_session.session = new_session[0]
                current_session.save()

            current_term.term = "1st"
            current_term.save()

            for setting in SchoolSettings.objects.all():
                if setting.auto and setting.current_term != "1st":
                    setting.current_term = "1st"
                    setting.save()

    # email_body = 'Hi Kells, this is just your daily cron-job check. Job
    # for fees, term and session ran successfully. \n'
    # data = {'email_body': email_body, 'to_email': "kelvinsajere@gmail.com",
    #         'email_subject': 'Cron Job Status'}
    # Util.send_email(data)


def remove_old_events():
    event_list = Event.objects.all()
    for event in event_list:
        if event.from_date and event.to_date:
            if date_diff(event.from_date, timezone.localtime().now().date(), 'd') >= 0\
                    or date_diff(event.to_date, timezone.localtime().now().date(), 'd') >= 0:
                continue
            else:
                event.delete()
        elif event.from_date and not event.to_date:
            if date_diff(event.from_date, timezone.localtime().now().date(), 'd') >= 0:
                continue
            else:
                event.delete()
