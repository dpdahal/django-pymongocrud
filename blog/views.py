from django.shortcuts import render,redirect
from django.http import HttpResponse
from pathlib import Path
from dmproject.settings import collection
import os
from bson import ObjectId  
import random

def index(request):
    users = list(collection.find())
    for user in users:
        user["id"] = str(user["_id"])
    return render(request, 'index.html', {'users': users})



def add(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")

        upload_dir = Path(__file__).resolve().parent.parent / "uploads"
        os.makedirs(upload_dir, exist_ok=True)

        image_path = ""
        if request.FILES.get("image"):
            image = request.FILES["image"]
            image_path = f"uploads/{image.name}"  # Store relative path
            full_image_path = upload_dir / image.name  # Full path to save
            # check if file already exists if yes then generate a new name
            if os.path.exists(full_image_path):
                image_name = image.name.split(".")
                random_number = random.randint(1, 1000)
                image_name[0] = image_name[0] + str(random_number)
                image.name = ".".join(image_name)
                image_path = f"uploads/{image.name}"
                full_image_path = upload_dir / image.name

            with open(full_image_path, "wb") as f:
                for chunk in image.chunks():
                    f.write(chunk)


        # Insert data into MongoDB
        collection.insert_one({
            "name": name,
            "email": email,
            "phone": phone,
            "image": image_path  # Store only the file path
        })   

        return redirect('index')
    else:
        return render(request, "add.html")
    

def delete_file(id):
    user = collection.find_one({"_id": ObjectId(id)})
    if "image" in user and user["image"]:
        upload_dir = Path(__file__).resolve().parent.parent / "uploads"
        full_image_path = upload_dir / user["image"].split("/")[-1]
        if os.path.exists(full_image_path):
            os.remove(full_image_path)
            return True
    else:
        return True



def update(request, id):
    if request.method=="POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        upload_dir = Path(__file__).resolve().parent.parent / "uploads"
        os.makedirs(upload_dir, exist_ok=True)

        image_path = ""
        if request.FILES:
            delete_file(id)
            image = request.FILES["image"]
            image_path = f"uploads/{image.name}"
            full_image_path = upload_dir / image.name
            with open(full_image_path, "wb") as f:
                for chunk in image.chunks():
                    f.write(chunk)
        else:
            user = collection.find_one({"_id": ObjectId(id)})
            image_path = user["image"]
        collection.update_one({"_id": ObjectId(id)}, {"$set": {"name": name, "email": email, "phone": phone, "image": image_path}})

        return redirect('index')

    else:
        user = collection.find_one({"_id": ObjectId(id)}) 
        user["id"] = str(user["_id"]) 
        if "image" in user and user["image"]:
                user["image_url"] = f"/{user['image']}"
        return render(request, "update.html", {"user": user})
    


def delete(request, id):
    delete_file(id)
    collection.delete_one({"_id": ObjectId(id)})
    return redirect('index')