from django.shortcuts import render
import datetime

# Create your views here.


def home_view(request, *args, **kwargs):
    print(args, kwargs)
    # print(request.user)
    print(datetime.datetime.now())

    return render(request, 'home.html', {})


def about_view(request, *args, **kwargs):
    return render(request, 'about.html', {})


def contact_view(request, *args, **kwargs):
    return render(request, 'contact.html', {})

# def image_upload(request):
#     from django.core.files.storage import FileSystemStorage
#     if request.method == "POST" and request.FILES["image_file"]:
#         image_file = request.FILES["image_file"]
#         fs = FileSystemStorage()
#         filename = fs.save(image_file.name, image_file)
#         image_url = fs.url(filename)
#         print(image_url)
#         return render(request, "upload.html", {
#             "image_url": image_url
#         })
#     return render(request, "upload.html")
