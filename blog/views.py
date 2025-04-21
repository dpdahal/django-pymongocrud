from django.shortcuts import render,redirect
from django.http import HttpResponse
from pathlib import Path
from dmproject.settings import collection, products,orders
import os
from bson import ObjectId  
import random
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages


import requests
import json



def login_check(func):
    def wrapper(request, *args, **kwargs):
        if request.session.get("is_login"):
            return func(request, *args, **kwargs)
        else:
            return redirect('login')
    return wrapper


def index(request):
    ppData = list(products.find())
    for pp in ppData:
        pp["id"] = str(pp["_id"])
    return render(request, 'index.html', {'productData': ppData})



def users(request):
    users = list(collection.find())
    for user in users:
        user["id"] = str(user["_id"])
    return render(request, 'users.html', {'users': users})



def add(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password = make_password(password)
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
            "password": password,
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



def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = collection.find_one({"email": email})
        if user and check_password(password, user["password"]):
            request.session["user"] = {
                "username": user["name"],
                "id": str(user["_id"]),
                "email": user["email"],
            }
            request.session["is_login"] = True
            return redirect('dashboard')
        else:
            return HttpResponse("Invalid credentials")
        
    else:
        return render(request, "login.html")
    


@login_check
def dashboard(request):
    return render(request, "dashboard.html")
   



def logout(request):
    request.session.flush()  # Clear session
    return redirect('login')



# add product 
def add_product(request):
    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
       
        products.insert_one({
            "name": name,
            "price": price
        })
        return redirect('index')
    else:
        return render(request, "add_product.html")



@login_check
def order(request, id):
    if request.method == "POST":
        login_user = request.session.get("user")
        name = request.POST.get("name")
        email = request.POST.get("email")
        quantity = request.POST.get("quantity")
        price_cal = products.find_one({"_id": ObjectId(id)})
        total_price = int(price_cal["price"]) * int(quantity)
        orders.insert_one({
            "name": name,
            "email": email,
            "quantity": quantity,
            "total_price": total_price,
            "product_id": id,
            "user_id": login_user["id"],
            "payment_status": "Pending",
        })
        last_order = orders.find_one(sort=[("_id", -1)])
        order_id = last_order["_id"]

        url = "https://dev.khalti.com/api/v2/epayment/initiate/"
        payload = json.dumps({
        "return_url": "http://127.0.0.1:8000/payment_success",
        "website_url": "https://example.com/",
        "amount": "1000",
        "purchase_order_id": str(order_id),
        "purchase_order_name": "test",
        "customer_info": {
        "name": "Ram Bahadur",
        "email": "test@khalti.com",
        "phone": "9800000001"
        }
        })
        headers = {
            'Authorization': 'key 116d62c8e03342c2b32192e4d9d72275',
            'Content-Type': 'application/json',
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        url = response.json()["payment_url"]
        return redirect(url)
    else:
        product = products.find_one({"_id": ObjectId(id)})
        product["id"] = str(product["_id"])
        return render(request, "order.html", {"product": product})
   


@login_check
def order_list(request):
    login_user = request.session.get("user")
    orders_data = list(orders.find({"user_id": login_user["id"]}))
    for order in orders_data:
        order["id"] = str(order["_id"])
        order["product"] = products.find_one({"_id": ObjectId(order["product_id"])})
        order["product"]["id"] = str(order["product"]["_id"])

    return render(request, "order_list.html", {"orders": orders_data})

    


@login_check
def payment_success(request):
    order_id = request.GET.get("purchase_order_id")
    orders.update_one({"_id": ObjectId(order_id)}, {"$set": {"payment_status": "Success"}})
    messages.success(request, "Payment successful!")
    return redirect('order_list')