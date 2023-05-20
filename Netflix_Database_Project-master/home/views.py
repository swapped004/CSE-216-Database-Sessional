from django.shortcuts import render,redirect
from django.db import connection

from django.core.files.storage import FileSystemStorage

from operator import itemgetter
import re
from django.http import HttpResponse
# Create your views here.

logged_in = False
ID = -1

def home_notLoggedIn(response):
    error_msg = ""
    no_of_results = ""
    if response.session.get('is_logged_in',False) == True:
        #return HttpResponse('This is User_ID' + request.session.get('user_ID',-1))
        id = response.session.get('user_ID', -1)
        show_list = []

        #search function
        if response.method == "POST":
            print("here")
            if response.POST.get("search_button") == "clicked":
                print(response.POST)
                search_item = response.POST.get('search_field')
                search_item = search_item.replace(" ","")
                search_pattern = "%" + search_item.lower() + "%"

                print(search_pattern)


                #search_type = response.POST.get('type')
                search_genre = response.POST.get('genre')
                search_lang = response.POST.get('language')
                search_from = response.POST.get('from_year')
                search_to = response.POST.get('to_year')
                sort_by = response.POST.get('sort_by')



                #print(search_type)
                print(search_genre)
                print(search_lang)
                print(search_from)
                print(search_to)
                print(sort_by)



                cursor = connection.cursor()


                sql = " SELECT DISTINCT(s.SHOW_ID) FROM SHOW s,ACTOR a,ACT ac" \
                      " WHERE s.SHOW_ID = ac.SHOW_IDACT AND ac.ACTOR_IDACT = a.PERSON_ID AND" \
                      " regexp_replace(LOWER(a.ACTOR_FIRST_NAME || ' ' || a.ACTOR_LAST_NAME), ' ','') like (%s)" \
                      " UNION" \
                      " (SELECT DISTINCT(s.SHOW_ID) FROM SHOW s, SERIES se"\
                      " WHERE s.SERIES_ID = se.SERIES_ID" \
                      " AND s.SEASON_NO = se.SEASON_NO" \
                      " AND regexp_replace(LOWER(se.TITLE), ' ','') like (%s)" \
                      " )" \
                      " UNION" \
                      " (" \
                      " SELECT DISTINCT(s.SHOW_ID)" \
                      " FROM SHOW s, DIRECTOR d" \
                      " WHERE s.DIRECTOR_ID = d.PERSON_ID" \
                      " AND regexp_replace(LOWER (d.DIRECTOR_FIRST_NAME || ' ' || d.DIRECTOR_LAST_NAME), ' ','') like (%s)" \
                      " )" \
                      " UNION" \
                      " (" \
                      " SELECT DISTINCT(s.SHOW_ID) FROM SHOW s" \
                      " WHERE regexp_replace(LOWER(s.TITLE), ' ','') like (%s)" \
                      " OR regexp_replace(LOWER(s.GENRE), ' ','') like (%s)" \
                      " )"

                print(sql)
                cursor.execute(sql, [search_pattern,search_pattern,search_pattern,search_pattern,search_pattern])

                result = cursor.fetchall();
                cursor.close()

                print(type(result))


                search_genre = response.POST.get('genre')
                search_genre = search_genre.replace(" ", "")
                search_genre = "%" + search_genre.lower() + "%"
                print(search_genre)

                search_lang = response.POST.get('language')
                search_lang = search_lang.replace(" ", "")
                search_lang = "%" + search_lang.lower() + "%"

                print(search_lang)

                search_from = response.POST.get('from_year')

                print(search_from)

                search_to = response.POST.get('to_year')

                print(search_to)


                result_genre = []
                if search_genre != "":
                    cursor = connection.cursor()
                    sql_genre = "SELECT DISTINCT(s.SHOW_ID) FROM SHOW s" \
                                " WHERE regexp_replace(LOWER(s.GENRE), ' ','') Like (%s)"
                    cursor.execute(sql_genre, [search_genre])
                    result_genre = cursor.fetchall()
                    cursor.close()
                else:
                    result_genre = result

                result_lang = []
                if search_lang != "":
                    cursor = connection.cursor()
                    sql_lang = "SELECT DISTINCT(s.SHOW_ID) FROM SHOW s" \
                                " WHERE regexp_replace(LOWER(s.LANGUAGE), ' ','') Like (%s)"
                    cursor.execute(sql_lang, [search_lang])
                    result_lang = cursor.fetchall()
                    cursor.close()
                else:
                    result_lang = result

                result_from = []
                if search_from != "":
                    cursor = connection.cursor()
                    sql_from = "SELECT DISTINCT(s.SHOW_ID) FROM SHOW s where s.YEAR >= %s"
                    cursor.execute(sql_from, [search_from])
                    result_from = cursor.fetchall()
                    cursor.close()
                else:
                    result_from = result

                result_to = []
                if search_to != "":
                    cursor = connection.cursor()
                    sql_to = "SELECT DISTINCT(s.SHOW_ID) FROM SHOW s where s.YEAR <= %s"
                    cursor.execute(sql_to, [search_to])
                    result_to = cursor.fetchall()
                    cursor.close()
                else:
                    result_to = result

                result_temp = set(result_genre).intersection(set(result_from).intersection(result_to))
                result_temp_new = set(result_temp).intersection(set(result_lang))
                result_final = set(result).intersection(result_temp_new)


                error_msg = "No Result Found!"
                show_list=[]


                cnt = 0
                for r in result_final:
                    cnt = cnt+1
                    print(type(r))
                    show_id = r[0]
                    print(show_id)
                    cursor = connection.cursor()
                    sql = "SELECT * FROM SHOW WHERE SHOW_ID = %s"
                    cursor.execute(sql, [show_id])
                    show_res = cursor.fetchall()
                    cursor.close()
                    print("here")

                    for r_temp in show_res:
                        #show_id = r_temp[0]
                        show_title = r_temp[2]
                        show_genre = r_temp[1]
                        show_des = r_temp[3]
                        show_age = r_temp[4]
                        show_lang = r_temp[8]
                        show_image = r_temp[13]
                        show_imdb = r_temp[5]
                        show_urating = r_temp[6]
                        single_row = {
                                      "show_id": show_id,
                                      "show_imdb": show_imdb,
                                      "show_title": show_title,
                                      "show_genre": show_genre,
                                      "show_des": show_des,
                                      "show_age": show_age,
                                      "show_lang": show_lang,
                                      "show_image": show_image,
                                      "show_user_rating": show_urating}
                        show_list.append(single_row)
                        error_msg = ""

                    #sort
                    if sort_by == "USER RATING(D)":
                        show_list = sorted(show_list, key=itemgetter('show_user_rating'), reverse=True)
                    if sort_by == "USER RATING(A)":
                        show_list = sorted(show_list, key=itemgetter('show_user_rating'), reverse=False)
                    if sort_by == "IMDB RATING(D)":
                        show_list = sorted(show_list, key=itemgetter('show_imdb'), reverse=True)
                    if sort_by == "IMDB RATING(A)":
                        show_list = sorted(show_list, key=itemgetter('show_imdb'), reverse=False)

                no_of_results = str(cnt)

        else:
            cursor = connection.cursor()
            sql = "SELECT * FROM SHOW"
            cursor.execute(sql)
            result_show = cursor.fetchall()
            cursor.close()
            show_list = []
            cnt = 0
            for r in result_show:
                cnt = cnt+1
                show_id = r[0]
                show_title = r[2]
                show_genre = r[1]
                show_imdb = r[5]
                show_image = r[13]
                single_row = {"show_id": show_id, "show_title": show_title, "show_genre": show_genre, "show_imdb": show_imdb,
                              "show_image": show_image}
                show_list.append(single_row)
            no_of_results = str(cnt)

        return render(response, "home/homepage.html", {'no_of_results': no_of_results, 'shows': show_list, 'error_msg': error_msg})

    else:
        return redirect("/user/login")


def log_out(request):
    if request.session.get('is_logged_in',False) == True:
        try:
            del request.session['user_ID']
            del request.session['is_logged_in']
        except KeyError:
            pass
        print("logged out successfully")

    return redirect("/user/login")


def genre(response, genre_name):
    if response.session.get('is_logged_in', False) == True:
        cursor = connection.cursor()
        genre_name = genre_name.lower()
        genre_pattern = "%"+genre_name+"%"
        print(genre_pattern)

        if genre_name != "miscellaneous":
            sql = "SELECT * FROM SHOW s WHERE lower(s.GENRE) LIKE %s"
            cursor.execute(sql, [genre_pattern])
        else:
            sql = "SELECT * FROM SHOW s"
            cursor.execute(sql)

        result = cursor.fetchall()
        cursor.close()

        show_list = []

        error_msg = "NO RESULT FOUND"
        cnt = 0
        for r_temp in result:
            cnt = cnt+1
            show_id = r_temp[0]
            show_title = r_temp[2]
            show_genre = r_temp[1]
            show_des = r_temp[3]
            show_age = r_temp[4]
            show_lang = r_temp[8]
            show_image = r_temp[13]
            show_imdb = r_temp[5]
            single_row = {"show_id": show_id,
                        "show_imdb": show_imdb,
                        "show_title": show_title,
                        "show_genre": show_genre,
                        "show_des": show_des,
                        "show_age": show_age,
                        "show_lang": show_lang,
                        "show_image": show_image}
            show_list.append(single_row)
            error_msg = ""

        no_of_results = str(cnt)

        return render(response, "home/homepage.html",
                      {'no_of_results': no_of_results, 'shows': show_list, 'error_msg': error_msg})
    else:
        print("not logged in")
        return redirect("/user/login/")


def shows(response, show_type):
    if response.session.get('is_logged_in', False) == True:

        show_list = []
        error_msg = ""
        no_of_results = ""

        if response.method == "POST":

            if response.POST.get("search_button") == 'clicked':
                print(response.POST)
                search_item = response.POST.get('search_field')
                search_item = search_item.replace(" ", "")
                search_pattern = "%" + search_item.lower() + "%"
                show_type_pattern = "%"+show_type.lower()+"%"

                print(search_pattern)
                print(show_type_pattern)

                # search_type = response.POST.get('type')
                search_genre = response.POST.get('genre')
                search_comp = response.POST.get('production')
                search_status = response.POST.get('status')
                search_lang = response.POST.get('language')
                sort_by = response.POST.get('sort_by')

                # print(search_type)
                print(search_genre)
                print(search_comp)
                print(search_status)
                print(search_lang)


                cursor = connection.cursor()
                sql = " SELECT DISTINCT se.SERIES_ID,se.SEASON_NO FROM Series se,SHOW s,ACTOR a,ACT ac" \
                      " WHERE se.SERIES_ID = s.SERIES_ID AND se.SEASON_NO = s.SEASON_NO AND" \
                      " s.SHOW_ID = ac.SHOW_IDACT AND ac.ACTOR_IDACT = a.PERSON_ID AND" \
                      " LOWER(se.CATEGORY) like (%s) AND" \
                      " regexp_replace(LOWER(a.ACTOR_FIRST_NAME || ' ' || a.ACTOR_LAST_NAME), ' ','') like (%s)" \
                      " UNION" \
                      " (" \
                      " SELECT DISTINCT se.SERIES_ID,se.SEASON_NO FROM SERIES se,SHOW s" \
                      " WHERE s.SERIES_ID = se.SERIES_ID AND s.SEASON_NO = se.SEASON_NO AND" \
                      " LOWER(se.CATEGORY) like (%s) AND" \
                      " (regexp_replace(LOWER(s.TITLE), ' ','') like (%s)" \
                      " OR regexp_replace(LOWER(s.GENRE), ' ','') like (%s))" \
                      " )" \
                      " UNION" \
                      " (" \
                      " SELECT DISTINCT se.SERIES_ID,se.SEASON_NO FROM Series se,SHOW s,DIRECTOR d" \
                      " WHERE se.SERIES_ID = s.SERIES_ID AND se.SEASON_NO = s.SEASON_NO AND" \
                      " LOWER(se.CATEGORY) like (%s) AND" \
                      " s.DIRECTOR_ID = d.PERSON_ID" \
                      " AND regexp_replace(LOWER (d.DIRECTOR_FIRST_NAME || ' ' || d.DIRECTOR_LAST_NAME), ' ','') like (%s)" \
                      " )" \
                      " UNION" \
                      " (" \
                      " SELECT DISTINCT se.SERIES_ID,se.SEASON_NO FROM SERIES se" \
                      " WHERE LOWER(se.CATEGORY) like (%s) AND" \
                      " regexp_replace(LOWER(se.TITLE), ' ','') like (%s)" \
                      " )"

                cursor.execute(sql, [show_type_pattern,search_pattern, show_type_pattern
                    ,search_pattern, search_pattern, show_type_pattern, search_pattern, show_type_pattern,
                                     search_pattern])
                result = cursor.fetchall();
                cursor.close()

                print(type(result))

                search_genre = response.POST.get('genre')
                search_genre = search_genre.replace(" ", "")
                search_genre = "%" + search_genre.lower() + "%"
                print(search_genre)

                search_comp = response.POST.get('production')
                search_comp = search_comp.replace(" ", "")
                search_comp = "%" + search_comp.lower() + "%"

                print(search_comp)

                search_status = response.POST.get('status')

                print(search_status)

                search_lang = response.POST.get('language')

                print(search_lang)

                result_final = []

                result_genre = []
                if search_genre != "":
                    cursor = connection.cursor()
                    sql_genre = "SELECT DISTINCT se.SERIES_ID,se.SEASON_NO FROM SERIES se,SHOW s" \
                                " where se.SERIES_ID = s.SERIES_ID AND se.SEASON_NO = s.SEASON_NO AND" \
                                " LOWER(se.CATEGORY) like (%s) AND" \
                                " regexp_replace(LOWER(s.GENRE), ' ','') Like (%s)"
                    cursor.execute(sql_genre, [show_type_pattern, search_genre])
                    result_genre = cursor.fetchall()
                    cursor.close()
                else:
                    result_genre = result

                result_comp = []
                if search_comp != "":
                    cursor = connection.cursor()
                    sql_comp = "SELECT DISTINCT se.SERIES_ID,se.SEASON_NO FROM SERIES se,SHOW s,PRODUCTION_COMPANY p" \
                                " where se.SERIES_ID = s.SERIES_ID AND se.SEASON_NO = s.SEASON_NO AND" \
                                " LOWER(se.CATEGORY) like (%s) AND" \
                                " s.COMPANY_ID = p.COMPANY_ID" \
                                " AND regexp_replace(LOWER(p.COMPANY_NAME), ' ','') Like (%s)"
                    cursor.execute(sql_comp, [show_type_pattern, search_comp])
                    result_comp = cursor.fetchall()
                    cursor.close()
                else:
                    result_comp = result

                result_status = []
                if search_status != "":
                    cursor = connection.cursor()
                    sql_status = "SELECT DISTINCT se.SERIES_ID,se.SEASON_NO FROM SERIES se where" \
                                 " LOWER(se.CATEGORY) like (%s) AND" \
                                 " LOWER(se.STATUS) = %s"
                    cursor.execute(sql_status, [show_type_pattern, search_status.lower()])
                    result_status = cursor.fetchall()
                    cursor.close()
                else:
                    result_status = result

                result_lang = []
                if search_lang != "":
                    cursor = connection.cursor()
                    sql_lang = "SELECT DISTINCT se.SERIES_ID,se.SEASON_NO FROM SERIES se,SHOW s" \
                               " where se.SERIES_ID = s.SERIES_ID AND se.SEASON_NO = s.SEASON_NO AND" \
                               " LOWER(se.CATEGORY) like (%s) AND " \
                               " LOWER(s.LANGUAGE) = %s"
                    cursor.execute(sql_lang, [show_type_pattern, search_lang.lower()])
                    result_lang = cursor.fetchall()
                    cursor.close()
                else:
                    result_lang = result

                result_temp = set(result_genre).intersection(set(result_status).intersection(result_lang))
                result_temp_new = set(result_temp).intersection(set(result_comp))
                result_final = set(result).intersection(result_temp_new)

                error_msg = "No Result Found!"
                show_list = []

                cnt = 0
                for r in result_final:
                    cnt = cnt + 1
                    print(type(r))
                    series_id = r[0]
                    season_no = r[1]
                    cursor = connection.cursor()
                    sql = "SELECT se.SERIES_ID,se.SEASON_NO,se.TITLE,se.COVER FROM SERIES se " \
                          "WHERE se.SERIES_ID = %s and se.SEASON_NO = %s"
                    cursor.execute(sql, [series_id,season_no])
                    show_res = cursor.fetchall()
                    cursor.close()
                    print("here")

                    for r_temp in show_res:
                        show_title = r_temp[2]
                        season_no = r_temp[1]
                        show_image = r_temp[3]
                        series_id = r_temp[0]

                        series_identifier = str(series_id) + "_" + str(season_no)

                        cursor = connection.cursor()
                        sql = "SELECT AVG(s.IMDB_RATING),AVG(s.USER_RATING) FROM SHOW s,Series se" \
                              " Where s.SERIES_ID = %s and s.SEASON_NO = %s "
                        cursor.execute(sql, [series_id, season_no])
                        res = cursor.fetchall()
                        cursor.close()

                        imdb_rating = 0
                        user_rating = 0
                        for r in res:
                            imdb_rating = round(r[0], 2)
                            user_rating = round(r[1], 2)

                        single_row = {"show_id": series_id, "show_title": show_title, "show_genre": season_no, "show_imdb": imdb_rating,
                                      "show_image": show_image, "series_identifier": series_identifier, "user_rating": user_rating}
                        show_list.append(single_row)
                        error_msg = ""
                # sort
                if sort_by == "USER RATING(D)":
                    show_list = sorted(show_list, key=itemgetter('user_rating'), reverse=True)
                if sort_by == "USER RATING(A)":
                    show_list = sorted(show_list, key=itemgetter('user_rating'), reverse=False)
                if sort_by == "IMDB RATING(D)":
                    show_list = sorted(show_list, key=itemgetter('show_imdb'), reverse=True)
                if sort_by == "IMDB RATING(A)":
                    show_list = sorted(show_list, key=itemgetter('show_imdb'), reverse=False)
                no_of_results = str(cnt)

        else:
            cursor = connection.cursor()
            sql=""
            if show_type == "series":
                sql = "SELECT se.SERIES_ID,se.SEASON_NO,se.TITLE,se.COVER  FROM SERIES se" \
                      " where se.CATEGORY = 'TV_Series' OR se.CATEGORY = 'Mini_TV_Series'"
            if show_type == "anime":
                sql = "SELECT se.SERIES_ID,se.SEASON_NO,se.TITLE,se.COVER FROM SERIES se where se.CATEGORY = 'Anime'"

            if show_type == "documentary":
                sql = "SELECT se.SERIES_ID,se.SEASON_NO,se.TITLE,se.COVER FROM SERIES se where se.CATEGORY = 'Documentary'"

            cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()


            show_list=[]
            error_msg = "No Result Found!"
            cnt = 0
            for r in result:
                cnt = cnt+1
                show_title = r[2]
                season_no = r[1]
                show_image = r[3]

                print(show_title)
                print(season_no)


                series_id = r[0]

                series_identifier = str(series_id)+"_"+str(season_no)
                cursor = connection.cursor()
                sql = "SELECT AVG(s.IMDB_RATING) FROM SHOW s,Series se" \
                      " Where s.SERIES_ID = %s and s.SEASON_NO = %s "
                cursor.execute(sql, [series_id,season_no])
                res = cursor.fetchall()
                cursor.close()

                imdb_rating = 0
                for r in res:
                    imdb_rating = round(r[0], 2)

                single_row = {"series_id": series_id, "show_title": show_title, "season_no": season_no, "show_imdb": imdb_rating,
                              "show_image": show_image, "series_identifier": series_identifier}
                show_list.append(single_row)
                error_msg = ""

            no_of_results = str(cnt)

        return render(response, "home/shows.html",
                  {'no_of_results': no_of_results, 'shows': show_list, 'error_msg': error_msg})



    else:
        print("not logged in")
        return redirect("/user/login/")






def movies(response):
    error_msg = ""
    no_of_results = ""
    if response.session.get('is_logged_in', False) == True:
        # return HttpResponse('This is User_ID' + request.session.get('user_ID',-1))
        id = response.session.get('user_ID', -1)
        show_list = []

        # search function
        if response.method == "POST":
            print("here")
            if response.POST.get("search_button") == "clicked":
                print(response.POST)
                search_item = response.POST.get('search_field')
                search_item = search_item.replace(" ", "")
                search_pattern = "%" + search_item.lower() + "%"

                print(search_pattern)

                # search_type = response.POST.get('type')
                search_genre = response.POST.get('genre')
                search_lang = response.POST.get('language')
                search_from = response.POST.get('from_year')
                search_to = response.POST.get('to_year')
                sort_by = response.POST.get('sort_by')

                # print(search_type)
                print(search_genre)
                print(search_lang)
                print(search_from)
                print(search_to)

                cursor = connection.cursor()
                sql = "SELECT DISTINCT(s.SHOW_ID) FROM SHOW s,ACTOR a,ACT ac" \
                      " WHERE s.SHOW_ID = ac.SHOW_IDACT AND ac.ACTOR_IDACT = a.PERSON_ID AND" \
                      " s.SERIES_ID IS NULL AND" \
                      " regexp_replace(LOWER(a.ACTOR_FIRST_NAME || ' ' || a.ACTOR_LAST_NAME), ' ','') like (%s)" \
                      " UNION" \
                      " (" \
                      " SELECT DISTINCT(s.SHOW_ID)" \
                      " FROM SHOW s, DIRECTOR d" \
                      " WHERE s.DIRECTOR_ID = d.PERSON_ID AND" \
                      " s.SERIES_ID IS NULL AND" \
                      " regexp_replace(LOWER (d.DIRECTOR_FIRST_NAME || ' ' || d.DIRECTOR_LAST_NAME), ' ','') like (%s)" \
                      " )" \
                      " UNION" \
                      " (" \
                      " SELECT DISTINCT(s.SHOW_ID) FROM SHOW s" \
                      " WHERE s.SERIES_ID IS NULL AND" \
                      " (regexp_replace(LOWER(s.TITLE), ' ','') like (%s)" \
                      " OR regexp_replace(LOWER(s.GENRE), ' ','') like (%s))" \
                      " )"

                cursor.execute(sql, [search_pattern, search_pattern, search_pattern, search_pattern])
                result = cursor.fetchall();
                cursor.close()

                print(type(result))

                search_genre = response.POST.get('genre')
                search_genre = search_genre.replace(" ", "")
                search_genre = "%" + search_genre.lower() + "%"
                print(search_genre)

                search_lang = response.POST.get('language')
                search_lang = search_lang.replace(" ", "")
                search_lang = "%" + search_lang.lower() + "%"

                print(search_lang)

                search_from = response.POST.get('from_year')

                print(search_from)

                search_to = response.POST.get('to_year')

                print(search_to)

                result_final = []

                result_genre = []
                if search_genre != "":
                    cursor = connection.cursor()
                    sql_genre = "SELECT DISTINCT(s.SHOW_ID) FROM SHOW s" \
                                " where regexp_replace(LOWER(s.GENRE), ' ','') Like (%s) AND" \
                                " s.SERIES_ID IS NULL"
                    cursor.execute(sql_genre, [search_genre])
                    result_genre = cursor.fetchall()
                    cursor.close()
                else:
                    result_genre = result

                result_lang = []
                if search_lang != "":
                    cursor = connection.cursor()
                    sql_lang = "SELECT DISTINCT(s.SHOW_ID) FROM SHOW s" \
                               " WHERE regexp_replace(LOWER(s.LANGUAGE), ' ','') Like (%s) AND" \
                               " s.SERIES_ID IS NULL"
                    cursor.execute(sql_lang, [search_lang])
                    result_lang = cursor.fetchall()
                    cursor.close()
                else:
                    result_lang = result

                result_from = []
                if search_from != "":
                    cursor = connection.cursor()
                    sql_from = "SELECT DISTINCT(s.SHOW_ID) FROM SHOW s where s.YEAR >= %s AND " \
                               " s.SERIES_ID IS NULL"
                    cursor.execute(sql_from, [search_from])
                    result_from = cursor.fetchall()
                    cursor.close()
                else:
                    result_from = result

                result_to = []
                if search_to != "":
                    cursor = connection.cursor()
                    sql_to = "SELECT DISTINCT(s.SHOW_ID) FROM SHOW s where s.YEAR <= %s AND" \
                             " s.SERIES_ID IS NULL"
                    cursor.execute(sql_to, [search_to])
                    result_to = cursor.fetchall()
                    cursor.close()
                else:
                    result_to = result

                result_temp = set(result_genre).intersection(set(result_from).intersection(result_to))
                result_temp_new = set(result_temp).intersection(set(result_lang))
                result_final = set(result).intersection(result_temp_new)

                error_msg = "No Result Found!"
                show_list = []

                cnt = 0
                for r in result_final:
                    cnt = cnt + 1
                    print(type(r))
                    show_id = r[0]
                    print(show_id)
                    cursor = connection.cursor()
                    sql = "SELECT * FROM SHOW WHERE SHOW_ID = %s"
                    cursor.execute(sql, [show_id])
                    show_res = cursor.fetchall()
                    cursor.close()
                    print("here")

                    for r_temp in show_res:
                        show_title = r_temp[2]
                        show_genre = r_temp[1]
                        show_des = r_temp[3]
                        show_age = r_temp[4]
                        show_lang = r_temp[8]
                        show_image = r_temp[13]
                        show_imdb = r_temp[5]
                        show_urating = r_temp[6]
                        single_row = {
                                      "show_id": show_id,
                                      "show_imdb": show_imdb,
                                      "show_title": show_title,
                                      "show_genre": show_genre,
                                      "show_des": show_des,
                                      "show_age": show_age,
                                      "show_lang": show_lang,
                                      "show_image": show_image,
                                      "show_user_rating": show_urating}
                        show_list.append(single_row)
                        error_msg = ""
                    # sort
                    if sort_by == "USER RATING(D)":
                        show_list = sorted(show_list, key=itemgetter('show_user_rating'), reverse=True)
                    if sort_by == "USER RATING(A)":
                        show_list = sorted(show_list, key=itemgetter('show_user_rating'), reverse=False)
                    if sort_by == "IMDB RATING(D)":
                        show_list = sorted(show_list, key=itemgetter('show_imdb'), reverse=True)
                    if sort_by == "IMDB RATING(A)":
                        show_list = sorted(show_list, key=itemgetter('show_imdb'), reverse=False)
                no_of_results = str(cnt)

        else:
            cursor = connection.cursor()
            sql = "SELECT * FROM SHOW WHERE SERIES_ID IS NULL"
            cursor.execute(sql)
            result_show = cursor.fetchall()
            cursor.close()
            show_list = []
            cnt = 0
            for r in result_show:
                cnt = cnt + 1
                show_id = r[0]
                show_title = r[2]
                show_genre = r[1]
                show_imdb = r[5]
                show_image = r[13]
                single_row = {"show_id": show_id, "show_title": show_title, "show_genre": show_genre, "show_imdb": show_imdb,
                              "show_image": show_image}
                show_list.append(single_row)
            no_of_results = str(cnt)
            print(no_of_results)

        return render(response, "home/movies.html",
                      {'no_of_results': no_of_results, 'shows': show_list, 'error_msg': error_msg})

    else:
        return redirect("/user/login")




def single_show(response,show_id):
    print("in the single show")
    if response.session.get('is_logged_in', False) == True:
        ok = False
        rate = 0
        if response.method == "POST":
            print("here")
            print(response.POST)


            if response.POST.get("review_btn"):
                print("success")
                review = response.POST.get("review")
                connection.autocommit = True

                user_id = response.session.get('user_ID')
                print(user_id)
                cursor = connection.cursor()
                sql = "UPDATE RATED SET FEEDBACK = %s WHERE SHOW_IDRATE = %s AND USER_IDRATE = %s"
                cursor.execute(sql, [review, show_id, user_id])
                cursor.close()



            if response.POST.get("rating"):
                if response.POST.get("rating") == "1":
                    ok = True
                    rate = 1
                elif response.POST.get("rating") == "2":
                    ok = True
                    rate = 2
                elif response.POST.get("rating") == "3":
                    ok = True
                    rate = 3
                elif response.POST.get("rating") == "4":
                    ok = True
                    rate = 4
                elif response.POST.get("rating") == "5":
                    ok = True
                    rate = 5


                if ok:
                    connection.autocommit = True
                    print("rating" + str(rate))
                    feedback = "Nothing"

                    user_id = response.session.get('user_ID')
                    print(user_id)
                    cursor = connection.cursor()
                    sql = "SELECT * FROM RATED WHERE USER_IDRATE = %s AND SHOW_IDRATE = %s"
                    cursor.execute(sql, [user_id, show_id])
                    result = cursor.fetchall()
                    cursor.close()

                    cnt = 0
                    prev_rate = 0
                    for r in result:
                        prev_rate = r[3]
                        cnt += 1
                    print(prev_rate)

                    if cnt == 0:
                        cursor = connection.cursor()
                        sql = "INSERT INTO RATED VALUES(%s,%s,%s,%s,SYSDATE)"
                        cursor.execute(sql, [user_id, show_id, feedback, rate])
                        cursor.close()
                    else:
                        cursor = connection.cursor()
                        sql = "UPDATE RATED SET RATING_OUT_OF_FIVE = %s, RATE_TIME = SYSDATE" \
                              " WHERE USER_IDRATE = %s AND SHOW_IDRATE = %s"
                        cursor.execute(sql, [rate, user_id, show_id])
                        cursor.close()

                        cursor = connection.cursor()
                        sql = "SELECT COUNT(*) FROM RATED where SHOW_IDRATE = %s"
                        cursor.execute(sql, [show_id])
                        result_row_cnt = cursor.fetchall()
                        tot_cnt = 0
                        for r in result_row_cnt:
                            tot_cnt = r[0]

                        print(tot_cnt)
                        cursor.close()


                        cursor = connection.cursor()
                        sql = "UPDATE SHOW SET USER_RATING = least(((USER_RATING*%s - %s + %s)/%s),5)" \
                              " WHERE SHOW_ID = %s"
                        cursor.execute(sql, [tot_cnt, prev_rate, rate, tot_cnt, show_id])
                        cursor.close()



        cursor = connection.cursor()
        sql = "SELECT * FROM SHOW WHERE SHOW_ID = %s"
        cursor.execute(sql, [show_id])
        result = cursor.fetchall()
        cursor.close()

        show_list = []
        for r_temp in result:
            show_title = r_temp[2]
            show_genre = r_temp[1]
            show_des = r_temp[3]
            show_age = r_temp[4]
            show_lang = r_temp[8]
            show_image = r_temp[13]
            show_imdb = r_temp[5]
            show_year = r_temp[14]
            show_user_rating = r_temp[6]
            director_id = r_temp[10]
            show_age_limit = r_temp[4]
            company_id = r_temp[9]
            file_name = r_temp[7]

            # director information
            cursor = connection.cursor()
            sql = "SELECT * FROM DIRECTOR d WHERE d.PERSON_ID = %s"
            cursor.execute(sql, [director_id])
            result_dir = cursor.fetchall()
            cursor.close()


            dir_first_name = ""
            dir_last_name = ""
            dir_wiki_link = ""
            for r_dir in result_dir:
                dir_first_name = r_dir[1]
                dir_last_name = r_dir[2]
                dir_wiki_link = r_dir[4]

            dir_name = dir_first_name + " " + dir_last_name



            #actor_information
            cursor = connection.cursor()
            sql = "SELECT a.ACTOR_FIRST_NAME,a.ACTOR_LAST_NAME,a.WIKI_LINK,a.PHOTO FROM ACTOR a,ACT ac,SHOW s" \
                  " WHERE a.PERSON_ID = ac.ACTOR_IDACT AND" \
                  " ac.SHOW_IDACT = s.SHOW_ID AND" \
                  " s.SHOW_ID = %s"
            cursor.execute(sql, [show_id])
            result_act = cursor.fetchall()
            cursor.close()

            actor_list = []
            for r_act in result_act:
                actor_name = r_act[0]+" "+r_act[1]
                single_act_row = {"actor_name": actor_name, "actor_link": r_act[2], "actor_photo": r_act[3]}
                actor_list.append(single_act_row)


            #production_company

            cursor = connection.cursor()
            sql = "SELECT p.COMPANY_NAME,p.LOGO FROM PRODUCTION_COMPANY p WHERE p.COMPANY_ID = %s"
            cursor.execute(sql, [company_id])
            result_comp = cursor.fetchall()
            cursor.close()

            for r_comp in result_comp:
                company_name = r_comp[0]
                company_logo = r_comp[1]


            #reviews

            cursor = connection.cursor()
            sql = "SELECT r.RATING_OUT_OF_FIVE, r.FEEDBACK, u.USER_FIRSTNAME, u.USER_LASTNAME, TO_CHAR( r.RATE_TIME,'DD Mon YYYY' ), u.USER_ID" \
                  " FROM RATED r, USERS u" \
                  " WHERE r.USER_IDRATE = u.USER_ID" \
                  " AND r.SHOW_IDRATE = %s" \
                  " ORDER BY r.RATE_TIME DESC"
            cursor.execute(sql, [show_id])
            result_review = cursor.fetchall()
            cursor.close()

            review_list = []
            review_count = 0
            for r in result_review:
                name = r[2]+" "+r[3]
                reviewer_id = r[5]
                row = {"rating_out_of_five": r[0],
                       "feedback": r[1],
                       "review_poster": name,
                       "review_time": r[4],
                       "reviewer_id": reviewer_id}
                review_list.append(row)
                review_count += 1

            #is subscribed?


            user_id = response.session.get('user_ID')
            cursor = connection.cursor()
            sql = "SELECT * from SUBSCRIPTION sub WHERE sub.USER_IDSUB = %s AND sub.SHOW_IDSUB = %s" \
                  " AND sub.SUBSCRIPTION_STATUS = 'ACTIVE'"
            cursor.execute(sql, [user_id, show_id])
            result_sub = cursor.fetchall()
            cursor.close()

            cnt = 0
            for r_sub in result_sub:
                cnt += 1

            is_sub = 0
            if cnt > 0:
                is_sub = 1

            cursor = connection.cursor()
            sql = "SELECT NVL(s.SERIES_ID, -1),NVL(s.SEASON_NO,-1) from SHOW s WHERE s.SHOW_ID = %s"
            cursor.execute(sql, [show_id])
            result_is_series = cursor.fetchall()
            cursor.close()

            is_series = 0
            series_id = -1
            season_no = -1
            for r_is_series in result_is_series:
                if r_is_series[0] == -1:
                    is_series = 0
                else:
                    series_id = r_is_series[0]
                    season_no = r_is_series[1]
                    is_series = 1


            single_row = {"show_id": show_id,
                          "show_imdb": show_imdb,
                          "show_title": show_title,
                          "show_genre": show_genre,
                          "show_des": show_des,
                          "show_age": show_age,
                          "show_lang": show_lang,
                          "show_image": show_image,
                          "show_year": show_year,
                          "show_age_limit": show_age_limit,
                          "show_user_rating": show_user_rating,
                          "file_name": file_name,
                          "director_name": dir_name,
                          "director_link": dir_wiki_link,
                          "actor_list": actor_list,
                          "company_name": company_name,
                          "company_logo": company_logo,
                          "is_sub": is_sub,
                          "is_series": is_series,
                          "series_id": series_id,
                          "season_no": season_no}

            show_list.append(single_row)
            print("cl: "+company_logo)

        return render(response, 'home\single_show.html', {"shows": show_list, "review_list": review_list , "review_count": review_count})

    else:
        return redirect("/user/login")



def single_series(response, series_identifier):
    if response.session.get('is_logged_in', False) == True:
        print("here")
        series_identifier = series_identifier.split("_")
        series_id = series_identifier[0]
        season_no = series_identifier[1]

        cursor = connection.cursor()
        sql = "SELECT * FROM SERIES se WHERE se.SERIES_ID = %s AND se.SEASON_NO = %s"
        cursor.execute(sql,[series_id,season_no])
        result = cursor.fetchall()
        cursor.close()

        title=""
        category=""
        start_year=""
        end_year=""
        status=""
        cover_image=""
        for r in result:
            category = r[2]
            start_year = r[3]
            end_year = r[4]
            status = r[5]
            title = r[6]
            cover_image = r[7]

        cursor = connection.cursor()
        sql = "SELECT s.SHOW_ID,s.GENRE,s.TITLE,s.LANGUAGE,s.YEAR,s.IMDB_RATING,s.USER_RATING FROM SHOW s WHERE s.SERIES_ID = %s AND s.SEASON_NO = %s"
        cursor.execute(sql, [series_id, season_no])
        result = cursor.fetchall()
        cursor.close()

        show_list = []

        tot_imdb = 0
        tot_user = 0
        cnt = 0
        language=""
        genre=""
        for r in result:
            language = r[3]
            genre = r[1]
            show_single_row = {"episode_id": r[0], "episode_title": r[2], "episode_year": r[4], "episode_number": cnt+1}
            show_list.append(show_single_row)
            tot_imdb += r[5]
            tot_user += r[6]
            cnt += 1

        imdb_rating = round(tot_imdb/cnt, 2)
        user_rating = round(tot_user / cnt, 2)


        #is_subscribed
        cursor = connection.cursor()
        sql = "SELECT * FROM SHOW s, SERIES se,SUBSCRIPTION sub,USERS u" \
              " WHERE s.SERIES_ID = se.SERIES_ID AND s.SEASON_NO = se.SEASON_NO" \
              " AND s.SHOW_ID = sub.SHOW_IDSUB" \
              " AND u.USER_ID = sub.USER_IDSUB" \
              " AND sub.SUBSCRIPTION_STATUS = 'ACTIVE'" \
              " AND u.USER_ID = %s" \
              " AND se.SERIES_ID = %s AND se.SEASON_NO = %s"

        user_id = response.session.get('user_ID')
        cursor.execute(sql, [user_id, series_id, season_no])
        result_is_sub = cursor.fetchall()
        cursor.close()

        cnt = 0
        is_subscribed = 0
        for r_sub in result_is_sub:
            cnt += 1

        if cnt > 0:
            is_subscribed = 1


        reviewC = 0
        cursor = connection.cursor()
        sql = "SELECT SHOW_ID FROM SHOW se WHERE se.SERIES_ID = %s AND se.SEASON_NO = %s"
        cursor.execute(sql, [series_id, season_no])
        result_show = cursor.fetchall()
        for r in result_show:
            show_id = r[0]
            cursor = connection.cursor()
            sql = "SELECT COUNT(*) FROM RATED se WHERE SHOW_IDRATE = %s"
            cursor.execute(sql, [show_id])
            result_rate = cursor.fetchall()
            for r in result_rate:
                reviewC = reviewC + r[0]
            cursor.close()
        cursor.close()

        #reviews
        cursor = connection.cursor()
        sql = "SELECT r.RATING_OUT_OF_FIVE, r.FEEDBACK, u.USER_FIRSTNAME, u.USER_LASTNAME, TO_CHAR( r.RATE_TIME,'DD Mon YYYY' ), u.USER_ID,s.TITLE" \
              " FROM RATED r, USERS u,SHOW s" \
              " WHERE r.USER_IDRATE = u.USER_ID" \
              " AND r.SHOW_IDRATE = s.SHOW_ID" \
              " AND s.SERIES_ID = %s" \
              " AND s.SEASON_NO = %s" \
              " ORDER BY r.RATE_TIME DESC"
        cursor.execute(sql, [series_id,season_no])
        result_review = cursor.fetchall()
        cursor.close()

        review_list = []
        review_count = 0
        for r in result_review:
            name = r[2] + " " + r[3]
            reviewer_id = r[5]
            row = {"rating_out_of_five": r[0],
                   "feedback": r[1],
                   "review_poster": name,
                   "review_time": r[4],
                   "reviewer_id": reviewer_id,
                   "review_episode": r[6]}
            review_list.append(row)
            review_count += 1

        print(review_list)



        series = {"series_id":series_id,"season_no":season_no, "title": title, "category":category,
                  "start_year": start_year, "end_year": end_year, "cover_image": cover_image, "status": status,
                  "imdb_rating": imdb_rating, "user_rating": user_rating, "language": language, "genre": genre,
                  "episode_list": show_list, "is_subscribed": is_subscribed, "no_of_reviews": reviewC, "review_list": review_list}
        print(series)

        return render(response, 'home\series_view.html', {"series": series})



    else:
        return redirect("/user/login")




def subscribe_show(response,show_identifier):
    if response.session.get('is_logged_in', False) == True:

        error_msg = ""
        show_identifier = show_identifier.split("_")
        show_type = show_identifier[0]

        if show_type == "show":
            print("show")
            show_id = show_identifier[1]
            print(show_id)

            amount = 0.99

            if response.method == "POST":
                print("here")
                if response.POST.get("pay") == "clicked":
                    print(response.POST)
                    card_number = response.POST.get("card_number")
                    exp_date = response.POST.get("exp_date")
                    username = response.POST.get("username")
                    password = response.POST.get("password")

                    if card_number == "" or exp_date == "" or username == "" or password == "":
                        error_msg = "No field can be left empty"
                    elif card_number.isnumeric() == False:
                        error_msg = "Invalid Card Number"
                    else:
                        cursor = connection.cursor()
                        sql = "SELECT * FROM CARD c" \
                              " WHERE c.CARD_ID = %s" \
                              " AND c.USER_NAME = %s" \
                              " AND c.CARD_PASS = %s"

                        cursor.execute(sql, [card_number, username, password])
                        result = cursor.fetchall()
                        cursor.close()

                        cnt = 0
                        balance = 0


                        for r in result:
                            balance = r[4]
                            cnt += 1

                        if cnt > 0:
                            val = float(balance) - amount

                            if val >= 0:
                                cursor = connection.cursor()
                                sql = "UPDATE CARD SET BALANCE = %s WHERE CARD_ID = %s"
                                cursor.execute(sql, [val, card_number])
                                cursor.close()


                                # generate bill_id
                                cursor = connection.cursor()
                                bill_id = cursor.callfunc('GIVEMAXBILLID', int)

                                print("Calling Function")
                                print(bill_id)
                                cursor.close()

                                bill_desc = "EMPTY"
                                service_period = 6
                                cursor = connection.cursor()
                                sql = "INSERT INTO BILLING_HISTORY VALUES(%s,SYSDATE,%s,%s,%s,%s)"
                                cursor.execute(sql, [bill_id, bill_desc, service_period, amount, card_number])
                                cursor.close()


                                #check subscription is there or one?
                                cursor = connection.cursor()
                                sql_isthere = "SELECT * FROM SUBSCRIPTION sub" \
                                              " WHERE sub.USER_IDSUB = %s" \
                                              " AND sub.show_IDSUB = %s"
                                user_id = response.session.get('user_ID')
                                cursor.execute(sql_isthere, [user_id, show_id])
                                result_isthere = cursor.fetchall()
                                cursor.close()

                                cnt = 0
                                for r in result_isthere:
                                    cnt += 1

                                sub_status = "ACTIVE"
                                if cnt == 0:
                                    # generate sub_id
                                    cursor = connection.cursor()
                                    sub_id = cursor.callfunc('GIVEMAXSUBID', int)

                                    print("Calling Function")
                                    print(sub_id)
                                    cursor.close()

                                    cursor = connection.cursor()
                                    sql = "INSERT INTO SUBSCRIPTION VALUES(%s,ADD_MONTHS(SYSDATE,%s),%s,%s,%s,%s)"
                                    user_id = response.session.get('user_ID')
                                    cursor.execute(sql, [sub_id, service_period, sub_status, user_id, show_id, bill_id])
                                    cursor.close()
                                    print("Successfully Subscribed")

                                else:
                                    cursor = connection.cursor()
                                    sql = "UPDATE SUBSCRIPTION sub" \
                                          " SET sub.SUBSCRIPTION_STATUS = %s, sub.SUBSCRIPTION_PERIOD = ADD_MONTHS(SYSDATE,%s)" \
                                          " WHERE sub.USER_IDSUB = %s AND sub.SHOW_IDSUB = %s"
                                    cursor.execute(sql, [sub_status, service_period, user_id, show_id])
                                    cursor.close()
                                    print("Successfully Subscription Updated")


                                curs_id = int(user_id)
                                print("curs_id"+str(curs_id))
                                print(type(curs_id))
                                cursor = connection.cursor()
                                cursor.callproc('UPDATE_FAV_GENRE', [curs_id])
                                cursor.close()

                                return redirect("/movies/"+show_id+"/")





                            else:
                                error_msg = "Insufficient Balance !!!"

                        else:
                            print("Invalid Card Information")
                            error_msg = "Invalid Card Information"


        elif show_type == "series":
            print("series")
            series_id = show_identifier[1]
            season_no = show_identifier[2]
            print(series_id)
            print(season_no)

            cursor = connection.cursor()
            sql = "SELECT DISTINCT SHOW_ID FROM SHOW s, SERIES se" \
                  " WHERE s.SERIES_ID = se.SERIES_ID" \
                  " AND s.SEASON_NO = se.SEASON_NO" \
                  " AND s.SERIES_ID = %s AND s.SEASON_NO = %s"

            cursor.execute(sql, [series_id, season_no])
            result_shows = cursor.fetchall()
            cursor.close()

            num_of_episodes = 0
            for r_show in result_shows:
                num_of_episodes += 1

            amount_epi = 0.99
            amount = amount_epi*num_of_episodes
            amount = round(amount, 2)

            if response.method == "POST":
                print(response.POST)
                card_number = response.POST.get("card_number")
                exp_date = response.POST.get("exp_date")
                username = response.POST.get("username")
                password = response.POST.get("password")

                if card_number == "" or exp_date == "" or username == "" or password == "":
                    error_msg = "No field can be left empty"
                else:
                    cursor = connection.cursor()
                    sql = "SELECT * FROM CARD c" \
                          " WHERE c.CARD_ID = %s" \
                          " AND c.USER_NAME = %s" \
                          " AND c.CARD_PASS = %s"

                    cursor.execute(sql, [card_number, username, password])
                    result = cursor.fetchall()
                    cursor.close()

                    cnt = 0
                    balance = 0
                    for r in result:
                        balance = r[4]
                        cnt += 1

                    if cnt > 0:
                        val = float(balance) - amount

                        if val >= 0:
                            cursor = connection.cursor()
                            sql = "UPDATE CARD SET BALANCE = %s WHERE CARD_ID = %s"
                            cursor.execute(sql, [val, card_number])
                            cursor.close()

                            # generate bill_id
                            cursor = connection.cursor()
                            bill_id = cursor.callfunc('GIVEMAXBILLID', int)

                            print("Calling Function")
                            print(bill_id)
                            cursor.close()

                            bill_desc = "EMPTY"
                            service_period = 6
                            cursor = connection.cursor()
                            sql = "INSERT INTO BILLING_HISTORY VALUES(%s,SYSDATE,%s,%s,%s,%s)"
                            cursor.execute(sql, [bill_id, bill_desc, service_period, amount, card_number])
                            cursor.close()


                            for r in result_shows:
                                show_id = r[0]
                                print(show_id)
                                # generate sub_id
                                cursor = connection.cursor()
                                sub_id = cursor.callfunc('GIVEMAXSUBID', int)

                                print("Calling Function")
                                print(sub_id)
                                cursor.close()

                                # check subscription is there or one?
                                cursor = connection.cursor()
                                sql_isthere = "SELECT * FROM SUBSCRIPTION sub" \
                                              " WHERE sub.USER_IDSUB = %s" \
                                              " AND sub.show_IDSUB = %s"
                                user_id = response.session.get('user_ID')
                                cursor.execute(sql_isthere, [user_id, show_id])
                                result_isthere = cursor.fetchall()
                                cursor.close()

                                cnt = 0
                                for r in result_isthere:
                                    cnt += 1

                                sub_status = "ACTIVE"
                                if cnt == 0:
                                    # generate sub_id
                                    cursor = connection.cursor()
                                    sub_id = cursor.callfunc('GIVEMAXSUBID', int)

                                    print("Calling Function")
                                    print(sub_id)
                                    cursor.close()

                                    cursor = connection.cursor()
                                    sql = "INSERT INTO SUBSCRIPTION VALUES(%s,ADD_MONTHS(SYSDATE,%s),%s,%s,%s,%s)"
                                    user_id = response.session.get('user_ID')
                                    cursor.execute(sql, [sub_id, service_period, sub_status, user_id, show_id, bill_id])
                                    cursor.close()
                                    print("Successfully Subscribed")

                                else:
                                    cursor = connection.cursor()
                                    sql = "UPDATE SUBSCRIPTION sub" \
                                          " SET sub.SUBSCRIPTION_STATUS = %s, sub.SUBSCRIPTION_PERIOD = ADD_MONTHS(SYSDATE,%s)" \
                                          " WHERE sub.USER_IDSUB = %s AND sub.SHOW_IDSUB = %s"
                                    cursor.execute(sql, [sub_status, service_period, user_id, show_id])
                                    cursor.close()
                                    print("Successfully Subscription Updated")

                                curs_id = int(user_id)
                                print("curs_id" + str(curs_id))
                                print(type(curs_id))
                                cursor = connection.cursor()
                                cursor.callproc('UPDATE_FAV_GENRE', [curs_id])
                                cursor.close()


                            return redirect("/series/" + series_id + "_"+season_no+"/")


                        else:
                            error_msg = "Insufficient Balance !!!"

                    else:
                        print("Invalid Card Information")
                        error_msg = "Invalid Card Information"

        show = {"amount": amount}

        return render(response,'home\subscribe.html', {"show": show, "error_msg": error_msg})

    else:
        return redirect("/user/login")



def subscribed_show(response):
    error_msg=""
    no_of_results=""
    if response.session.get('is_logged_in', False) == True:
        user_id = response.session.get('user_ID', -1)
        if response.method == "POST":
            print("here")
            if response.POST.get("search_button") == "clicked":
                print(response.POST)
                search_item = response.POST.get('search_field')
                search_item = search_item.replace(" ", "")
                search_pattern = "%" + search_item.lower() + "%"

                print(search_pattern)

                # search_type = response.POST.get('type')
                search_genre = response.POST.get('genre')
                search_lang = response.POST.get('language')
                search_from = response.POST.get('from_year')
                search_to = response.POST.get('to_year')

                # print(search_type)
                print(search_genre)
                print(search_lang)
                print(search_from)
                print(search_to)

                cursor = connection.cursor()
                sql = "SELECT DISTINCT(s.SHOW_ID) FROM SHOW s,ACTOR a,ACT ac, SUBSCRIPTION sub" \
                      " WHERE s.SHOW_ID = ac.SHOW_IDACT AND ac.ACTOR_IDACT = a.PERSON_ID AND s.SHOW_ID = sub.SHOW_IDSUB AND" \
                      " sub.SUBSCRIPTION_STATUS = 'ACTIVE' AND" \
                      " sub.USER_IDSUB = %s AND" \
                      " regexp_replace(LOWER(a.ACTOR_FIRST_NAME || ' ' || a.ACTOR_LAST_NAME), ' ','') like (%s)" \
                      " UNION" \
                      " (SELECT DISTINCT(s.SHOW_ID) FROM SHOW s, SERIES se, SUBSCRIPTION sub" \
                      " WHERE s.SERIES_ID = se.SERIES_ID" \
                      " AND s.SEASON_NO = se.SEASON_NO" \
                      " AND s.SHOW_ID = sub.SHOW_IDSUB" \
                      " AND sub.USER_IDSUB = %s" \
                      " AND sub.SUBSCRIPTION_STATUS = 'ACTIVE'" \
                      " AND regexp_replace(LOWER(se.TITLE), ' ','') like (%s)" \
                      " )" \
                      " UNION" \
                      " (" \
                      " SELECT DISTINCT(s.SHOW_ID)" \
                      " FROM SHOW s, DIRECTOR d, SUBSCRIPTION sub" \
                      " WHERE s.DIRECTOR_ID = d.PERSON_ID AND s.SHOW_ID = sub.SHOW_IDSUB AND" \
                      " sub.USER_IDSUB = %s AND" \
                      " sub.SUBSCRIPTION_STATUS = 'ACTIVE' AND" \
                      " regexp_replace(LOWER (d.DIRECTOR_FIRST_NAME || ' ' || d.DIRECTOR_LAST_NAME), ' ','') like (%s)" \
                      " )" \
                      " UNION" \
                      " (" \
                      " SELECT DISTINCT(s.SHOW_ID) FROM SHOW s, SUBSCRIPTION sub" \
                      " WHERE s.SHOW_ID = sub.SHOW_IDSUB AND sub.USER_IDSUB = %s AND sub.SUBSCRIPTION_STATUS = 'ACTIVE' AND" \
                      " (regexp_replace(LOWER(s.TITLE), ' ','') like (%s)" \
                      " OR regexp_replace(LOWER(s.GENRE), ' ','') like (%s))" \
                      " )"

                cursor.execute(sql, [user_id, search_pattern, user_id, search_pattern, user_id, search_pattern, user_id, search_pattern, search_pattern])
                result = cursor.fetchall();
                cursor.close()

                print(type(result))

                search_genre = response.POST.get('genre')
                search_genre = search_genre.replace(" ", "")
                search_genre = "%" + search_genre.lower() + "%"
                print(search_genre)

                search_lang = response.POST.get('language')
                search_lang = search_lang.replace(" ", "")
                search_lang = "%" + search_lang.lower() + "%"

                print(search_lang)

                search_from = response.POST.get('from_year')

                print(search_from)

                search_to = response.POST.get('to_year')

                print(search_to)

                result_final = []

                result_genre = []
                if search_genre != "":
                    cursor = connection.cursor()
                    sql_genre = "SELECT DISTINCT(s.SHOW_ID) FROM SHOW s, SUBSCRIPTION sub" \
                                " where s.SHOW_ID = sub.SHOW_IDSUB AND" \
                                " sub.SUBSCRIPTION_STATUS = 'ACTIVE' AND" \
                                " regexp_replace(LOWER(s.GENRE), ' ','') Like (%s) AND" \
                                " sub.USER_IDSUB = %s"
                    cursor.execute(sql_genre, [search_genre,user_id])
                    result_genre = cursor.fetchall()
                    cursor.close()
                else:
                    result_genre = result

                result_lang = []
                if search_lang != "":
                    cursor = connection.cursor()
                    sql_lang = "SELECT DISTINCT(s.SHOW_ID) FROM SHOW s, SUBSCRIPTION sub" \
                               " WHERE s.SHOW_ID = sub.SHOW_IDSUB AND" \
                               " sub.SUBSCRIPTION_STATUS = 'ACTIVE' AND" \
                               " regexp_replace(LOWER(s.LANGUAGE), ' ','') Like (%s) AND" \
                               " sub.USER_IDSUB = %s"
                    cursor.execute(sql_lang, [search_lang,user_id])
                    result_lang = cursor.fetchall()
                    cursor.close()
                else:
                    result_lang = result

                result_from = []
                if search_from != "":
                    cursor = connection.cursor()
                    sql_from = "SELECT DISTINCT(s.SHOW_ID) FROM SHOW s, SUBSCRIPTION sub" \
                               " where s.SHOW_ID = sub.SHOW_IDSUB AND" \
                               " sub.SUBSCRIPTION_STATUS = 'ACTIVE' AND" \
                               " s.YEAR >= %s AND " \
                               " sub.USER_IDSUB = %s"
                    cursor.execute(sql_from, [search_from,user_id])
                    result_from = cursor.fetchall()
                    cursor.close()
                else:
                    result_from = result

                result_to = []
                if search_to != "":
                    cursor = connection.cursor()
                    sql_to = "SELECT DISTINCT(s.SHOW_ID) FROM SHOW s, SUBSCRIPTION sub" \
                             " where s.SHOW_ID = sub.SHOW_IDSUB" \
                             " AND sub.SUBSCRIPTION_STATUS = 'ACTIVE'" \
                             " AND s.YEAR <= %s" \
                             " AND sub.USER_IDSUB = %s"
                    cursor.execute(sql_to, [search_to,user_id])
                    result_to = cursor.fetchall()
                    cursor.close()
                else:
                    result_to = result

                result_temp = set(result_genre).intersection(set(result_from).intersection(result_to))
                result_temp_new = set(result_temp).intersection(set(result_lang))
                result_final = set(result).intersection(result_temp_new)

                error_msg = "No Result Found!"
                show_list = []

                cnt = 0
                for r in result_final:
                    cnt = cnt + 1
                    print(type(r))
                    show_id = r[0]
                    print(show_id)
                    cursor = connection.cursor()
                    sql = "SELECT * FROM SHOW WHERE SHOW_ID = %s"
                    cursor.execute(sql, [show_id])
                    show_res = cursor.fetchall()
                    cursor.close()
                    print("here")

                    for r_temp in show_res:
                        show_title = r_temp[2]
                        show_genre = r_temp[1]
                        show_des = r_temp[3]
                        show_age = r_temp[4]
                        show_lang = r_temp[8]
                        show_image = r_temp[13]
                        show_imdb = r_temp[5]
                        single_row = {
                                      "show_id": show_id,
                                      "show_imdb": show_imdb,
                                      "show_title": show_title,
                                      "show_genre": show_genre,
                                      "show_des": show_des,
                                      "show_age": show_age,
                                      "show_lang": show_lang,
                                      "show_image": show_image}
                        show_list.append(single_row)
                        error_msg = ""
                no_of_results = str(cnt)
        else:
            cursor = connection.cursor()
            sql_subs = "SELECT * FROM SUBSCRIPTION sub WHERE sub.USER_IDSUB = %s AND sub.SUBSCRIPTION_STATUS = 'ACTIVE'"
            cursor.execute(sql_subs, [user_id])
            result = cursor.fetchall()
            #print(result)
            cursor.close()
            show_list=[]
            cnt = 0
            cnt_sub = 0
            no_of_result=""
            for r in result:
                cnt_sub = cnt_sub+1
                showID = r[4]
                cursor = connection.cursor()
                sql_sh = "SELECT * FROM SHOW WHERE SHOW_ID = %s"
                cursor.execute(sql_sh, [showID])
                result_main = cursor.fetchall()
                #print(result_main)
                for r_main in result_main:
                    cnt = cnt+1
                    show_id = r_main[0]
                    show_title = r_main[2]
                    show_genre = r_main[1]
                    show_imdb = r_main[5]
                    show_image = r_main[13]
                    single_row = {"show_id": show_id, "show_title": show_title, "show_genre": show_genre, "show_imdb": show_imdb,
                                  "show_image": show_image}
                    show_list.append(single_row)
                no_of_results = str(cnt)
                cursor.close()
                print("Numbereeeererer")
                print(no_of_results)
            if cnt_sub == 0:
                error_msg = "Sorry! You haven't subscribed for a single show!"
        return render(response,'home\homepage.html',{'no_of_results': no_of_results, 'shows': show_list,"error_msg":error_msg})
    else:
        return redirect("/user/login")


def unsubscribe_show(response, show_identifier):
    if response.session.get('is_logged_in', False) == True:

        user_id = response.session.get('user_ID')
        show_identifier = show_identifier.split("_")
        show_type = show_identifier[0]

        if show_type == "show":
            print("show")
            show_id = show_identifier[1]
            print(show_id)

            cursor = connection.cursor()
            sql = "UPDATE SUBSCRIPTION sub" \
                  " SET sub.SUBSCRIPTION_STATUS = 'INACTIVE'" \
                  " WHERE sub.USER_IDSUB = %s" \
                  " AND sub.SHOW_IDSUB = %s"
            cursor.execute(sql, [user_id, show_id])
            cursor.close()

            return redirect("/movies/"+show_id+"/")


        elif show_type == "series":
            print("series")
            series_id = show_identifier[1]
            season_no = show_identifier[2]
            print(series_id)
            print(season_no)

            cursor = connection.cursor()
            sql = "SELECT DISTINCT SHOW_ID FROM SHOW s, SERIES se" \
                  " WHERE s.SERIES_ID = se.SERIES_ID" \
                  " AND s.SEASON_NO = se.SEASON_NO" \
                  " AND s.SERIES_ID = %s AND s.SEASON_NO = %s"

            cursor.execute(sql, [series_id, season_no])
            result_shows = cursor.fetchall()
            cursor.close()

            for r_show in result_shows:
                cursor = connection.cursor()
                sql = "UPDATE SUBSCRIPTION sub" \
                      " SET sub.SUBSCRIPTION_STATUS = 'INACTIVE'" \
                      " WHERE sub.USER_IDSUB = %s" \
                      " AND sub.SHOW_IDSUB = %s"
                cursor.execute(sql, [user_id, r_show[0]])
                cursor.close()

            return redirect("/series/"+series_id+"_"+season_no+"/")

    else:
        return redirect("/user/login")




def pushintoDBsettings(l,user_id,change):
    #encrypt password
    if change == 1:
        encrypted_password = pbkdf2_sha256.encrypt(l[4], rounds=12000, salt_size=32)
    else:
        encrypted_password = l[4]

    cursor = connection.cursor()
    sql = "UPDATE USERS SET USER_FIRSTNAME = %s, USER_LASTNAME = %s, PASSWORD = %s, PHONE_NO = %s, PHOTO = %s WHERE USER_ID = %s"
    cursor.execute(sql, [l[0], l[1], encrypted_password, l[2], l[5], user_id])
    connection.commit()
    cursor.close()

def settings(response):
    error_msg = ""
    user_id = -1
    if response.session.get('is_logged_in', False) == True:
        user_id = response.session.get('user_ID', -1)
        if response.method == "POST":
            if response.POST.get("update"):
                first_name = response.POST.get("fname")
                last_name = response.POST.get("lname")
                phone = response.POST.get("phone")
                password = response.POST.get("password")
                confpass = response.POST.get("confpass")

                print(response.FILES)
                file_ok = True
                pp = False
                try:
                    if response.FILES["profile_pic"]:
                        myfile = response.FILES["profile_pic"]

                        print(myfile.name)
                        f_name = myfile.name
                        f_name = f_name.split(".")
                        ext = ""
                        for f in f_name:
                            ext = f
                        print(ext)

                        file_ok = False
                        if ext.lower() == "jpg" or ext.lower() == "png":
                            file_ok = True

                        if file_ok:
                            fs = FileSystemStorage()
                            filename = fs.save(myfile.name, myfile)
                            uploaded_file_url = "../.."
                            uploaded_file_url += fs.url(filename)
                            print(uploaded_file_url)
                            pp = True

                except Exception:
                    print("Exception occured not receiving any file")


                cursor = connection.cursor()
                sql_show = "SELECT * FROM USERS WHERE USER_ID = %s"
                cursor.execute(sql_show, [user_id])
                result = cursor.fetchall()
                for r in result:
                    f_name_db = r[2]
                    l_name_db = r[3]
                    pass_db = r[4]
                    phone_db = r[6]
                    photo_db = r[11]
                cursor.close()

                l = []
                if first_name == "":
                    l.append(f_name_db)
                else:
                    l.append(first_name)

                if last_name == "":
                    l.append(l_name_db)
                else:
                    l.append(last_name)

                if phone == "":
                    l.append(phone_db)
                else:
                    l.append(phone)

                if password == "":
                    change = 0
                    l.append(pass_db)
                else:
                    change = 1
                    l.append(password)
                if pp:
                    l.append(uploaded_file_url)
                else:
                    l.append(photo_db)
                print(l)

                if len(password) < 8 and password != "":
                    error_msg = "Password should be at least 8 characters"
                elif password != "" and password != confpass:
                    error_msg = "Passwords do not match"
                elif file_ok == False:
                    error_msg = "File has to be an image"
                else:
                    pushintoDBsettings(l, user_id, change)
                    return redirect("/home/")

        return render(response, "home/settings.html", {"error_msg": error_msg})

    else:
        return redirect("/user/login/")


def profile_show(response, user_id):
    if response.session.get('is_logged_in', False) == True:

        print(user_id)
        my_profile = 0
        if user_id == "my_profile":
            id = response.session.get('user_ID')
            my_profile = 1
        else:
            id = user_id
        cursor = connection.cursor()
        sql = "SELECT USER_FIRSTNAME,USER_LASTNAME,TO_CHAR(JOIN_DATE,'MON dd, YYYY'),TO_CHAR(DATE_OF_BIRTH,'MON dd, YYYY')," \
              " PHONE_NO,FAVOURITE_GENRE,GENDER,EMAIL,PHOTO" \
              " FROM USERS WHERE USER_ID = %s"
        cursor.execute(sql, [id])
        result = cursor.fetchall()
        cursor.close()
        print(result)
        for r in result:
            userFname = r[0]
            userLname = r[1]
            Jdate = r[2]
            Bday = r[3]
            phone = r[4]
            Favg = r[5]
            gender = r[6]
            mail = r[7]
            photo = r[8]

        cursor = connection.cursor()
        sql = "SELECT COUNT(sub.SUBSCRIPTION_ID) FROM SUBSCRIPTION sub where sub.USER_IDSUB = %s"
        cursor.execute(sql, [id])
        result = cursor.fetchall()
        cursor.close()

        for r in result:
            no_of_subs = r[0]

        cursor = connection.cursor()
        sql = "SELECT COUNT(d.DOWNLOAD_ID) FROM DOWNLOAD_HISTORY d, SUBSCRIPTION sub, USERS u" \
              " WHERE d.SUB_ID = sub.SUBSCRIPTION_ID" \
              " AND sub.USER_IDSUB = %s"
        cursor.execute(sql, [id])
        result = cursor.fetchall()
        cursor.close()

        for r in result:
            no_of_downloads = r[0]

        user_info = {"userFname":userFname, "userLname":userLname, "Jdate":Jdate,
                     "Bday":Bday,"phone":phone,"Favg":Favg,"gender":gender,
                     "mail":mail,"profile_pic": photo,"no_of_subs": no_of_subs, "no_of_downloads": no_of_downloads}



        if my_profile == 1:
            return render(response, 'home\profile.html', {"user_info": user_info, "my_profile": my_profile})
        else:
            return render(response, 'home\profile_review.html', {"user_info": user_info, "my_profile": my_profile})


def downloads(response):
    if response.session.get('is_logged_in', False) == True:
        user_id = response.session.get('user_ID', -1)
        cursor = connection.cursor()
        sql = "SELECT TO_CHAR(DOWNLOAD_TIME,'MON dd, YYYY hh:mi:ss') FROM DOWNLOAD_HISTORY ORDER BY DOWNLOAD_TIME DESC"
        cursor.execute(sql)
        result_date = cursor.fetchall()
        cursor.close()
        #print(result_date)

        msg = ""
        cnt = 0
        show_list = []
        cursor = connection.cursor()
        sql = "SELECT sh.SHOW_ID, sh.TITLE, sh.GENRE, sh.USER_RATING, TO_CHAR(dh.DOWNLOAD_TIME,'MON dd, YYYY hh:mi:ss') FROM SHOW sh, SUBSCRIPTION sub, DOWNLOAD_HISTORY dh WHERE dh.SUB_ID = sub.SUBSCRIPTION_ID AND sub.SHOW_IDSUB = sh.SHOW_ID AND sub.USER_IDSUB = %s ORDER BY DOWNLOAD_TIME DESC"
        cursor.execute(sql,[user_id])
        result_show = cursor.fetchall()
        cursor.close()
        #print(result_show)
        for r in result_show:
            cnt = cnt + 1
            show_id = r[0]
            show_title = r[1]
            show_genre = r[2]
            show_urating = r[3]
            dtime = r[4]
            single_row = {"show_id":show_id,"show_title":show_title,"show_genre":show_genre,"show_urating":show_urating,"dtime":dtime}
            show_list.append(single_row)
        print(show_list)
        print(cnt)
        if cnt == 0:
            msg = "Sorry! You haven't downloaded a single show!"
            cnt = str(cnt)
        return render(response, 'home\downloads.html',{"show_list":show_list,"count":cnt,"msg":msg})
    else:
        return redirect("/user/login/")
