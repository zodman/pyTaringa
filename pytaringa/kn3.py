import requests
import time
import json
import os

class Kn3(object):
    @staticmethod
    def import_to_kn3(url, logo=False):
        request = requests.get(url, stream=True)
        if request.status_code == 200:
            temp_name = str(time.time()) +".jpg"
            with open(temp_name, 'wb') as f:
                for chunk in request.iter_content(1024):
                    f.write(chunk)
            if logo != False:
                temp_name = Kn3.put_logo(temp_name, logo)
            upload = Kn3.upload(temp_name)
            os.remove(temp_name)
            if not upload:
                debug("Could not upload image")
                return "Could not upload image"
            else:
                return upload
    @staticmethod
    def put_logo(temp_name, logo):
        from PIL import Image
        original_image = Image.open(temp_name)
	original_image = original_image.convert("RGBA")
        logo_image = Image.open(logo)
        original_image.paste(logo_image, (0,0), logo_image.convert("RGBA"))
        original_image.save(temp_name)
        return temp_name

    @staticmethod
    def upload(filename):
        kn3Url = "http://kn3.net/upload.php"
        files = {'files[]': open(filename, 'rb')}
        r = requests.post(kn3Url,files=files)
        if r.status_code == 200:
            response = json.loads(r.text)
            return response["direct"]
        else:
            return None
