from django.shortcuts import render,redirect
from django.db import connection
import re
from django.contrib.auth.models import User
from passlib.hash import pbkdf2_sha256



def is_valid(l):
    for i in l:
        if i == '':
            return False
    return True

def is_valid_email(e):
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'

    if re.search(regex,e):
        return True
    else:
        return False

def is_already_taken(e):
    cursor = connection.cursor()
    sql = "SELECT email FROM USERS"
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()

    for r in result:
        if e == r[0]:
            return True
    return False

def push_into_db(l):

    #generate user id
    cursor = connection.cursor()
    ID = cursor.callfunc('GIVEMAXUSERID', int)

    print("Calling Function")
    print(ID)
    cursor.close()


    #current date
    cursor = connection.cursor()
    curr_date_sql = "SELECT TO_CHAR(SYSDATE, 'YYYY-MM-DD') FROM dual"
    curr_date_list = cursor.execute(curr_date_sql)
    for i in curr_date_list:
        curr_date = str(i[0])
    print(curr_date)
    cursor.close()

    #encrypt password
    encrypted_password = pbkdf2_sha256.encrypt(l[6], rounds=12000, salt_size=32)

    #insert into database
    cursor = connection.cursor()
    sql = "INSERT INTO USERS(USER_ID,USER_FIRSTNAME, USER_LASTNAME, GENDER, DATE_OF_BIRTH, EMAIL, PHONE_NO, PASSWORD, JOIN_DATE) VALUES(%s, %s, %s, %s, TO_DATE(%s,'DD/MM/YYYY'), %s, %s, %s, %s)"
    cursor.execute(sql, [ID, l[0], l[1], l[2], l[3], l[4], l[5], encrypted_password, curr_date])
    connection.commit()
    cursor.close()
    #user = User.objects.create_user(str(ID),l[4],l[6])
    #user.save()


def register(response):
    error_msg = ""

    form_values = {'first_name': "",
                   'last_name': "",
                   'gender': "",
                   'bday': "",
                   'email': "",
                   'phone': "",
                   'password': "",
                   'conf_password': ""
                   }


    if response.method == "POST":
        print(response.POST)

        if response.POST.get("Register"):
            first_name = response.POST.get("first_name")
            last_name = response.POST.get("last_name")
            gender = ""
            if response.POST.get("gender"):
                gender = response.POST.get("gender")
            bday = response.POST.get("birthday")
            email = response.POST.get("email")
            phone = response.POST.get("phone")
            password = response.POST.get("password")
            conf_password = response.POST.get("confirm_password")

            l = []
            l.append(first_name)
            l.append(last_name)
            l.append(gender)
            l.append(bday)
            l.append(email)
            l.append(phone)
            l.append(password)
            l.append(conf_password)

            form_values = {'first_name' : first_name,
                           'last_name' : last_name,
                           'gender' : gender,
                           'bday' : bday,
                           'email' : email,
                           'phone' : phone,
                           'password' : password,
                           'conf_password':conf_password
                           }

            print(form_values['first_name'])
            print(l)


            if is_valid(l) == False:
                print("No Field can be left empty")
                error_msg = "No Field can be left empty"

            else:
                if is_valid_email(email) == False:
                    print("Not a valid e-mail")
                    error_msg = "Not a valid e-mail"
                elif is_already_taken(email) == True:
                    print("email already used with an account")
                    error_msg = "email already used with an account"
                elif len(password) < 8:
                    print("Password should be at least 8 characters")
                    error_msg = "Password should be at least 8 characters"

                elif password != conf_password:
                    print("Passwords do not match")
                    error_msg = "Passwords do not match"
                else:
                    push_into_db(l)
                    logged_in = True
                    print("Successfully registered")
                    #redirect to login page
                    return redirect("/user/login/")


    return render(response, 'accounts\RegisterForm.html',{"error_msg":error_msg , "form_values": form_values})




def login(request):

    cursor = connection.cursor()
    sql = "SELECT * FROM USERS"
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()

    error_msg = ""


    if request.session.get('is_logged_in', False) == True:
        return redirect("/home/")

    elif request.method == "POST":
        #print(request.POST)
        if request.POST.get("login"):
            email = request.POST.get("email")
            password = request.POST.get("password")


            ok = False
            user_ID = -1
            for r in result:
                email_db = r[10]
                password_db = r[4]
                if email_db == email and pbkdf2_sha256.verify(password,password_db):
                    user_ID = r[0]
                    ok = True
                    break

            if ok == False:
                print("Wrong Email or Password. Try Again!")
                error_msg = "Wrong Email or Password. Try Again!"
            else:
                print("successfully logged in")
                print(user_ID)

                request.session['is_logged_in'] = True
                request.session['user_ID'] = str(user_ID)
                #expires after 5 minutes of inactivity
                request.session.set_expiry(0)

                cursor = connection.cursor()
                cursor.callproc('UPDATE_SUBSCRIPTION', [user_ID])
                cursor.close()
                #redirect to home page
                #return redirect("http://127.0.0.1:8000/home/"+str(user_ID)+"/")
                return redirect("/home/")


    return render(request, 'accounts\loginForm.html',{"error_msg" : error_msg})


def resetpass(response):

    error_msg = ""
    print("here")
    if response.method == "POST":
        print(response.POST)
        if response.POST.get("login"):
            email = response.POST.get("email")
            newpassword = response.POST.get("new_password")
            confpassword = response.POST.get("conf_new_password")

            print(email)
            print(newpassword)
            print(confpassword)

            cursor = connection.cursor()
            sql = "SELECT * FROM USERS WHERE EMAIL = %s"
            cursor.execute(sql, [email])
            result = cursor.fetchall()
            cursor.close()

            ok = False
            count = 0
            for r in result:
                count = count + 1

            if count == 1:
                ok = True

            if ok == False:
                print("Wrong email")
                error_msg = "You don't have an account with this email"

            elif len(newpassword) < 8:
                print("Password should be at least 8 characters")
                error_msg = "Password should be at least 8 characters"

            elif newpassword != confpassword:
                error_msg = "Passwords don't match"
            else:
                cursor = connection.cursor()
                encrypted_password = pbkdf2_sha256.encrypt(newpassword, rounds=12000, salt_size=32)
                sql = "UPDATE USERS SET PASSWORD = %s WHERE EMAIL = %s"
                cursor.execute(sql, [encrypted_password, email])
                connection.commit()
                cursor.close()
                print("successfully changed your password")
                return redirect("/user/login/")

    return render(response, 'accounts\ResetPassword.html', {"error_msg": error_msg})



def contact(request):
    return render(request, 'accounts\contact.html')