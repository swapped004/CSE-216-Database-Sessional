from django.shortcuts import redirect
from django.db import connection
#streaming part
import os
import re
import mimetypes
from wsgiref.util import FileWrapper
from django.http.response import StreamingHttpResponse,HttpResponse,Http404,FileResponse
from django.utils.encoding import smart_str


range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)


class RangeFileWrapper(object):
    def __init__(self, filelike, blksize=8192, offset=0, length=None):
        self.filelike = filelike
        self.filelike.seek(offset, os.SEEK_SET)
        self.remaining = length
        self.blksize = blksize

    def close(self):
        if hasattr(self.filelike, 'close'):
            self.filelike.close()

    def __iter__(self):
        return self

    def __next__(self):
        if self.remaining is None:
            # If remaining is None, we're reading the entire file.
            data = self.filelike.read(self.blksize)
            if data:
                return data
            raise StopIteration()
        else:
            if self.remaining <= 0:
                raise StopIteration()
            data = self.filelike.read(min(self.remaining, self.blksize))
            if not data:
                raise StopIteration()
            self.remaining -= len(data)
            return data


def stream_video(request, file_name):
    if request.session.get('is_logged_in'):
        print("here")
        range_header = request.META.get('HTTP_RANGE', '').strip()
        range_match = range_re.match(range_header)
        path = "E:\\"+file_name

        if os.path.exists(path):
            size = os.path.getsize(path)
            print(path)
            print(size)
            content_type, encoding = mimetypes.guess_type(path)
            content_type = content_type or 'application/octet-stream'
            print(content_type)
            if range_match:
                print("range_match")
                first_byte, last_byte = range_match.groups()
                first_byte = int(first_byte) if first_byte else 0
                last_byte = int(last_byte) if last_byte else size - 1
                if last_byte >= size:
                    last_byte = size - 1
                length = last_byte - first_byte + 1
                resp = StreamingHttpResponse(RangeFileWrapper(open(path, 'rb'), offset=first_byte, length=length), status=206, content_type=content_type)
                resp['Content-Length'] = str(length)
                resp['Content-Range'] = 'bytes %s-%s/%s' % (first_byte, last_byte, size)
            else:
                print("not range_match")
                resp = StreamingHttpResponse(FileWrapper(open(path, 'rb')), content_type=content_type)
                resp['Content-Length'] = str(size)
            resp['Accept-Ranges'] = 'bytes'
            print("at the end")
            return resp
        else:
            raise Http404
    else:
        return redirect("/user/login")


def pushintoDhistory(show_id,user_id):
    print(show_id)
    print(user_id)
    #generate download_id
    cursor = connection.cursor()
    sql_ID = "SELECT NVL(MAX(DOWNLOAD_ID),0) FROM DOWNLOAD_HISTORY"
    cursor.execute(sql_ID)
    result = cursor.fetchall()
    for i in result:
        down_ID = i[0]
    cursor.close()
    down_ID = down_ID+1
    print(down_ID)

    #get subscription_id
    cursor = connection.cursor()
    sql = "SELECT SUBSCRIPTION_ID FROM SUBSCRIPTION WHERE USER_IDSUB = %s AND  SHOW_IDSUB = %s"
    cursor.execute(sql,[user_id,show_id])
    result = cursor.fetchall()
    for i in result:
        sub_ID = i[0]
    cursor.close()
    print(sub_ID)

    isFav = "no"
    #insert into download_history
    cursor = connection.cursor()
    sql = "INSERT INTO DOWNLOAD_HISTORY VALUES(%s, SYSDATE, %s, %s)"
    cursor.execute(sql, [down_ID, isFav,sub_ID])
    connection.commit()
    cursor.close()





def download_video(request,file_name):
    if request.session.get('is_logged_in'):
        user_id = request.session.get('user_ID')
        file_name = file_name.split("-")
        print(file_name[0])
        print(file_name[1])
        show_id = file_name[1]
        path = "E:\\" + file_name[0]
        if os.path.exists(path):
            file_path = path
            chunk_size = 1024

            #PUSH_into_db
            pushintoDhistory(show_id, user_id)

            response = StreamingHttpResponse(
                FileWrapper(open(file_path, 'rb'), chunk_size),
                content_type="video/mp4"
            )
            response['Content-Length'] = os.path.getsize(file_path)
            response['Content-Disposition'] = "attachment; filename=%s" % file_name[0]
            return response
        else:
            raise Http404
    else:
        return redirect("/user/login")